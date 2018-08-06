# Virtual Machine Setup

You will be using virtual machines VMs for both your local development/hacking and remotely. This guide is to help you access and setup both

## si485h remote VMs for labs

There are 4 remote VM's pre-setup for you to use both for development/hacking
and to complete the labs.

* `si585h-clone0` : `ssh -p 2210 si485h.academy.usna.edu` : NO-ASLR
* `si585h-clone1` : `ssh -p 2211 si485h.academy.usna.edu` : NO-ASLR 
* `si585h-clone2` : `ssh -p 2212 si485h.academy.usna.edu` : ASLR 
* `si585h-clone3` : `ssh -p 2213 si485h.academy.usna.edu` : ASLR 

You will be directed to an appropriate clone VM dependent on the lab
assignment. If you want a general purpose VM to use for your work, please
connect to either `clone0` or `clone1`.

Also note that each of the clone VMs runs on a different port. You must specify
the port to connect properly.

### SSH-Keys on si485h VMs

You cannot access the remote VMs with a password --- **you must use a
ssh-key**. To establish your ssh-key you will need to follow the
[gitlab](rsc/gitlab.md) setup instructions and upload a ssh public key to your
gitlab account.

## Local VM Setup

You are **strongly** encourage to set up your own local VM to complete your
assignments that is seperate from your main CS VM. This is because you'll make
some changes and alterations that you do not want to persist.

I would recommend that you use [virtualbox](https://www.virtualbox.org/) to
manage your VM, but you may use VMware as well.


### Step 1: Download Ubuntu 18.04 Desktop Edition

Download a copy of the Ubuntu 18.04.1 Desktop edition aka [Bionic
Beaver](http://releases.ubuntu.com/18.04/ubuntu-18.04.1-desktop-amd64.iso). Save
it somewhere convenient where you can access the iso later.

### Step 2: Create a VM in your VM-Manager

When completing this, make sure to provision at least...

- 16GB of local storage
- 4GB of memory

This will ensure that your VM is not too lagy. You should also give your VM a
reasonable name, such as `si485h-vm` to help distinguish it from other VMs you
may have.

Once created, load the ubuntu iso file into the CD/DVD device and boot it up.

### Step 3: Install Ubuntu

Follow the instructions for installing ubuntu as directed by the installation
media, but you **MUST using your usna network name as username during the
installation setup.** That is, your m19XXXX/m20XXXXX username. If you don't, it
will affect later settings --- you should also choose a reasonable password, but
not your network password.

Once complete, reboot the machine and remove the iso from the virtual CD-drive. 

### Step 4: Package Installation

Once you've booted your VM, you'll need to install a number of packages that
will be utilized.

```
sudo apt-get update
sudo dpkg --add-architecture i386
sudo apt-get udpate
sudo apt-get install gcc gdb nasm emacs libc6:i386 libncurses5:i386 libstdc++6:i386 gcc-multilib python python3 openssh-server git
sudo apt-get upgrade
```

You can, of course, install other packages you might like as well.

### Step 5: Local Settings


#### Generate ssh-keys

You will need a ssh-key to use the git system, generate one with `ssh-keygen` 

```
$ ssh-keygen 
Generating public/private rsa key pair.
Enter file in which to save the key (/home/aviv/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/aviv/.ssh/id_rsa.
Your public key has been saved in /home/aviv/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:k6iZX9eKG3YzqHfJVEILA0cNKTfbEvpKdvFQRKGM7Tg aviv@si485h-desktop
The key's randomart image is:
+---[RSA 2048]----+
|      .o+*+.     |
|      .=B.+      |
|      .++X .     |
|      .+=.+ .    |
|      E.S= o     |
|     +o.ooo.     |
|    +o o=o=..    |
|     ..+.=++     |
|      o.oo.      |
+----[SHA256]-----+
```

You'll of course get some other kind of art. 

#### Turn off ASLR

For 98% of what we do this semester, you'll need to have ASLR (address space
layout randomization) turned off. To do so, use the following command:

```
echo 0 | sudo tee > /proc/sys/kernel/randomize_va_space
```

You might find it useful to save this command in a bash script, maybe something called `no_aslr.sh`, like

```bash
#!/bin/bash

echo 0 > /proc/sys/kernel/randomize_va_space
```

because you'll need to turn off ASLR on every reboot

#### Set up your gdb inits

Using your favorite editor (which should be EMACS!), create a file in your home
directory `.gdbinit` and put the following lines in it.

```
set disassembly-flavor intel
alias ds=disassemble
```
The first option has it display intel syntax x86 and the set gives us a short hand to a very useful command.

#### Setup 32 bit compiler

Since your VM is a 64-bit machine, we need to use some special flags if we want
to compile C code into 32-bit executables. To make this easier, we will
establish an `alias` in your `bashrc`.

With your favorite editor (EMACS!), create a file in your home directory called
`.bash_aliases` and place the following in it.

```
alias gcc32="cc -no-pie -m32 -fno-stack-protector -z execstack"
```

Reload your `bashrc` 

```
. ~/.bashrc
```

And if you type `alias` you should see that the alias was applied

```
$ alias
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias gcc32='cc -no-pie -m32 -fno-stack-protector -z execstack'
alias grep='grep --color=auto'
alias l='ls -CF'
alias la='ls -A'
alias ll='ls -alF'
alias ls='ls --color=auto'
```

















