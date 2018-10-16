#!/usr/bin/python

import sys
import struct
import os

USAGE="""le-fourbytes.py bin [hexkey]

Convert the binary in bin to four byte littel Endian segments in
hex. If hexkey is present, then encode using xor of key for each
byte. Use - to read binary from stdin.

"""
if __name__ == "__main__":

    #default key of 0x00 has no affect on binary
    key = 0x00

    #usage check
    if len(sys.argv) < 1: 
        print >>sys.stderr, USAGE
        exit(1)

    #read in raw bytes
    if sys.argv[1] == "-":
        binary = sys.stdin.read().strip()
    else:
        binary = open(sys.argv[1]).read().strip()


    #read in key
    if len(sys.argv) == 3:
        if sys.argv[2].startswith('0x'):
            key = int(sys.argv[2],0)  & 0x000000FF
        else:
            key = int(sys.argv[2],16) & 0x000000FF
        
    #pack out to factor of 4 bytes
    for i in range(4 - len(binary) % 4):
        binary += '\x90'

    #read 4 bytes at a time
    for i in range(0,len(binary),4):
        
        #xor each four byte value with the key save as string
        by = "".join(map(chr,map(lambda b: b^key,map(ord, binary[i:i+4]))))

        #pack that string as a Little Endian integer
        d = struct.unpack("<I", by)[0]

        #write the integer as hex
        print hex(d).replace("L","")

        
        
        
        

        

        


