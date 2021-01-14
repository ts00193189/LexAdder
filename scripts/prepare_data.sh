#!/bin/bash

kaldi_s5=/home/denis/kaldi/egs/lexbuild/s5
text_corpus=$kaldi_s5/text_corpus

  cd $kaldi_s5
  rm -rf data/local/train/others data/local/train/text data/local/train/text_src
  local/prepare_data.sh || exit 1;
  cp data/local/train/text data/local/train/text_src
  rm -rf data/local/train/others data/local/train/text
  for x in part00 part01 part02 part03 part04 part05 part06 part07 part08 part10 part11; do
    cat $text_corpus/$x/*.txt | dos2unix >> data/local/train/others || exit 1;
  done
  cat data/local/train/text_src > data/local/train/text
  cat data/local/train/others >> data/local/train/text


