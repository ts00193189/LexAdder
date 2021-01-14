#!/bin/bash
kaldi_s5=/home/denis/kaldi/egs/lexbuild/s5
chain=chain/tdnnf_1b_sp
cd $kaldi_s5
utils/mkgraph.sh --self-loop-scale 1.0 data/lang_test $chain $chain/graph
