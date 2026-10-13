import random

from .config import DanmakuConfig
from .item import DanmakuItem


class TrackManager:
  def __init__(self, config: DanmakuConfig) -> None:
    self.cfg = config

  def count(self, height: float, coverage: float) -> int:
    usable = height * coverage - self.cfg.top_margin
    return max(1, int(usable // self.cfg.track_height))

  def pick(
    self,
    items: list[DanmakuItem],
    width: float,
    height: float,
    coverage: float,
  ) -> int | None:
    n = self.count(height, coverage)
    right_edge = width - self.cfg.gap
    occupied = [False] * n
    for it in items:
      t = it.track
      if 0 <= t < n and it.x + it.w > right_edge:
        occupied[t] = True
    free = [i for i in range(n) if not occupied[i]]
    if not free:
      return None
    return random.choice(free)
