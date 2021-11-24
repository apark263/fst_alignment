from absl import app
from absl import flags
import csv
from typing import Callable, Dict, List, Optional
import pywrapfst as fst

EPS = '<eps>'
SIL = '<sil>'
UNK = '<unk>'

SAMPLE_PHRASE = 'g u @ <sil> h ae t h eI g u g @ l h h <sil> oU'

FLAGS = flags.FLAGS
flags.DEFINE_string('prons', 'prons.lex', 'List of phrases file.')


def invalid_symbol(symbol: str) -> bool:
  return symbol in [EPS, SIL, UNK]


def DefaultFst(isyms: fst.SymbolTable, osyms: fst.SymbolTable) -> fst.VectorFst:
  f = fst.VectorFst()
  one = fst.Weight.one(f.weight_type())
  f.set_input_symbols(isyms)
  f.set_output_symbols(osyms)
  s = f.add_state()
  f.set_start(s)
  return f, one


class PronLex:
  def __init__(self, pron_file: str, isymbols: str, osymbols: str):
    self.isyms = fst.SymbolTable.read_text(isymbols)
    self.osyms = fst.SymbolTable.read_text(osymbols)
    self.pron_dict = {}

    with open(pron_file, newline='') as csvfile:
      row_reader = csv.reader(csvfile, delimiter=' ')
      for r in row_reader:
        self.pron_dict.setdefault(r[0], []).append(r[1:])

  def _MakePron(self, word: str, pron: List[str]) -> fst.VectorFst:
    f, wt = DefaultFst(self.isyms, self.osyms)
    f.add_states(len(pron))
    for ns, phone in enumerate(pron):
      insym = self.isyms.find(word) if ns == 0 else 0
      f.add_arc(ns, fst.Arc(insym, self.osyms.find(phone), wt, ns+1))
    f.set_final(len(pron))
    return f

  def CreateFst(self):
    fst_list = []
    for word in self.pron_dict.keys():
      for pron in self.pron_dict[word]:
        fst_list.append(self._MakePron(word, pron))
    combined = fst_list[0].union(*fst_list[1:])
    combined.rmepsilon()
    return combined
    
def MakeGrammar(syms):
  c = fst.Compiler(isymbols=syms,
                   osymbols=syms,
                   keep_isymbols=True,
                   keep_osymbols=True)
  c.write(f'0 1 {EPS} {EPS} -1.0')
  c.write('1 2 hey hey')
  c.write('1 2 okay okay')
  c.write(f'2 2 {SIL} {SIL}')
  c.write('2 3 google google')
  c.write('3')
  return c.compile()


def MakeFlower(syms):
  f, wt = DefaultFst(syms, syms)
  s = f.start()
  for idx, _ in syms:
    if idx != 0:
      f.add_arc(s, fst.Arc(idx, syms.find(SIL), wt, s))
  f.set_final(s, wt)
  return f

def MakeLinear(syms, sentence):
  f, wt = DefaultFst(syms, syms)
  f.add_states(len(sentence))
  for s, phn in enumerate(sentence):
    f.add_arc(s, fst.Arc(syms.find(phn), 0, wt, s + 1))
  f.set_final(len(sentence))
  f.project('input')
  return f


def PhoneSymTable(filename='phones.sym'):
  return fst.SymbolTable.read_text(filename)


def VocabSymTable(filename='vocab.sym'):
  return fst.SymbolTable.read_text(filename)


def main(argv):
  del argv    # Unused
  phone = PhoneSymTable()
  vocab = VocabSymTable()

  # This creates the hotword acceptor grammar
  g = MakeGrammar(vocab)
  g.arcsort()

  # This creates the pronunciation expansions for the grammar
  x = PronLex('prons.lex', osymbols='phones.sym', isymbols='vocab.sym')
  pfst = x.CreateFst()
  pfst.closure()

  # Compose with the grammar to get the phrase -> prons
  newfst = fst.compose(g, pfst)
  newfst.project('output').rmepsilon()
  newfst.write('pronlex.fst')

  ## This is the final acceptor
  unk = MakeFlower(phone)
  acceptor = unk.union(newfst).closure()

  # Create the input as a linear FST
  input_sent = MakeLinear(phone, SAMPLE_PHRASE.split())

  # Now get the output
  result = fst.compose(input_sent, acceptor).rmepsilon()
  output = fst.shortestpath(result).topsort()
  output.write('output.fst')

  a = list(output.arcs(output.start()))
  out_seq = []
  while a:
    arc = a.pop(0)
    out_seq.append(phone.find(arc.olabel))
    a = list(output.arcs(arc.nextstate))
  print(out_seq)


if __name__ == '__main__':
  app.run(main)