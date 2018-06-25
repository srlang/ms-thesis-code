#!/bin/bash

home_dir="~/decay/outputs/"

operation="single"

cd $home_dir
module load Python/3.5.2-foss-2016b
source ./venv/bin/activate

#for game in {0..7} ; do #0 3 4 8 9 10 11 12 ; do # GAMES HERE
for rate in 0.00 0.05 0.10 0.15 0.25 0.50 ; do #  0.00 0.02 0.05 0.07 0.10 0.15 0.25 0.50 ; do

	indir="checkpoints/decay_${rate}-11"
	date_start_string=`ls $indir | grep checkpoint | sed 's/_/ /g' | awk '{print \$3}' | uniq | head -n 1`

	echo "date_string: $date_start_string"

	for strategy in {hand_max_min,hand_max_avg,hand_max_med,hand_max_poss,crib_min_avg,pegging_max_avg_gained,pegging_max_med_gained,pegging_min_avg_given}; do

		for agent in {agent1,agent2}; do # AGENT NAMES HERE

			echo "Generating images for $agent : $strategy during $game"

			outdir_base="images/decay_${rate}-11"
			#indir_base="checkpoints/lr_$rate"

			echo "    dealer:"
			mkdir -pv "$outdir_base/dealer/$strategy"
			./analyze.py $operation\
				--agent $agent\
				--date-str $date_start_string\
				--directory "$indir"\
				--output-dir "$outdir_base/dealer/$strategy"\
				--strategy $strategy

			echo "    pone:"
			mkdir -pv "$outdir_base/pone/$strategy"
			./analyze.py $operation\
				--agent $agent\
				--date-str $date_start_string\
				--directory "$indir"\
				--output-dir "$outdir_base/pone/$strategy"\
				--strategy $strategy\
				--pone
		done

	done

done

deactivate
cd
