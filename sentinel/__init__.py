"""Sentinel-26145: passive threat detection for one-way (tap / data-diode) IP traffic.

The package never transmits toward the monitored network. Ingest reads packet
captures, packet streams on stdin, or Zeek logs; detection works on metadata
only; output is alert records, cases and verifiable evidence bundles.
"""

__version__ = "1.0.0"
