#!/bin/sh

ifconfig at0 up
ifconfig at0 192.168.3.1 netmask 255.255.255.0
service isc-dhcp-server start

sysctl net.ipv4.ip_forward=1

iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain
iptables -P FORWARD ACCEPT
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

