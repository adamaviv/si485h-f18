#!/bin/sh

readelf -x .text $1 | grep "0x" | cut -d " "  -f 4,5,6,7 | tr "\n" " " | sed "s/ //g" | sed -e "s/\(.\)\(.\)/\\\\x\\1\\2/g" ; echo
