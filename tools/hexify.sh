#!/bin/bash

bytes=$(readelf -x .text $1 | grep "0x080" | cut -d " " -f 4,5,6,7  | tr "\n" " " | sed "s/ //g" | sed "s/\.//g")
echo $bytes | python -c "import sys; hex=sys.stdin.read().strip(); print ''.join('\\\\x%s%s'%(hex[i*2],hex[i*2+1]) for i in range(len(hex)/2))"

