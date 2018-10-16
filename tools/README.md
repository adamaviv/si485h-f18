# Tools, Tips, and Tricks

In this directory, you'll find a number of useful programs that will make your
life easier. However, just because they're provided, doesn't mean you don't have
to understand them, so do take a look at their source code. There are things to
learn.

* [Makefile](Makefile) : A handy, universal makefile that can compile most C and asm
  programs with the right arguments for 32 bit with all the fancy stuff turned
  off. Just put it in your source directory and fire away. It doesn't not handle
  dependencies, though, so sources should be self contained.
  
* [hexify.sh](hexify.sh) : A tool to convert a compiled assembly program into a hex string for use in an exploit.  
  
* [le-fourbytes.py](le-fourbytes.py) : A tool to make 4-byte little
  Endian words of a series of bytes with 0x prefixes and nop
  fillers. Will also use xor to do basic encoding. 
