from _typeshed import Incomplete

from .config import DanmakuConfig as DanmakuConfig
from .item import DanmakuItem as DanmakuItem

class TrackManager:
  cfg: Incomplete
  def __init__(self, config: DanmakuConfig) -> None: ...
  def count(self, height: float, coverage: float) -> int: ...
  def pick(
    self, items: list[DanmakuItem], width: float, height: float, coverage: float
  ) -> int | None: ...
