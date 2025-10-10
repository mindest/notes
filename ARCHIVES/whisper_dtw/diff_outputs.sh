#!/bin/bash

audio=${1:-"audios/1.flac"}

set -x

python ref.py -a $audio
python bmk.py -n 1 -b 1 -a $audio
diff output_ref.txt output_ort.txt -U 1000 --color=always
