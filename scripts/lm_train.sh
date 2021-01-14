#!/bin/bash

kaldi_s5=/home/denis/kaldi/egs/lexbuild/s5
cd $kaldi_s5

# LM training
  echo "$0: LM training"
  rm -rf data/local/lm/3gram-mincount
  local/train_lms.sh || exit 1;
