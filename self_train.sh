#!/bin/zsh

# Parameters wanted:
#	1: name (use for working_dir)
#	2: db_bz2
#	3: agent_1_file
#	4: agent_2_file
#	5: epochs
#	6: checkpoints

PYEXE="python3"
source_dir="/Users/srlang/Documents/hy/thesis/code/sim"
source_tar="$source_dir/py.tar.bz2"
name="$1"
working_dir="/tmp/$1"
db_bz2="$2"
db_bz2_name=`basename $db_bz2`
db_bz2_basename=`basename $db_bz2 .bz2`
agent_1_file="$3"
agent_2_file="$4"
epochs="$5"
checkpoints="$6"
output_dir='/Users/srlang/tmp'

echo "running script with parameters:\n"\
	"\tPYEXE=$PYEXE\n"\
	"\tsource_dir=$source_dir\n"\
	"\tsource_tar=$source_tar\n"\
	"\tname=$name\n"\
	"\tworking_dir=$working_dir\n"\
	"\tdb_bz2=$db_bz2\n"\
	"\tdb_bz2_name=$db_bz2_name\n"\
	"\tdb_bz2_basename=$db_bz2_basename\n"\
	"\tagent_1_file=$agent_1_file\n"\
	"\tagent_2_file=$agent_2_file\n"\
	"\tepochs=$epochs\n"\
	"\tcheckpoints=$checkpoints\n"\
	"\toutput_dir=$output_dir"

#if [[ `false` ]]; then 
# ensure the working directory is created
[[ -d $working_dir ]] || mkdir -v $working_dir

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
tar -xvJf $source_tar
echo "done."

# make the extra directories
echo "making the subdirectories..."
mkdir -pv checkpoints
mkdir -pv data
echo "done."


# copy over database file to data and extract
echo "copying and extracting database files..."
cp -v "$db_bz2" "data/$db_bz2_name"
bunzip2 -v "data/$db_bz2_name"
echo "done."


echo "ls before"
pwd
ls -alR .


# run the actual experiments
echo -n "Running the actual experiment..."
$PYEXE train.py game\
	--epochs "$epochs"\
	--checkpoint "$checkpoints"\
	--agent1file "$agent_1_file"\
	--agent2file "$agent_2_file"
echo "done."


# zip up the database file for easier copy
echo -n "zipping up completed database file..."
bzip2 "data/$db_bz2_basename"
echo "done."


echo "ls after"
pwd
ls -alR .


# return to output directory
mkdir -pv $output_dir
cd $output_dir

# copy over the files we care about
#	1. checkpoints (for analysis later)
#	2. database (combine pegging learning later)
#		tarball this for safety and transfer speed

# make a subdir for checkpoints
#	to avoid same-name collisions between concurrent processes
echo -n "Copying over the checkpoints and database files..."
mkdir -pv checkpoints/$name
cp -v $working_dir/checkpoints/* checkpoints/$name/

# copy over the 
mkdir -pv data/$name
cp -v $working_dir/data/* data/$name
echo "done."


# cleanup
echo "removing all leftover local files in $working_dir..."
rm -rv $working_dir
echo "done."


# get ready to "exit"
cd $old_dir
echo "Exiting"
#fi
