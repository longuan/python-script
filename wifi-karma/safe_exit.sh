#!/bin/sh

airmon-ng stop ${1}mon
service isc-dhcp-server stop
