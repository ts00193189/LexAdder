#!/bin/bash
kaldi_s5=/home/denis/kaldi/egs/lexbuild/s5
cd $kaldi_s5
# G compilation, check LG composition
  echo "$0: G compilation, check LG composition"
  utils/format_lm.sh data/lang data/local/lm/3gram-mincount/lm_unpruned.gz \
      data/local/dict/lexicon.txt data/lang_test || exit 1;
