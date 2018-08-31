# Unit 1: C Programming and Compilation

# Hello World

Let's start in the beginning: Hello World!

``` c
/*helloworld.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  printf("Hello World!\n");

  return 0;
}
```

This program prints "Hello World!" by making a call to the library
function `printf()`, the format print function. Additionally, note that
`main()` in c programs take two arguments:

-   `int argc` : the number of command line arguments (always at least
    1)
-   `char * argv[]` : a NULL terminated array of strings for the command
    line arguments.

We'll come back to `main()`'s function arguments later when we discuss
arrays and strings. The last item to note from the `main()` function is
that it has a return value, namely 0. This return value is also the
*exit value* for the program. It is customary for programs that return
successful to return 0 while those that do not succeed to return some
value other than 0, typically 1 or 2 depending on the error.

Finally, note the two includes: `stdio.h` `stdlib.h`. These are the
*header files* for portions of the c-standard lib (often referred to as
clib). `stdio.h` refers to c standard input and output, and `stdlib`
refers to c standard library functions.

As we will see below, by default for all c programs, libc is included,
but the headers describe which portions of the library functions you
will use. The header files contain the function definitions, for example
for `printf()`, so the compiler knows if the function call type checks.
More on the compilation process next.

## Simple Compilation Process

We will use `gcc` (the GNU c compiler) exclusively to do compilation for
c programs. The most straight forward way to use `gcc` is to just call
it with the program source file as the argument.

``` example
user@si485h-clone0:demo$ gcc helloworld.c 
user@si485h-clone0:demo$ ls
a.out  helloworld.c
user@si485h-clone0:demo$ ./a.out 
Hello World!
```

This produces an output binary file called `a.out` that we can execute
to get the "Hello World!" message. If we want to compile the program to
a specific file name, same `helloworld`, then we use the `-o` option to
specify the name of the output file.

``` example
user@si485h-clone0:demo$ gcc -o helloworld helloworld.c 
user@si485h-clone0:demo$ ./helloworld 
Hello World!
```

## Multi Step Compilation Process

There is actually obscuring a large portion of the compilation process which
really involves multiple steps. A source program actually goes through two
stages before becoming a binary executable.

First, the source code must be *compiled* into *object code*, which is
an intermediate representation of the source file. This is called
compilation because there is a literal transformation of one source doe
to another source code. The object file contains the compiled source in
machine level instructions (e.g. x86 assembly) but it is not executable
yet because it must be *assembled* and *linked* properly with some other
code sources (e.g., code from the c standard library) so that it can
actually execute on the specific target machine.

To see how this works, let's look at multi-file hello world program. In
one file (below) we have the `main()` function which calls two other
functions `hello()` and `world()`, but only `hello()` is provided in the
program source. Both functions have definitions, that is, the types of
their input is known, but not the code for both functions.

``` c
/*hello.c*/
#include <stdio.h>
#include <stdlib.h>

void world(void);
void hello(void);

void hello(){
  printf("Hello ");
}

int main(int argc, char *argv[]){
  hello();
  world();
}
```

If we were to try and compile this program, we will get an error.

``` example
user@si485h-clone0:demo$ gcc -o hello hello.c
/tmp/ccC4VYbK.o: In function `main':
hello.c:(.text+0x20): undefined reference to `world'
collect2: error: ld returned 1 exit status
```

Looking closely at the error, we see that it is actually *not* gcc that
is printing an error, but rather `ld`. That is because the program
actually compiled but did not assemble properly. `ld` the GNU linker was
not able to find the reference (or code) for `world()` and failed to
link the code into the executable source and thus nothing was
assembled.

You can see, that yes, this program does actually compile by using the
`-c` tag with gcc, which says to compile the source to an object file:

``` example
user@si485h-clone0:demo$ gcc -c -o hello.o hello.c
```

This succeeds, and now we have an object file for `hello` and we need to
provide more compiled code to complete the assembly process.
Specifically, we need to provide code that fills in the `world()`
function.

``` c
/*world.c*/
#include <stdio.h>
#include <stdlib.h>

void world( ){

  printf("World!\n");
}
```

Once we have that, we can compile `world.c` into `world.o` and we can
assemble the two `.o` files into a single executable.

``` example
user@si485h-clone0:demo$ gcc -c -o world.o world.c
user@si485h-clone0:demo$ gcc -o hello hello.o world.o
user@si485h-clone0:demo$ ./hello 
Hello World!
```

However, as you will see many times in this class, there is still more going on
beneath the surface. There is still yet more code that is being used in the
assembly process. We can reveal this with the `-v` flag for gcc.

