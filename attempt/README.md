
python3 make_pronlex.py

fstunion unk.fst x.fst - | fstclosure - pronlex.fst
fstarcsort grammar.fst | fstcompose - pronlex.fst | fstrmepsilon - composed.fst

fstproject --project_type=output composed.fst | fstrmepsilon - | fstprint

d d a b c d d d

d: <blank>

```bash
fstclosure x.fst pronlex.fst
fstarcsort grammar.fst | fstcompose - pronlex.fst | fstproject --project_type=output | fstrmepsilon - phrase_phone.fst

fstconcat entry.fst phrase_phone.fst pp2.fst
fstunion unk.fst pp2.fst pp3.fst
fstclosure pp3.fst | fstrmepsilon | fstarcsort - final.fst

```
fstdraw -portrait - | \
    dot -Tpdf > a.pdf

g u @ <sil> h aet h eI <sil> g u g @ l h h <sil> oU
