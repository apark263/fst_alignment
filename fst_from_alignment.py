from absl import app
from absl import flags
import csv
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from itertools import filterfalse
import fst_builder_lib as flib


FLAGS = flags.FLAGS
flags.DEFINE_string('alignment', None, 'Aligment text.')
flags.DEFINE_string('output', None, 'where to write fst.')

@dataclass
class Frame:
  """Class for keeping track of frame properties."""
  phone: str = 'sil'
  index: int = 0
  am_cost: float = 0.0

  def __repr__(self):
    return f'{self.index} {self.phone} {self.am_cost:.05f}'

  @property
  def arc_spec(self):
    return (str(self.index), self.phone, self.am_cost)

@dataclass
class Segment:
  """Class for keeping track of segment properties."""
  phone: str = 'sil'
  start: int = 0
  end: int = 0
  am_cost: float = 0.0

  def __repr__(self):
    return f'{self.start}->{self.end} {self.phone}'

  @property
  def frames(self):
    frame_count = self.end - self.start + 1
    frame_cost = self.am_cost / frame_count
    frms = [
        Frame(self.phone, s, frame_cost) for s in range(self.start, self.end)
    ]
    return frms

@dataclass
class Alignment:
  """Class for encapsulating an alignment."""
  segments: Optional[List[Segment]] = None

  def __repr__(self):
    return '\n'.join([f'{s}' for s in self.segments])

  @staticmethod
  def FromFile(filename):
    segments = []
    with open(filename) as f:
      for line in f.readlines():
        r = line.split()
        segments.append(Segment(r[0], int(r[1]), int(r[2]), float(r[3])))
    return Alignment(segments)

  def to_fst(self):
    fst = flib.Fst()
    seg_count = len(self.segments)
    curstate = 0
    for seg in self.segments:
      for frame in seg.frames:
        fst.AddArc(flib.Arc(curstate, curstate + 1, *frame.arc_spec))
        curstate += 1
    fst.AddEndState(curstate)
    return fst


def main(argv):
  del argv    # Unused
  phrases = Alignment.FromFile(FLAGS.alignment)
  phrases.to_fst().to_file(FLAGS.output)

if __name__ == '__main__':
  app.run(main)