```example
aviv@si485h-clone0: demo$ gcc -v hello.o world.o -o hello
Using built-in specs.
COLLECT_GCC=gcc
COLLECT_LTO_WRAPPER=/usr/lib/gcc/x86_64-linux-gnu/7/lto-wrapper
OFFLOAD_TARGET_NAMES=nvptx-none
OFFLOAD_TARGET_DEFAULT=1
Target: x86_64-linux-gnu
Configured with: ../src/configure -v --with-pkgversion='Ubuntu 7.3.0-16ubuntu3' --with-bugurl=file:///usr/share/doc/gcc-7/README.Bugs --enable-languages=c,ada,c++,go,brig,d,fortran,objc,obj-c++ --prefix=/usr --with-gcc-major-version-only --with-as=/usr/bin/x86_64-linux-gnu-as --with-ld=/usr/bin/x86_64-linux-gnu-ld --program-suffix=-7 --program-prefix=x86_64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/lib --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --with-sysroot=/ --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-gnu-unique-object --disable-vtable-verify --enable-libmpx --enable-plugin --enable-default-pie --with-system-zlib --with-target-system-zlib --enable-objc-gc=auto --enable-multiarch --disable-werror --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --with-tune=generic --enable-offload-targets=nvptx-none --without-cuda-driver --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu
Thread model: posix
gcc version 7.3.0 (Ubuntu 7.3.0-16ubuntu3) 
COMPILER_PATH=/usr/lib/gcc/x86_64-linux-gnu/7/:/usr/lib/gcc/x86_64-linux-gnu/7/:/usr/lib/gcc/x86_64-linux-gnu/:/usr/lib/gcc/x86_64-linux-gnu/7/:/usr/lib/gcc/x86_64-linux-gnu/
LIBRARY_PATH=/usr/lib/gcc/x86_64-linux-gnu/7/:/usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu/:/usr/lib/gcc/x86_64-linux-gnu/7/../../../../lib/:/lib/x86_64-linux-gnu/:/lib/../lib/:/usr/lib/x86_64-linux-gnu/:/usr/lib/../lib/:/usr/lib/gcc/x86_64-linux-gnu/7/../../../:/lib/:/usr/lib/
COLLECT_GCC_OPTIONS='-v' '-o' 'hello' '-mtune=generic' '-march=x86-64'
 /usr/lib/gcc/x86_64-linux-gnu/7/collect2 -plugin /usr/lib/gcc/x86_64-linux-gnu/7/liblto_plugin.so -plugin-opt=/usr/lib/gcc/x86_64-linux-gnu/7/lto-wrapper -plugin-opt=-fresolution=/tmp/cc08edqZ.res -plugin-opt=-pass-through=-lgcc -plugin-opt=-pass-through=-lgcc_s -plugin-opt=-pass-through=-lc -plugin-opt=-pass-through=-lgcc -plugin-opt=-pass-through=-lgcc_s --sysroot=/ --build-id --eh-frame-hdr -m elf_x86_64 --hash-style=gnu --as-needed -dynamic-linker /lib64/ld-linux-x86-64.so.2 -pie -z now -z relro -o hello /usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu/Scrt1.o /usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu/crti.o /usr/lib/gcc/x86_64-linux-gnu/7/crtbeginS.o -L/usr/lib/gcc/x86_64-linux-gnu/7 -L/usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/7/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/7/../../.. hello.o world.o -lgcc --push-state --as-needed -lgcc_s --pop-state -lc -lgcc --push-state --as-needed -lgcc_s --pop-state /usr/lib/gcc/x86_64-linux-gnu/7/crtendS.o /usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu/crtn.o
COLLECT_GCC_OPTIONS='-v' '-o' 'hello' '-mtune=generic' '-march=x86-64'
```

Holly cow! That's a lot of stuff. The most important part is the last line, with
the program `collect2` (a fancy name for `ld`). You'll notice there is a ton of
flag options, and you'll also notice that these are 64-bit libraries and object files. 

Let's see if we get this down to the smallest set of possible library and object
files to get this to work.

## Breaking down compilation even further

First notice, if we use `ld` directly on the compilation, we get the following
error:

```example
aviv@si485h-clone0:demo$ ld hello.o world.o -o hello
ld: warning: cannot find entry symbol _start; defaulting to 00000000004000b0
hello.o: In function `hello':
hello.c:(.text+0x11): undefined reference to `printf'
world.o: In function `world':
world.c:(.text+0xc): undefined reference to `puts'
```

Two big errors: First, we don't know where the program `_start` is --- this is
the real `main()` method of a program; Second, we don't know what `printf` or
`puts` are. We need the object/library files to include these as well.

The second problem is solved more easily than the first --- we need the C
library! That's right, when we included `stdio.h` and `stdlib.h` these are
functions defined by the larger C library, and we need to link in the code for
those functions. We can do this with `-lc` flag:

```example
aviv@si485h-clone0:demo$ ld -lc hello.o world.o -o hello
ld: warning: cannot find entry symbol _start; defaulting to 0000000000400310
```

Just one more error to go. This error is related to how programs are written in
assembly where `_start` is the real starting point. We didn't write such a
function in C, but it does exist in another object file that is part of the
include list.

Looking at the `gcc -v` output, we see some `.o` files that might contain the
`_start` point. Trying `crt1.o`, this removes the error but introduces a new
one. 

```example
aviv@si485h-clone0:~/tmp$ ld -lc -o hello /usr/lib/x86_64-linux-gnu/crt1.o -lc hello.o world.o 
/usr/lib/x86_64-linux-gnu/libc_nonshared.a(elf-init.oS): In function `__libc_csu_init':
(.text+0x2d): undefined reference to `_init'
```

To solve this we can add `crti.o` which contains `_init` 

