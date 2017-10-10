
.PHONY: clean

CC=gcc
CFLAGS=-Wall --std=c99 -O3
OBJECTS=$(wildcard *.o)

all: $(OBJECTS) enumerate db_populator

#cribbage.o: cribbage.c cribbage.h
#	cc -o $@ -c $<
#
#score.o: score.c score.h
#	cc -o $@ -c  score.c

db_populator: db_populate.c db_populate.h *.o
	${CC} ${CFLAGS} -o $@ -c $< -lpthread -lsqlite3

%.o: %.c %.h utils.h
	${CC} ${CFLAGS} -o $@ -c $<

enumerate: enumerate.c enumerate.h score.o cribbage.o utils.h
	${CC} ${CFLAGS}  -o $@  enumerate.c score.o cribbage.o -lpthread

clean:
	@rm -v  *.o
	@rm -v enumerate

