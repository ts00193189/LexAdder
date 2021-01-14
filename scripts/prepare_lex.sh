#!/bin/bash

kaldi_s5=/home/denis/kaldi/egs/lexbuild/s5

cp ./lexicon.txt $kaldi_s5/lex/lexicon.txt
cd $kaldi_s5
local/prepare_dict.sh || exit 1;

