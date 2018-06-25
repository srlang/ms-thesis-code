#!/bin/bash

pngname=$1
name=`basename $pngname .png`

working_dir="/tmp/$name"

source_tar="~/longtourny/py/py.tar.bz2"

db_bz2="~/longtourny/inputs/database.db.bz2"
db_bz2_name=`basename $db_bz2`
db_bz2_basename=`basename $db_bz2 .bz2`

checkpoints_tarball="~/longtourny/inputs/checkpoints.tar.gz"
checkpoints_tarball_name=`basename $checkpoints_tarball`


echo "RUNNING KALE_T2.SH"
echo "pngname=$pngname"
echo "name=$name"
echo "working_dir=$working_dir"
echo "source_tar=$source_tar"
echo "db_bz2=$db_bz2"
echo "checkpoints_tarball=$checkpoints_tarball"


# ensure the working directory is created
mkdir -pv $working_dir

# change to working directory
old_dir=${pwd}
cd $working_dir


# copy over the source directory files
#	1. all python code
#	2. database file (+ untar it)
#	3. make necessary(ish) directories
#		- checkpoints/
#		- data/

# extract source code
echo "Extracting source code tarball..."
tar xvjf $source_tar
echo "done."

# make the extra directories
echo "making the subdirectories..."
mkdir -pv checkpoints
mkdir -pv data
echo "done."


# copy over database file to data and extract
echo "copying and extracting database files..."
cp -v "$db_bz2" "data/$db_bz2_name"
time bunzip2 -v "data/$db_bz2_name"
echo "done."

echo "copying over and extracting checkpoint files..."
cp -v $checkpoints_tarball
tar xvzf $checkpoints_tarball -C checkpoints/
echo "done"


echo "ls before"
pwd
ls -al .
ls -al checkpoints
ls -al data


echo -n "loading python module to be able to actually run things..."
module load Python/3.5.2-foss-2016b
echo "done."

# create virtual environment, enter, and install dependencies
echo "creating and entering virtual environment"
mkdir -pv "venv_$name"
virtualenv "venv_$name"
source "./venv_$name/bin/activate"

echo "installing pip requirements"
pip install -r requirements.txt


# Run the actual png creation
python3 -u tournament2.py spread \
    --master-agent=checkpoints/checkpoint_agent1_20180306-161634_000000999999.txt \
    --output=$pngname \
    --x-range=0,9 \
    --x-step=1 \
    --x-label="Epoch Checkpoint (x100k)" \
    --y-label="Point Spread" \
    --games=1000 \
    --times=10 \
    --previous-agents=checkpoints/checkpoint_agent1_20180306-161634_000000000000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000100000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000200000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000300000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000400000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000500000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000600000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000700000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000800000.txt,checkpoints/checkpoint_agent1_20180306-161634_000000900000.txt


# cleanup
echo "cleaning up"
cd
rm -rf $working_dir
echo "done"
