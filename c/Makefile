
.PHONY: clean

CC=gcc
CFLAGS=-Wall --std=c99 -Ofast
OBJECTS=$(wildcard *.o)

all: $(OBJECTS) enumerate db_populate

#cribbage.o: cribbage.c cribbage.h
#	cc -o $@ -c $<
#
#score.o: score.c score.h
#	cc -o $@ -c  score.c

db_populate: db_populate.c score.o cribbage.o db_populate.h
	${CC} ${CFLAGS} -o $@ db_populate.c score.o cribbage.o -lpthread -lsqlite3

%.o: %.c %.h utils.h
	${CC} ${CFLAGS} -o $@ -c $<

enumerate: enumerate.c enumerate.h score.o cribbage.o utils.h
	${CC} ${CFLAGS}  -o $@  enumerate.c score.o cribbage.o -lpthread

clean:
	@test -f enumerate && rm -v enumerate
	@test -f db_populate && rm -v db_populate
	@test -f test_score && rm -v test_score
	@rm -v  *.o

tar: c_populator.tar.gz

c_populator.tar.gz: *.c *.h Makefile tmp_db_c.db.empty
	tar cvzf $@ $^

test_score: score.c
	${CC} ${CFLAGS} -o test_score score.c cribbage.o -DMAIN_SCORE
