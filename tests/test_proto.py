import hashlib
import io

import pytest

from sentinel.ingest.pcapio import PcapReader, PcapWriter, sha256_file
from sentinel.lab import packets as P
from sentinel.proto import tls
from sentinel.proto.community_id import community_id


def _parse(record: bytes) -> tls.ClientHello:
    return tls.parse_client_hello(tls.extract_handshake(record, tls.CLIENT_HELLO))


def test_ja4_matches_foxio_spec_vectors():
    assert tls.ja4_b(P.CHROME_LIKE.ciphers) == "8daaf6152771"
    assert tls.ja4_c(P.CHROME_LIKE.extensions, P.CHROME_LIKE.sigalgs) == "e5627efa2ab1"


def test_ja4_full_string_ignores_grease():
    ch = _parse(P.client_hello(P.CHROME_LIKE, "example.com"))
    assert tls.ja4(ch) == "t13d1516h2_8daaf6152771_e5627efa2ab1"
    assert ch.sni == "example.com"
    assert ch.alpn[0] == b"h2"


def test_ja4_without_sni_or_alpn():
    ch = _parse(P.client_hello(P.GO_LIKE, None))
    assert tls.ja4(ch).startswith("t13i190800_")


def test_alpn_non_alphanumeric_uses_hex_first_last():
    assert tls._alpn_chars([b"\xab\xcd"]) == "ad"
    assert tls._alpn_chars([b"h"]) == "hh"
    assert tls._alpn_chars([]) == "00"


def test_ja3_string_excludes_grease():
    ch = _parse(P.client_hello(P.CHROME_LIKE, "example.com"))
    text = tls.ja3_string(ch)
    assert "2570" not in text.split(",")[1].split("-")  # 0x0a0a
    assert text.startswith("771,4865-4866-4867,") is False  # full cipher list present
    assert text.split(",")[0] == "771"
    assert tls.ja3(ch) == hashlib.md5(text.encode()).hexdigest()


def test_server_hello_negotiated_version():
    body = tls.extract_handshake(P.server_hello(0x1302), tls.SERVER_HELLO)
    sh = tls.parse_server_hello(body)
    assert sh.selected_version == 0x0304 and sh.cipher == 0x1302
    assert len(tls.ja3s(sh)) == 32


def test_handshake_split_needs_more_data():
    record = P.client_hello(P.FIREFOX_LIKE, "a.example")
    with pytest.raises(tls.NeedMoreData):
        tls.extract_handshake(record[:100], tls.CLIENT_HELLO)
    assert tls.extract_handshake(b"GET / HTTP/1.1\r\n", tls.CLIENT_HELLO) is None


def test_community_id_reference_vector_and_symmetry():
    expected = "1:LQU9qZlK+B5F3KDmev6m5PMibrg="
    assert community_id(6, "128.232.110.120", "66.35.250.204", 34855, 80) == expected
    assert community_id(6, "66.35.250.204", "128.232.110.120", 80, 34855) == expected


def test_pcap_roundtrip_offsets_and_hash(tmp_path):
    path = tmp_path / "t.pcap"
    frames = [P.udp_packet("10.0.0.1", "10.0.0.2", 5000 + i, 53, b"x" * (10 + i)) for i in range(3)]
    with open(path, "wb") as f:
        writer = PcapWriter(f)
        for i, frame in enumerate(frames):
            writer.write(1000.25 + i, frame)
    with PcapReader(str(path)) as reader:
        got = list(reader)
        digest = reader.sha256
    assert [p.data for p in got] == frames
    assert got[0].offset == 24 and got[1].offset == 24 + 16 + len(frames[0])
    assert abs(got[2].ts - 1002.25) < 1e-6
    assert digest == sha256_file(str(path))


def test_reader_rejects_non_capture(tmp_path):
    path = tmp_path / "bad.pcap"
    path.write_bytes(b"not a capture at all")
    with pytest.raises(ValueError):
        list(PcapReader(str(path)))
