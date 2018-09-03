CC=gcc
CFLAGS=-m32 -no-pie -fno-stack-protector -z execstack -Wno-format-security -O0 -g
SRC=$(wildcard *.c)
BIN=$(SRC:.c=)

AS=nasm
ASFLAGS=-g -f elf32
LD=ld

AS_SRC=$(wildcard *.asm)
AS_OBJ=$(AS_SRC:.asm=.o)
AS_BIN=$(AS_SRC:.asm=)


all: $(BIN) $(AS_BIN)

$(AS_BIN): $(AS_OBJ)
	$(LD) $(LDFLAGS) -o $@ $(@:=.o)

$(AS_OBJ): $(AS_SRC)
	$(AS) $(ASFLAGS) -o $@ $(@:.o=.asm)

clean:
	rm -f *.o $(BIN) $(AS_OBJ) $(AS_BIN) *~
