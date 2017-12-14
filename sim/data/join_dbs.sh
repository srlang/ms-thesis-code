#!/bin/bash

fields="kcard0,kcard1,kcard2,kcard3,tcard0,tcard1,kmin,kmax,kmed,kavg,kmod,tmin,tmax,tmed,tavg,tmod"
joined_name="all_joined.db"

# copy the first db over to have a base
cp -v tmp_db_c_0.db "$joined_name"


for x in {1..55}; do
	att_db="tmp_db_c_$x.db"

	echo "ATTACH '$att_db' as tomerge; "\
		"BEGIN; "\
		"INSERT INTO keep_throw_stats($fields) SELECT $fields FROM tomerge.keep_throw_stats; "\
		"COMMIT; "

	echo "ATTACH '$att_db' as tomerge; "\
		"BEGIN; "\
		"INSERT INTO keep_throw_stats($fields) SELECT $fields FROM tomerge.keep_throw_stats; "\
		"COMMIT; " \
		| sqlite3 "$joined_name"

done




