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


fstcompile --isymbols=a_i --osymbols=g_i --keep_isymbols=1 --keep_osymbols=1 pos.txt.fst | fstdraw -portrait | dot -Tpng > pos.png
fstcompile --isymbols=a_i --osymbols=g_i --keep_isymbols=1 --keep_osymbols=1 neg.txt.fst | fstdraw -portrait | dot -Tpng > neg.png

fstunion neg.cfst pos.cfst | fstclosure - both.cfst

fstcompile --isymbols=a_i --osymbols=a_i  tale.txt - | fstproject - tale.cfst

