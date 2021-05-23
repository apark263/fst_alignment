# Alignment experiments

## Installation
First had to install `openfst` from [here](http://www.openfst.org/twiki/bin/view/FST/FstDownload).

Then:

    make -j 8 && sudo make install

## Candidate phrases

Create a list of candidate acceptor phrases into `wake_phrases.list`.

```sh
isym=vocab.list
osym=wake_phrases.list

python3 fst_builder_lib.py --phrases wake_phrases.list | \
    fstcompile --isymbols=${isym} --osymbols=${osym} | \
    fstrmepsilon | fstdeterminize | fstminimize > hw_opt.fst

fstdraw --isymbols=${isym} --osymbols=${osym} -portrait | dot -Tpdf > tmp2.pdf
```

Create carrier sentence fst.

