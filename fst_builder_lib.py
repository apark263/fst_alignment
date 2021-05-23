from absl import app
from absl import flags
from dataclasses import dataclass
from typing import List, Optional

EPS = '<epsilon>'
SIL = '<silence>'

FLAGS = flags.FLAGS
flags.DEFINE_string('phrases', None, 'List of phrases file.')

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
  end_state: int = 0

  def __add__(self, other: Arc):
    arcs = self.arcs
    end_state = max(self.end_state, other.istate, other.ostate)
    return Fst(arcs=arcs, end_state=end_state)


def phrase_to_arcs(phrase: str, start: int = 0) -> List[Arc]:
  result = []
  result = Fst()
  for idx, word in enumerate(phrase.split(), start=start):
    result.append(Arc(idx, idx + 1, word, word))
    result.append(Arc(idx, idx, SIL, EPS))
  return result

def phrases_to_fst(phrases: List[str]) -> Fst:
  result = Fst()
  for phrase in phrases:
    for idx, word in enumerate(phrase.split()):
      result += Arc(idx, idx + 1, word, word)
      result += Arc(idx, idx, SIL, EPS)

    result.append(Arc(idx, idx + 1, word, word))
    result.append(Arc(idx, idx, SIL, EPS))
  return result

def vocab_fst(lines):
  s = 0
  for line in lines:
    word, state = line.split()
    if word in [EPS, SIL]:
      continue  # epsilon
    for i, l in enumerate(word):
      if i == 0:
        print(f'0 {s + 1} {l} {word}')
      else:
        s += 1
        print(f'{s} {s + 1} {l} {EPS}')
    s += 1
    print(f'{s}')

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
  vocab = set(' '.join(phrases).split())
  writelines('isyms.txt', '\n'.join(symbol_table(vocab)))
  vocab_fst(symbol_table(vocab))


if __name__ == '__main__':
  app.run(main)