## How to create prefix fst

```sh
for i in any prefix google; do
    fstcompile \
        --isymbols=phones.syms --keep_isymbols=true \
        ${i}.fst.txt ${i}.fst
done

fstconcat any.fst prefix.fst | \
    fstconcat - google.fst | \
    fstconcat - any.fst | \
    fstrmepsilon | fstclosure - acceptor.fst

python3 ../fst_from_alignment.py \
    --alignment phone_align_sample.txt \
    --output phone_align.fst.txt

fstcompile --osymbols=phones.syms --keep_osymbols=true \
    phone_align.fst.txt phone_align.fst

fstcompose phone_align.fst acceptor.fst  | fstshortestpath - | fstprint > b.txt

```

## make the acceptor

```
fstcompose sent.fst acceptor.fst | \
    fstproject --project_type=output | \
    fstrmepsilon | \
    fstdraw -portrait - | \
    dot -Tpdf > a.pdf

fstcompose badsent.fst acceptor.fst | \
    fstproject --project_type=output | \
    fstrmepsilon | \
    fstdraw -portrait - | \
    dot -Tpdf > a.pdf

```

x x x h eI sil



