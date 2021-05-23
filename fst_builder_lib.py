from absl import app
from absl import flags
from dataclasses import dataclass
from typing import List, Optional
from itertools import filterfalse

EPS = '<epsilon>'
SIL = '<silence>'

FLAGS = flags.FLAGS
flags.DEFINE_string('phrases', None, 'List of phrases file.')


def invalid_symbol(symbol: str) -> bool:
  return symbol in [EPS, SIL]


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
    return f'{self.istate} {self.ostate} {self.isym} {self.osym} {wt}'


@dataclass
class Fst:
  arcs: List[Arc]
  end_states: List[int]

  def AddArc(self, other: Arc):
    self.arcs.append(other)

  def AddEndState(self, other: int):
    self.end_states.append(other)

  def __repr__(self):
    strs = [f'{a}' for a in self.arcs]
    strs += [f'{e}' for e in self.end_states]
    return '\n'.join(strs)


def phrase_to_arcs(phrase: str, start: int = 0) -> List[Arc]:
  result = []
  result = Fst()
  for idx, word in enumerate(phrase.split(), start=start):
    result.append(Arc(idx, idx + 1, word, word))
    result.append(Arc(idx, idx, SIL, EPS))
  return result


def phrases_to_fst(phrases: List[str]) -> Fst:
  result = Fst([], [])
  offset = 0
  phrase_stack = []
  phrases = [l.split()[0] for l in phrases]
  for phrase in filterfalse(invalid_symbol, phrases):
    phrase_words = phrase.split('_')
    result.AddArc(Arc(0, offset + 1, phrase_words[0], phrase))
    for idx, word in enumerate(phrase_words[1:], start=offset + 1):
      result.AddArc(Arc(idx, idx + 1, word, EPS))
      result.AddArc(Arc(idx, idx, SIL, EPS))
    offset += len(phrase_words)
    phrase_stack.append(offset)
  for idx in phrase_stack:
    result.AddArc(Arc(idx, offset, EPS, EPS))
  result.AddEndState(offset)
  return result


def vocab_fst(lines):
  result = Fst([], [])
  offset = 0
  words = [l.split()[0] for l in lines]
  for word in filterfalse(invalid_symbol, words):
    result.AddArc(Arc(0, offset + 1, word[0], word))
    for i, letter in enumerate(word[1:], start=offset + 1):
      result.AddArc(Arc(i, i + 1, letter, EPS))
    offset += len(word)
    result.AddEndState(offset)
  return result


def symbol_table(symbols: List[str]) -> List[str]:
  result = [f'{EPS} 0', f'{SIL} 1']
  for idx, sym in enumerate(symbols, start=2):
    result.append(f'{sym} {idx}')
  return result


def writelines(filename: str, lines: List[str]):
  with open(filename, 'wt') as f:
    f.writelines(lines)


def readlines(filename: str) -> List[str]:
  with open(filename, 'rt') as f:
    return f.readlines()


def main(argv):
  del argv  # Unused
  phrases = readlines(FLAGS.phrases)
  print(phrases_to_fst(phrases))
  # vocab = set(' '.join(phrases).split())
  # writelines('isyms.txt', '\n'.join(symbol_table(vocab)))
  # x = vocab_fst(symbol_table(vocab))
  # print(x)


if __name__ == '__main__':
  app.run(main)