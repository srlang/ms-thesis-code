#!/bin/bash

for i in {0..9}; do

node=$(expr $i + 7)

cat >"self_$i.job" <<EOF
#!/bin/bash
#SBATCH --job-name=self_tourny_$i
#SBATCH -o self_tourny_$i.out
#SBATCH -p long
#SBATCH -c 2
#SBATCH -t 14-00:00:00
#SBATCH --mem-per-cpu=2048
#SBATCH --mail-type=ALL
#SBATCH --constraint=tmp
#SBATCH --gres=tmp:25G
#SBATCH --nodelist=kas`printf %02d $node`

name="self_tourny_$i"

srun ~/longtourny/shells/selftourny.sh \$name

EOF

done
