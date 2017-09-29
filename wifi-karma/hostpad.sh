#!/bin/sh
airmon-ng start $1
airbase-ng -C 30 --essid $2 -q ${1}mon
