#!/bin/bash
INTERFACE=${1:-eth1}
echo "[*] Configuring physical monitoring interface: $INTERFACE"
ip link set dev $INTERFACE up
ethtool -K $INTERFACE rx off tx off sg off tso off ufo off gso off gro off lro off rxvlan off txvlan off rxhash off
ip link set dev $INTERFACE promisc on
echo "[*] Interface $INTERFACE is ready for passive sniffing. Run tcpdump -ni $INTERFACE -c 100 to verify."

