#!/bin/bash

NTHREADS=10
TMPFS_DIR=/tmp
EMPTY_DB_FILE=tmp_db_c.db
DB_FILE_PREFIX="tmp_db_c_"
DB_FILE_SUFFIX=".db"

cwd=${pwd}

cp $EMPTY_DB_FILE $TMPFS_DIR

cd $TMPFS_DIR

for i in {0..$NTHREADS}; do
	cp "$EMPTY_DB_FILE" "$DB_FILE_PREFIX$i$DB_FILE_SUFFIX"
done


cd $cwd


