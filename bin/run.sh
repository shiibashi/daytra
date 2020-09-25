#!bin/sh

export MODE=FORECAST
dir_name=$(cd $(dirname $0); pwd)
cd $dir_name

shopt -s expand_aliases
source ~/.bashrc

cd ../script

python train.py \
  --mode dev
