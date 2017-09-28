
.PHONY: clean

CC=gcc
CFLAGS=-Wall --std=c99
OBJECTS=$(wildcard *.o)

all: $(OBJECTS) enumerate

#cribbage.o: cribbage.c cribbage.h
#	cc -o $@ -c $<
#
#score.o: score.c score.h
#	cc -o $@ -c  score.c

%.o: %.c %.h utils.h
	${CC} ${CFLAGS} -o $@ -c $<

enumerate: enumerate.c enumerate.h score.o cribbage.o utils.h
	${CC} ${CFLAGS}  -o $@  enumerate.c score.o cribbage.o -lpthread

clean:
	@rm -v  *.o
	@rm -v enumerate

