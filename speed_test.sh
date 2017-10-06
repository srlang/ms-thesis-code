#!/bin/bash

WORK_DIR=~/Documents/hy/thesis/code/sim
CURR_DIR=$(pwd)
DB_FILE=/tmp/tmp_db.db
DB_OUTPUT="./tmp_db.db_$(date -j '+%H:%M:%s')"
PYPY_BIN_DIR=/Users/srlang/Brew/bin
PYPY_BIN="$PYPY_BIN_DIR/pypy3"
RECORDS_SCRIPT=records.py

cd "$WORK_DIR"

# wipe existing database to make sure it's clear for next run
test -f "$DB_FILE" && rm -v "$DB_FILE"
touch "$DB_FILE"

date
time "$PYPY_BIN" "$RECORDS_SCRIPT"
#cp -v "$DB_OUTPUT" "db_$(date -j '+%H:%M:%s')"
cp -v "$DB_FILE" "$DB_OUTPUT"
date

cd "$CURR_DIR"


