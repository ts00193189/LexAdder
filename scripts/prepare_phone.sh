#!/bin/bash

kaldi_s5=/home/denis/kaldi/egs/lexbuild/s5
cd $kaldi_s5

   # Phone Sets, questions, L compilation
  echo "$0: Phone Sets, questions, L compilation Preparation"
  rm -rf data/lang
  utils/prepare_lang.sh --position-dependent-phones false data/local/dict \
     "<SIL>" data/local/lang data/lang || exit 1;

