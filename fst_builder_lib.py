from absl import app
from absl import flags
import csv
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from itertools import filterfalse

EPS = '<epsilon>'
SIL = '<silence>'
UNK = '<unknown>'

FLAGS = flags.FLAGS
flags.DEFINE_string('phrases', None, 'List of phrases file.')
flags.DEFINE_string('sentence', None, 'Sentence string.')


def invalid_symbol(symbol: str) -> bool:
  return symbol in [EPS, SIL, UNK]


@dataclass
class SymbolTable:
  states: Dict[str, int]

  def __repr__(self):
    return '\n'.join([f'{a} {b}' for a, b in self.states])

  def as_gen(self):
    return sorted(self.states, key=lambda x: x[1])

  @staticmethod
  def FromFile(filename):
    with open(filename, newline='') as csvfile:
      row_reader = csv.reader(csvfile, delimiter=' ')
      return SymbolTable({r[0]: int(r[1]) for r in row_reader})

  def ToFile(self, filename):
    with open(filename, newline='', mode='wt') as csvfile:
      row_writer = csv.writer(csvfile, delimiter=' ')
      for k, v in self.states.items():
        row_writer.writerow([k, v])


@dataclass
class Arc:
  """Class for encapsulating an FST arc."""
  istate: int
  ostate: int
  isym: str = EPS
  osym: str = EPS
  weight: Optional[float] = None

  def __repr__(self):
    wt = self.weight or ''
    return f'{self.istate} {self.ostate} {self.isym} {self.osym} {wt:.05f}'


@dataclass
class Fst:
  """Class for encapsulating an FST."""
  arcs: Optional[List[Arc]] = None
  end_states: Optional[List[int]] = None

  def AddArc(self, other: Arc):
    if not self.arcs:
      self.arcs = [other]
    else:
      self.arcs.append(other)

  def AddEndState(self, other: int):
    if not self.end_states:
      self.end_states = [other]
    else:
      self.end_states.append(other)

  def __repr__(self):
    strs = [f'{a}' for a in self.arcs]
    strs += [f'{e}' for e in self.end_states]
    return '\n'.join(strs)

  def to_file(self, filename: str):
    with open(filename, 'w') as f:
      f.write(str(self))

  @staticmethod
  def FromSentence(sentence: str):
    """Makes a linear fst (words -> words) out of a sequence of words."""
    result = Fst()
    words = sentence.split()
    for idx, word in enumerate(words):
      result.AddArc(Arc(idx, idx + 1, word, word))
    result.AddEndState(len(words))
    return result

  @staticmethod
  def MultiPathFst(paths: SymbolTable,
                   splitter: Callable,
                   allow_inserts: bool = True):
    """Makes a multi-path fst (words -> phrases) given a set of phrases."""
    result = Fst()
    offset = 0
    path_stack = []
    for path in filterfalse(invalid_symbol, paths.as_gen()):
      tokens = splitter(path)
      result.AddArc(Arc(0, offset + 1, tokens[0], path))
      for idx, word in enumerate(tokens[1:], start=offset + 1):
        result.AddArc(Arc(idx, idx + 1, word, EPS))
        if allow_inserts:
          result.AddArc(Arc(idx, idx, SIL, EPS))
      offset += len(tokens)
      path_stack.append(offset)
    for idx in path_stack:
      result.AddArc(Arc(idx, offset, EPS, EPS))
    result.AddEndState(offset)
    return result

  @staticmethod
  def FromPhrases(phrases: SymbolTable):
    return Fst.MultiPathFst(phrases, lambda x: x.split('_'))

  @staticmethod
  def FromWords(words: SymbolTable):
    return Fst.MultiPathFst(words, lambda x: list(x), False)


class PhraseAcceptor:

  def __init__(self, phrases: SymbolTable):
    self._ParsePhrases(phrases)

  def _ParsePhrases(self, phrases: SymbolTable):
    self.fst = Fst.FromPhrases(phrases)
    vocab = set([EPS, UNK, SIL])
    phrases = [l.split()[0] for l in phrases.as_gen()]
    for phrase in filterfalse(invalid_symbol, phrases):
      vocab.update(phrase.split('_'))
    self.phrases = SymbolTable({p: s for s, p in enumerate(phrases)})
    self.vocab = SymbolTable({w: s for s, w in enumerate(vocab)})

  @property
  def input_symbols(self):
    return self.vocab

  @property
  def output_symbols(self):
    return self.phrases

  def filter_sentence(self, sentence: str) -> str:
    """Rewrites a sentence by removing unknown words."""
    words = sentence.split()
    for idx, word in enumerate(words):
      if word not in self.vocab:
        words[idx] = UNK
    return ' '.join(words)


def main(argv):
  del argv    # Unused
  phrases = SymbolTable.FromFile(FLAGS.phrases)
  hw_accept = PhraseAcceptor(phrases)
  hw_accept.input_symbols.ToFile('isyms.list')
  hw_accept.output_symbols.ToFile('osyms.list')


if __name__ == '__main__':
  app.run(main)