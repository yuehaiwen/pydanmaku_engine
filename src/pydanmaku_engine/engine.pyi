from collections import deque

from _typeshed import Incomplete

from .config import DanmakuConfig as DanmakuConfig
from .item import DanmakuItem as DanmakuItem
from .item import ItemPool as ItemPool
from .renderer import TextRenderer as TextRenderer
from .track import TrackManager as TrackManager

class DanmakuEngine:
  cfg: Incomplete
  renderer: Incomplete
  tracks: Incomplete
  pool: Incomplete
  items: list[DanmakuItem]
  pending: deque[tuple[str, str | None, int | None]]
  def __init__(
    self,
    config: DanmakuConfig,
    renderer: TextRenderer,
    tracks: TrackManager,
    pool: ItemPool,
  ) -> None: ...
  def set_viewport(self, width: float, height: float, dpr: float) -> None: ...
  def enqueue(
    self, text: str, color: str | None = None, size: int | None = None
  ) -> bool: ...
  def send(
    self, text: str, color: str | None = None, size: int | None = None
  ) -> bool: ...
  def clear(self) -> None: ...
  def prune(self, max_track: int) -> None: ...
  def tick(self, dt: float) -> None: ...