```example
aviv@si485h-clone0:~/tmp$ ld -lc -o hello /usr/lib/x86_64-linux-gnu/crt1.o /usr/lib/x86_64-linux-gnu/crti.o hello.o world.o 
/usr/lib/x86_64-linux-gnu/crt1.o: In function `_start':
(.text+0x12): undefined reference to `__libc_csu_fini'
(.text+0x19): undefined reference to `__libc_csu_init'
```

Which introduces a new error because the c library contains those methods, so we
have to relink that after that object, move the `-lc` later in the command.

```
aviv@si485h-clone0:~/tmp$ ld -o hello /usr/lib/x86_64-linux-gnu/crt1.o -lc /usr/lib/x86_64-linux-gnu/crti.o hello.o world.o 
```

And we have a clean compilation, but running our program, that introduces problems.

```
aviv@si485h-clone0:~/tmp$ ./hello 
-bash: ./hello: No such file or directory
aviv@si485h-clone0:~/tmp$ ls hello
hello
```

That's awfully strange, because `hello` is where we would expect it. What gives?
Well, it turns out that the error is within the execution of `hello` and not the
absence of `hello`. The error is that we are missing `ld` library code that will
do the dynamic loading as part of the linux system. This needs to be dynamically
linked in, like below.

```
aviv@si485h-clone0:~/tmp$ ld --dynamic-linker /lib64/ld-linux-x86-64.so.2  -o hello /usr/lib/x86_64-linux-gnu/crt1.o -lc /usr/lib/x86_64-linux-gnu/crti.o hello.o world.o 
aviv@si485h-clone0:~/tmp$ ./hello 
Segmentation fault (core dumped)
```

Closer, but still missing something --- we need some code to end the
assembly. In particular, `crtn.o` contains our ending routines and completes the
circle.

```
aviv@si485h-clone0:~/tmp$ ld --dynamic-linker /lib64/ld-linux-x86-64.so.2  -o hello /usr/lib/x86_64-linux-gnu/crt1.o -lc /usr/lib/x86_64-linux-gnu/crti.o hello.o world.o  /usr/lib/x86_64-linux-gnu/crtn.o 
aviv@si485h-clone0:~/tmp$ ./hello 
Hello World!
```

Hello world, indeed.

## 32 Bit Compilation

All of that was for 64-bit compilation since we will be running our programs on
a 64-bit machine. However, hacking in 64-bits is a whole other level and not
covered in this class. Instead we'll do our compilation in 32-bit.

Fortunately, most 64-bit processors can execute 32-bit code, and `gcc` can
compile into both variants, with the right flags. (There's always another flag
for that in `gcc`!).

In the compilation instructions, you'll notice that there is a flag `-m
elf_x86_64`. The `-m` flag specifies the machine type to compile to. For our
purposes, we can specify `-m32` (shorthand for `elf_x86`), and we can see we
have a different kind of file now. 

```
aviv@si485h-clone0:~/tmp$ gcc helloworld.c
aviv@si485h-clone0:~/tmp$ file a.out 
a.out: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=9d9573a79d4bce9874568534406bb99533995299, not stripped
aviv@si485h-clone0:~/tmp$ gcc -m32 helloworld.c
aviv@si485h-clone0:~/tmp$ file a.out 
a.out: ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=4b6a3496b7616638a4ce488997628f0faceee5e4, not stripped
```

Note that elf is the file type for executable binaries on linux, and 32-bit elf
file runs just fine, even on a 64 bit machine (if you have the right libraries
installed --- see [resources](../resources/vms.md) for how to setup a machine for that)

```
aviv@si485h-clone0:~/tmp$ ./a.out 
Hello, world!
```

As a last note, as of `gcc` version 7.3, all programs are compiled with position
independent loading. This isn't a big deal for hacking, generally, but it will
make some stuff annoying, so we will by default turn it off with the `-no-pie` flag.

```
aviv@si485h-clone0:~/tmp$ gcc -m32 -no-pie helloworld.c
aviv@si485h-clone0:~/tmp$ ./a.out 
Hello, world!
```

Finally, finally, we will also use a slew of other flags to turn off security
features. The eventually compilation will be obnoxiously long.

```
aviv@si485h-clone0:~/tmp$ gcc -no-pie -m32 -fno-stack-protector -z execstack helloworld.c
aviv@si485h-clone0:~/tmp$ ./a.out 
Hello, world!
```

As such, we'll create an alias for these set of compilations, `gcc32`.

```
aviv@si485h-clone0:~/tmp$ alias gcc32
alias gcc32='gcc -no-pie -m32 -fno-stack-protector -z execstack'
aviv@si485h-clone0:~/tmp$ gcc32 helloworld.c
aviv@si485h-clone0:~/tmp$ ./a.out 
Hello, world!
```

And for simplicity in the notes, I will shorthand `gcc32` just to `gcc`, and you
should assume that ALL `gcc` compilation is occurring in 32 bit mode with these
options, unless otherwise specified. 


# Library Functions vs. System Calls

If you look more closely at the `ld` command line above, you will also
see the flag `-lc` which says to include `clib` in the compilation. The
c standard library provides a lot of functionality for the programmer,
but its primary task is to provide an interface by which the programmer
can easily access the underlying operating system interface.

Recall that a system call is a mechanisms for the programmer to gain
access to an operating system feature. The operating system provides a
few key features relevant to this class:

-   Input/Output : reading and writing from devices, such as the
    terminal, network, and other peripherals
-   Memory Management : maintain the memory for programs and ensuring
    that programs do not access memory that is invalid, this includes
    maintaining the virtual memory layout for a program
-   Program Execution: loading and unloading programs and executing them
    on the CPU

## Tracing Function and System Calls

A library function, on the other hand, provides a more user friendly
interface to the system calls. To see this dynamic, we can *trace* a
programs execution and see where library functions vice system calls.
There are two tracers we will use heavily in this class:

-   `ltrace` trace library functions
-   `strace` trace system calls.

And we can look at the output of these traces to get a sense of how
programs execute.

``` example
user@si485h-clone0:demo$ ltrace ./hello > /dev/null 
__libc_start_main(0x8048304, 1, 0xbffa7744, 0x8048360 <unfinished ...>
printf("Hello ")                                                                  = 6
puts("World!")                                                                    = 7
+++ exited (status 7) +++
```

In the `ltrace` above, we see that for the `hello` program from the
previous section, there are two library calls: `printf()` and `puts()`.
If you were to look at the manual page, both `puts()` `printf()` takes a
string and writes it to `stdout`. However, we know that the actual
method for writing to `stdout` is using the `write()` system call, and
we can see this using `strace`.

``` example
user@si485h-clone0:demo$ strace ./hello > /dev/null 
execve("./hello", ["./hello"], [/* 20 vars */]) = 0
brk(0)                                  = 0x87b7000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
mmap2(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb7760000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat64(3, {st_mode=S_IFREG|0644, st_size=70286, ...}) = 0
mmap2(NULL, 70286, PROT_READ, MAP_PRIVATE, 3, 0) = 0xb774e000
close(3)                                = 0
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
open("/lib/i386-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0\340\233\1\0004\0\0\0"..., 512) = 512
fstat64(3, {st_mode=S_IFREG|0755, st_size=1754876, ...}) = 0
mmap2(NULL, 1759868, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0xb75a0000
mmap2(0xb7748000, 12288, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1a8000) = 0xb7748000
mmap2(0xb774b000, 10876, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0xb774b000
close(3)                                = 0
mmap2(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb759f000
set_thread_area({entry_number:-1 -> 6, base_addr:0xb759f940, limit:1048575, seg_32bit:1, contents:0, read_exec_only:0, limit_in_pages:1, seg_not_present:0, useable:1}) = 0
mprotect(0xb7748000, 8192, PROT_READ)   = 0
mprotect(0xb7783000, 4096, PROT_READ)   = 0
munmap(0xb774e000, 70286)               = 0
fstat64(1, {st_mode=S_IFCHR|0666, st_rdev=makedev(1, 3), ...}) = 0
ioctl(1, SNDCTL_TMR_TIMEBASE or SNDRV_TIMER_IOCTL_NEXT_DEVICE or TCGETS, 0xbf8187d8) = -1 ENOTTY (Inappropriate ioctl for device)
mmap2(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb775f000
write(1, "Hello World!\n", 13)          = 13
exit_group(7)                           = ?
+++ exited with 7 +++
```

In fact, there are a lot of system calls that get involved here.
Starting at the top, we have the `execve()` system call that executes
the program, but after that, there is a lot of loading and reading
libraries into memory. And finally, two from the bottom, we see the
`write()` system call to `stdout` (file descriptor 1).

## Hello System Call

We can, of course, write a hello-world program without any library
functions. But, we'll need some helper functions, like writing our own
string length function.

``` c
/*hellosystem.c*/
#include <unistd.h>


int mystrlen(char * str){

  int i;
  for(i=0; str[i]; i++);

  return i;

}


int main(int argc, char *argv[]){

  char str[] = "Hello World!\n";

  write(1,str,mystrlen(str));

}
```

Compiling and executing this program and analyzing the `ltrace`, we
still see a call to `write()` but no calls to `puts()` or `printf()`.

``` example
user@si485h-clone0:demo$ ltrace ./hellosystem > /dev/null 
__libc_start_main(0x8048494, 1, 0xbf8c5034, 0x8048510 <unfinished ...>
write(1, "Hello World!\n", 13)                                                                                                    = 13
+++ exited (status 13) +++
```

The reason that `write()` still appears is that this `write()` is not
the *real* system call `write()`, but is a library wrapper to it ... but
that is a story for another day. What's more interesting is the
`strace`, which if you observe closely, you will see is the same as the
other version of the program.

``` example
user@si485h-clone0:demo$ strace ./hellosystem > /dev/null 
execve("./hellosystem", ["./hellosystem"], [/* 20 vars */]) = 0
brk(0)                                  = 0x8c9b000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
mmap2(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb77c3000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat64(3, {st_mode=S_IFREG|0644, st_size=70286, ...}) = 0
mmap2(NULL, 70286, PROT_READ, MAP_PRIVATE, 3, 0) = 0xb77b1000
close(3)                                = 0
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
open("/lib/i386-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0\340\233\1\0004\0\0\0"..., 512) = 512
fstat64(3, {st_mode=S_IFREG|0755, st_size=1754876, ...}) = 0
mmap2(NULL, 1759868, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0xb7603000
mmap2(0xb77ab000, 12288, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1a8000) = 0xb77ab000
mmap2(0xb77ae000, 10876, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0xb77ae000
close(3)                                = 0
mmap2(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb7602000
set_thread_area({entry_number:-1 -> 6, base_addr:0xb7602940, limit:1048575, seg_32bit:1, contents:0, read_exec_only:0, limit_in_pages:1, seg_not_present:0, useable:1}) = 0
mprotect(0xb77ab000, 8192, PROT_READ)   = 0
mprotect(0x8049000, 4096, PROT_READ)    = 0
mprotect(0xb77e6000, 4096, PROT_READ)   = 0
munmap(0xb77b1000, 70286)               = 0
write(1, "Hello World!\n", 13)          = 13
exit_group(13)                          = ?
+++ exited with 13 +++
```

# Numeric Data Types and Sign-ness

## Basic Numeric Types

Let's recall the basic data types for C programs. One thing to consider
is that we are going to be working with 32-bit architectures as opposed
to 64-bit ones. This is mostly to keep things simple for the exploits,
but it does mean some things may be a bit different at times.

For example, consider this program and its output with the basic numeric
types.

``` c
/*datatypes.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]){

  char c = 0xef;
  short s = 0xbeef;
  int i = 0xdeadbeef;
  long l = 0xcafebabe;

  printf("char c=%d size=%u\n",c,sizeof(char));
  printf("short s=%d size=%u\n",s,sizeof(short));
  printf("int i=%d size=%u\n",i,sizeof(int));
  printf("long l=%ld size=%u\n",l,sizeof(long));

  return 0;
}
```

``` example
user@si485h-clone0:demo$ ./datatypes
char c=-17 size=1
short s=-16657 size=2
int i=-559038737 size=4
long l=-889275714 size=4
```

Notice that the long number is the same size as an integer, 4-bytes, as
opposed to 8-bytes on 64 bit machines. This is because the registers on
32 bit machines are 32 bits wide, and storing 8-byte values is annoying,
at best. You can still have 8-byte values, but you have to use
`long long`.

## Signed Numeric Values

The basic numeric types are also signed, that is, their range of values
go from [ -2<sup>(w-1)</sup> : 2<sup>(w-1)</sup>-1 ] because one of the
bits is used to indicate the sign. The signed bit is the leading one, if
it is 1 then the number is negative, but if it is 0, the number is
positive. Positive numbers are represented as you may expected, with
regard to binary counting; however, negative numbers are represented
with 2's-compliment. That means, you count backwards ... sort of.

See the example below for the greatest and smallest negative values:

``` c
/*signess.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  //largest positive signed int: 
  //  binary: 0111 1111 1111 1111 1111 1111 1111 1111
  //     hex:   7    f     f    f    f    f   f    f
  int l_pos = 0x7fffffff;

  //smallest postivie signed int: 
  //  binary: 0000 0000  0000 0000 0000 0000 0000 0000
  //     hex:   0   0     0    0    0    0    0    0
  int s_pos = 0x00000000;

  //smallest negative signed int:
  //  binary: 1000 0000 0000 0000 0000 0000 0000 0000
  //     hex:   8    0    0     0    0    0    0   0
  int s_neg = 0x80000000;


  //largest negative signed int:
  //  binary: 1111 1111 1111 1111 1111 1111 1111 1111
  //     hex:   8    f   f     f    f    f    f   f
  int l_neg = 0xffffffff;



  printf(" largest positive=%d \t (0x%08x)\n",l_pos,l_pos);
  printf("smallest positive=%d \t\t (0x%08x)\n",s_pos,s_pos);
  printf("\n");

  printf(" largest negative=%d \t\t (0x%08x)\n",l_neg,l_neg);
  printf("smallest negative=%d \t (0x%08x)\n",s_neg,s_neg);
  printf("\n");

}
```

``` example
user@si485h-clone0:demo$ ./signess 
 largest positive=2147483647     (0x7fffffff)
smallest positive=0          (0x00000000)

 largest negative=-1         (0xffffffff)
smallest negative=-2147483648    (0x80000000)
```

If we were to count in twos-complement with negative numbers, we start
at 0xffffffff (-1) and go to 0x80000000 (-2147483648). This where the
counting backwards comes from, except we are counting backwards in the
lower 31 bits. The program below shows this clearly:

``` c
/*twos-comp.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int s_neg = 0x80000000;
  int l_neg = 0xffffffff;

  printf("largest negative  =%d \t\t(0x%08x)\n",l_neg,l_neg);
  printf("largest negative-1=%d \t\t(0x%08x)\n",l_neg-1,l_neg-1);
  printf("largest negative-2=%d \t\t(0x%08x)\n",l_neg-2,l_neg-2);
  printf("largest negative-3=%d \t\t(0x%08x)\n",l_neg-3,l_neg-3);
  printf("...\n");
  printf("smallest negative+3=%d (0x%08x)\n",s_neg+3,s_neg+3);
  printf("smallest negative+2=%d (0x%08x)\n",s_neg+2,s_neg+2);
  printf("smallest negative+1=%d (0x%08x)\n",s_neg+1,s_neg+1);
  printf("smallest negative  =%d (0x%08x)\n",s_neg,s_neg);

}
```

``` example
user@si485h-clone0:demo$ ./twos-comp
largest negative  =-1       (0xffffffff)
largest negative-1=-2       (0xfffffffe)
largest negative-2=-3       (0xfffffffd)
largest negative-3=-4       (0xfffffffc)
...
smallest negative+3=-2147483645 (0x80000003)
smallest negative+2=-2147483646 (0x80000002)
smallest negative+1=-2147483647 (0x80000001)
smallest negative  =-2147483648 (0x80000000)
```

Of course, as with all data in C, how we interpret ones and zeros is
really in the eye of the beholder. If we were to instead interpret these
values as **unsigned**, then we get very different output:

``` c
/*unsigned.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int s_neg = 0x80000000;
  int l_neg = 0xffffffff;

  printf("(unsigned) largest negative  =%u \t\t(0x%08x)\n",l_neg,l_neg);
  printf("(unsigned)  largest negative-1=%u \t\t(0x%08x)\n",l_neg-1,l_neg-1);
  printf("(unsigned) largest negative-2=%u \t\t(0x%08x)\n",l_neg-2,l_neg-2);
  printf("(unsigned) largest negative-3=%u \t\t(0x%08x)\n",l_neg-3,l_neg-3);
  printf("...\n");
  printf("(unsigned) smallest negative+3=%u (0x%08x)\n",s_neg+3,s_neg+3);
  printf("(unsigned) smallest negative+2=%u (0x%08x)\n",s_neg+2,s_neg+2);
  printf("(unsigned) smallest negative+1=%u (0x%08x)\n",s_neg+1,s_neg+1);
  printf("(unsigned) smallest negative  =%u (0x%08x)\n",s_neg,s_neg);

}
```

``` example
user@si485h-clone0:demo$ ./unsigned 
(unsigned) largest negative  =4294967295  (0xffffffff)
(unsigned) largest negative-1=4294967294  (0xfffffffe)
(unsigned) largest negative-2=4294967293  (0xfffffffd)
(unsigned) largest negative-3=4294967292  (0xfffffffc)
...
(unsigned) smallest negative+3=2147483651 (0x80000003)
(unsigned) smallest negative+2=2147483650 (0x80000002)
(unsigned) smallest negative+1=2147483649 (0x80000001)
(unsigned) smallest negative  =2147483648 (0x80000000)
```

# Pointers and Memory References

## Pointers Basic

Pointers (or memory references) are crucial for C programs. Some
terminology for the syntax of pointers:

-   `int * p` : *declaring* an integer pointer `p`.
-   The *value* or *pointer value* of `p` is a memory reference, an
    address of a memory value.
-   `*p` : *de-referencing* means to *follow the pointer* to the memory
    referenced by `p` and change the memory value there.
-   `&a` : *address of* the variable a, which is a *pointer value* since
    it a memory reference.

The best way to get a feeling for this is to see it in action:

``` c
/*reference.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int a = 10;
  int b = 20;
  int * p = &a; //MARK 1

  *p = b; //MARK 2

  p = &b;
  b = 50; //MARK 3

  printf("a=%d &a=%p\n",a,&a);
  printf("b=%d &b=%p\n",b,&b);
  printf("p=%p &p=%p *p=%d\n",p,&p,*p);

  return 0;
}
```

We can analyze this using a memory diagram for each of the marks. We use
arrows to indicate a memory reference.

``` example

   MARK 1            Mark 2           Mark 3

  .----.----.       .----.----.      .----.----.
  | a  | 10 |<-.    | a  | 20 |<-.   | a  | 20 |
  |----+----|  |    |----+----|  |   |----+----|
  | b  | 20 |  |    | b  | 20 |  |   | b  | 50 |<-.
  |----+----|  |    |----+----|  |   |----+----|  |
  | p  |  --+--'    | p  |  --+--'   | p  |  --+--'
  '----'----'       '----'----'      '----'----'
```

And, we can see the last mark is the case when we run the program.

``` example
user@si485h-clone0:demo$ ./reference 
a=20 &a=0xbfd00ebc
b=50 &b=0xbfd00eb8
p=0xbfd00eb8 &p=0xbfd00eb4 *p=50
```

Notice, though, that the pointer values or memory references are really
just numbers. Really, the way we should model this diagram is with the
full references and values, for the end state:

``` example
       address     value
    .------------.------------.
  a | 0xbfaebd9c |  20        |
    |------------+------------|
  b | 0xbfd00eb8 |  50        | <-.
    |------------+------------|   |
  p | 0xbfd00eb4 | 0xbfd00eb8 | --'
    '------------'------------'
```

## Randomization of Memory

One thing that will trip you up is that on most modern linux install,
each run of the program will randomize the address space. The reason for
this will be clear later, but the implications is that when your run the
program again, you'll get different values.

``` example
user@si485h-clone0:demo$ ./reference 
a=20 &a=0xbfaebd9c
b=20 &b=0xbfaebd98
p=0xbfaebd98 &p=0xbfaebd94 *p=50
```

To ensure that this will not be the case, you'll have to turn this
feature off. Here's how to do that.

``` example
user@si485h-clone0:demo$ echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

Now, when you run the program, you'll get the same output ever time.

``` example
user@si485h-clone0:demo$ ./reference 
a=20 &a=0xbffff6bc
b=20 &b=0xbffff6b8
p=0xbffff6b8 &p=0xbffff6b4 *p=50
user@si485h-clone0:demo$ ./reference 
a=20 &a=0xbffff6bc
b=20 &b=0xbffff6b8
p=0xbffff6b8 &p=0xbffff6b4 *p=50
user@si485h-clone0:demo$ 
```

# Arrays and Strings

## Array Values and Pointers are the same thing!

Here is a fact: pointers and array values are the same thing. Hold this
truth to be self-evident, and you will never be lost in the dark forest
of memory ...

Why is this truth true? Well it has to do with the definition of an
array. An `array` is a contiguous memory block of a sequence of
similarly typed data types. An array is a reference to the first data
item in the contiguous memory block, and thus an array's value
references memory. That means an array value is a pointer. Boom!

If that is not so clear, let's look at an example.

``` c
/*arrays.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int a[] = {10,11,12,13,14};

  int * p = a;

  p[2] = 5;

  printf("a=%p p=%p\n",a,p);

  int i;
  for(i=0;i<5;i++){
    printf("a[%d] = %d\n",i,a[i]);
  }

  return 0;
}
```

Here, an array `a` is declared with 5 values, and we allow the pointer
`p` to hold the same value as a. Wait! Notice, that we did not use `&`
to set the value of `p`. This is a straight assignment, so the value in
`a` is already a memory reference to an integer because that is the kind
of data that `p` stores.

Next, notice that this line:

``` c
  p[2] = 5;
```

We are using the array index operator `[ ]` with `p`, so in a very real
sense, we are treating `p` as an array. And, the operation does as we
would expect in the output.

``` example
user@si485h-clone0:demo$ ./arrays 
a=0xbffff6b4 p=0xbffff6b4
a[0] = 10
a[1] = 11
a[2] = 5
a[3] = 13
a[4] = 14
```

This begs the question: What is the array index operator anyway? It's a
special deference that adds the index to the base. For example:

``` example
  p[i]  <-- same as --->   *(p+i) 
```

You can see this to be true in the following example:

``` c
/*p_arrays.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int a[] = {10,11,12,13,14};

  int * p = a;

  *(p+2) = 5;

  printf("a=%p p=%p\n",a,p);

  int i;
  for(i=0;i<5;i++){
    printf("a+%d=%p *(a+%d) = %d\n",i,a+i,i,a[i]);
  }

  return 0;
}
```

``` example
user@si485h-clone0:demo$ ./p_arrays 
a=0xbffff6b4 p=0xbffff6b4
a+0=0xbffff6b4 *(a+0) = 10
a+1=0xbffff6b8 *(a+1) = 11
a+2=0xbffff6bc *(a+2) = 5
a+3=0xbffff6c0 *(a+3) = 13
a+4=0xbffff6c4 *(a+4) = 14
```

Ok, so if array values and pointers the same, why do we have array
values? Well, I lied, just a bit. Array values and pointers are the same
in the sense that they are both memory references, but the declaration
of an array and the declaration of a pointer are **not** the same. When
you declare an array, you are declare a region of memory all at once,
and you must be able to always reference that memory, otherwise you'll
have a memory leak. That is, an array value is immutable or constant ---
it cannot change.

When you declare a pointer, on the other hand, you are creating a
variable whose value reference memory, but the memory it references can
change.

## Pointer Arithmetic

Let's take a closer look at the last output:

``` example
user@si485h-clone0:demo$ ./p_arrays 
a=0xbffff6b4 p=0xbffff6b4
a+0=0xbffff6b4 *(a+0) = 10
a+1=0xbffff6b8 *(a+1) = 11
a+2=0xbffff6bc *(a+2) = 5
a+3=0xbffff6c0 *(a+3) = 13
a+4=0xbffff6c4 *(a+4) = 14
```

Notice the memory reference on each incrimination. While we are adding
just 1 to the value a, the resulting memory reference is changing by 4.
That is because each integer is four bytes wide, so the computer has to
shift each array index reference by the size of the data types stored
within the array.

Consider the same style program for different types, and this fact
becomes apparent:

``` c
/*pointer_arithemtic.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  int a[] = {10,11,12,13,14};
  short s[] = {10,11,12,13,14};
  char c[] =  {10,11,12,13,14};

  int i;
  for(i=0;i<5;i++){
    printf("a+%d=%p *(a+%d) = %d\n",i,a+i,i,a[i]);
  }

  printf("\n");

  for(i=0;i<5;i++){
    printf("s+%d=%p *(s+%d) = %d\n",i,s+i,i,s[i]);
  }

  printf("\n");

  for(i=0;i<5;i++){
    printf("c+%d=%p *(c+%d) = %d\n",i,c+i,i,c[i]);
  }

  return 0;
}
```

``` example
user@si485h-clone0:demo$ ./pointer_arithemtic 
a+0=0xbffff6a8 *(a+0) = 10
a+1=0xbffff6ac *(a+1) = 11
a+2=0xbffff6b0 *(a+2) = 12
a+3=0xbffff6b4 *(a+3) = 13
a+4=0xbffff6b8 *(a+4) = 14

s+0=0xbffff69e *(s+0) = 10
s+1=0xbffff6a0 *(s+1) = 11
s+2=0xbffff6a2 *(s+2) = 12
s+3=0xbffff6a4 *(s+3) = 13
s+4=0xbffff6a6 *(s+4) = 14

c+0=0xbffff699 *(c+0) = 10
c+1=0xbffff69a *(c+1) = 11
c+2=0xbffff69b *(c+2) = 12
c+3=0xbffff69c *(c+3) = 13
c+4=0xbffff69d *(c+4) = 14
```

## Strings

C-strings(!!!!) the bane of student programmers worldwide, but they are
not really that bad if you remember that string is simply an array of
characters that is null terminated. In its most pedantic usage, we can
declare a string as an array in the standard sense.

``` c
/*chararray.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  char str[] = {'H','e','l','l','o',' ','W','o','r','l','d','!','\n','\0'};

  printf("%s",str);

  return 0;
}
```

However, this is a huge burden, so in C, we can use the double-quote
mark to declare strings which automatically creates the array and null
terminates. As below:

``` c
/*string.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  char str[] = "Hello World!\n";

  printf("%s",str);

  return 0;
}
```

Notice, that when we declare a string with double-quotes, we still have
to declare the variable that references the string as an array type (or
a pointer type) that's because it is still an array.

And, like arrays of integer, we can still reference individual items in
the array using pointer iteration. It is also typical with strings to
leverage the fact that it is NULL terminated. NULL is just a pseudonym
for 0, which is a false value.

``` c
/*string_iterate.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv[]){

  char str[] = "Hello World!\n";
  char * c;

  for( c = str;*c; c++){
    putchar(*c);
  }

  return 0;
}
```

# Program Memory Layout

## Cowboys and Endian-s

If you think about it, there are two very different fundamental ways to
organize bytes with meaning. As western language thinkers and learning,
we assign meaning from left to right. For example, if I wrote down the
number:

210500

That is the number two-hundred-and-ten thousand, five hundred. It is not
the number five thousand and twelve (reading the number right to left).

Where the most-significant byte is represented is referred to as
*endian-ness* in computer science. By far the most prevalent
representation is *little endian*, by which the **least significant
bytes come first**. This is in opposition to *big endian*, which is how
we think of things, where the most significant byte comes first.

The impact of this becomes clear with a simple program below.

``` c
/*endian.c*/
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char * argv){

  int a = 0xdeadbeef;

  //treat the integer like a array of one-byte values
  char * p = (char *) &a;

  int i;
  for(i=0;i<4;i++){
    printf("p[%d] = 0x%hhx\n",i,p[i]);
  }

  return 0;

}
```

Here, we treat the integer `a` as a buffer of 4-bytes. If we write those
bytes out indexed from 0 to 3, we see that the number 0xdeadbeef is
written out in reveres, 0xef, 0xbe, 0xad, 0xde.

``` example
user@si485h-clone0:demo$ ./endian 
p[0] = 0xef
p[1] = 0xbe
p[2] = 0xad
p[3] = 0xde
```

## Stack, Heap, Data, BSS

Now that we have a decent sense of how we interact with memory, let's
spend some time looking at the memory address layout. The big question
is, when we declare a variable/value/data, where is that data located?

To start, we need to remind ourselves of the **virtual address space**,
which allows a single program to treat the entire available memory space
in an ordered way, from high to low addresses. In reality, the memory is
stored in physical RAM in random locations, but from the program's
perspective, it's all lined up.

When a program is loaded into memory, there are different regions for
different kinds of data. A key concept, though, is that the program's
data and its code all reside in memory together, which is what we will
leverage when we exploit programs later.

Here are the general areas of the program memory layout, from higher
address to lower address. Note that this is a 32-bit memory addresses,
so there is total of about 4GB in the memory space.

``` example


higher address
0xffffffff --> .----------------.
               |    reserved    |  <-- command line args
               +----------------+      environment variables
               |                |
               |     stack      |  <-- user stack, function frames
               |       |        |
               :       |        :
               '       v        '
                                   <-- mapped data
               .       ^        .
               :       |        :
               |       |        |
               |     heap       |  <-- user heap, dynamic memory
               +----------------+
               |      bss       |  <-- global memory 
               +----------------+
               |     text       |  <-- code segments
0x00000000 --> '----------------'
lower address
```

Here's what each of these sections are used for:

-   *reserved*: the reserved space is used for passing environment
    variables and command line arguments to the program.
-   *stack*: the stack is for organizing the execution of the program
    into stack frames for tracing functions and local variables. Each
    function call *pushes* a stack fram. from on the stack, and each
    return *pops* off a stack frame. The stack grows towards lower
    addresses, into empty memory address space.
-   *heap* : the heap is for dynamic, global memory allocations, such as
    called from `malloc()`
-   *bss* : the bss is used to store global or statically declared values
-   *text* : is where the program code, i.e., the x86 instructions, is
    stored.

We can see each of these memory locations in the following program:

``` c
/*mem_layout.c*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void foo(void) { return; }

int main(int argc, char *argp[], char *envp[]){

  int a = 10;

  char stack_str[] = "Hello";

  char * heap_str = malloc(strlen(stack_str)+1);
  strcpy(heap_str,stack_str);

  char * bss_str = "World";



  printf("(reserved)   evnp = 0x%08x \n", envp);
  printf("(stack)        &a = 0x%08x \n", &a);
  printf("(stack) stack_str = 0x%08x \n", stack_str);
  printf("(heap)   heap_str = 0x%08x \n", heap_str);
  printf("(bss)     bss_str = 0x%08x \n", bss_str);
  printf("(text)       main = 0x%08x \n", main);
  printf("(text)        foo = 0x%08x \n", foo);
}
```

``` example
user@si485h-clone0:demo$ ./mem_layout 
(reserved)   evnp = 0xbffff77c 
(stack)        &a = 0xbffff6c4 
(stack) stack_str = 0xbffff6be 
(heap)   heap_str = 0x0804b008 
(bss)     bss_str = 0x08048630 
(text)       main = 0x080484b3 
(text)        foo = 0x080484ad 
```
