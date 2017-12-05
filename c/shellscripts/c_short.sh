#!/bin/bash

WORK_DIR=~/c_ukko2_short
CURR_DIR=$(pwd)
#DB_DIR=/local/srlang
DB_DIR=/tmp/srlang_short
DB_BLANK="$WORK_DIR/tmp_db_c.db.empty"
DB_FILE_TEMP="tmp_db_c_"
DB_COUNT=56
DB_SINGLE="tmp_db_c.db"
DB_OUT_DIR="/home/srlang/db_out_dir_short"

date

echo "DB setup"
test -d "$DB_DIR" || mkdir -v "$DB_DIR"
cd "$DB_DIR"

#for i in {0..$DB_COUNT}; do
for ((i=0;i<$DB_COUNT;i+=1)); do
	cp -v "$DB_BLANK" "$DB_FILE_TEMP$i.db"
done

###cp -v "$DB_BLANK" "$DB_SINGLE"



echo "Running DB populator"

cd "$WORK_DIR"
time ./db_populate
#gdb ./db_populate


echo "DB cleanup"

cd "$DB_DIR"

for ((i=0;i<$DB_COUNT;i+=1)); do
	test -f "$DB_FILE_TEMP$i.db" && cp -v "$DB_FILE_TEMP$i.db" "$DB_OUT_DIR/$DB_FILE_TEMP$i.db"
	test -f "$DB_FILE_TEMP$i.db" && rm -v "$DB_FILE_TEMP$i.db"
done

###test -f "$DB_SINGLE" && cp -v "$DB_SINGLE" ~/
###test -f "$DB_SINGLE" && rm -v "$DB_SINGLE"

# 
cd "$CURR_DIR"
rmdir -v "$DB_DIR" || rm -rfv "$DB_DIR"

date
