#!/bin/bash
export MONITOR_INTERFACE="eth1"
echo "1. Validating Physical Interface Packets..."
tcpdump -ni $MONITOR_INTERFACE -c 100
echo "2. Validating Zeek Live Sniffing..."
docker exec sih26145-zeek-sensor tail -f /var/log/zeek/conn.log
echo "3. Validating Kafka Transport..."
docker exec sih26145-redpanda rpk topic consume network-observations -n 5
echo "4. Validating NIC Drops..."
ethtool -S $MONITOR_INTERFACE | grep -E "drop|error"

