#!/bin/sh
apk update
apk add nmap

while true; do
  echo "Generating Port Scan against Zeek..."
  nmap -sS -p 1-200 sih26145-zeek > /dev/null 2>&1
  
  echo "Generating Brute Force against SSH (Port 22)..."
  for i in $(seq 1 30); do
    nc -z -w 1 sih26145-zeek 22 > /dev/null 2>&1
  done
  
  sleep 1
done
