#!/bin/bash

round=1
games="11 12 13 14 15 3 4 5 6 7 8 9"


operation='single'
strategies={x,y,z}
agent_names={a,b}
date_string='something-likethis'
color='Greys'


checkpoints_base_dir='//'
images_base_dir='//'


for game in {11,15,3,4,5,6,7,8,9}; do # GAMES HERE

	date_start_string=`ls ./data/round$round/g$game/ | grep checkpoint | sed 's/_/ /g' | awk '{print \$3}' | uniq`

	echo $date_start_string

	for strategy in {hand_max_min,hand_max_avg,hand_max_med,hand_max_poss,crib_min_avg,pegging_max_avg_gained,pegging_max_med_gained,pegging_min_avg_given}; do

		for agent in {agent1,agent2}; do # AGENT NAMES HERE

			echo "Generating images for $agent : $strategy during $game"

			outdir_base="images/training/round$round/g$game"

			echo "    dealer:"
			mkdir -pv "$outdir_base/dealer/$strategy"
			./analyze.py $operation\
				--agent $agent\
				--date-str $date_start_string\
				--directory "data/round$round/g$game"\
				--output-dir "$outdir_base/dealer/$strategy"\
				--strategy $strategy

			echo "    pone:"
			mkdir -pv "$outdir_base/pone/$strategy"
			./analyze.py $operation\
				--agent $agent\
				--date-str $date_start_string\
				--directory "data/round$round/g$game"\
				--output-dir "$outdir_base/pone/$strategy"\
				--strategy $strategy\
				--pone
		done

	done

done
