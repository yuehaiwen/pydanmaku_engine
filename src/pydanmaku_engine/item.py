from PySide6.QtGui import QPixmap


class DanmakuItem:
  __slots__ = ("h", "pad", "pixmap", "track", "w", "x", "y")

  def __init__(self) -> None:
    self.pixmap: QPixmap | None = None
    self.w = 0.0
    self.h = 0.0
    self.pad = 0
    self.x = 0.0
    self.y = 0.0
    self.track = 0

  def setup(self, pixmap, w, h, pad, x, y, track) -> None:
    self.pixmap = pixmap
    self.w = w
    self.h = h
    self.pad = pad
    self.x = x
    self.y = y
    self.track = track

  def release(self) -> None:
    self.pixmap = None
    self.w = 0.0
    self.h = 0.0
    self.pad = 0
    self.x = 0.0
    self.y = 0.0
    self.track = 0


class ItemPool:
  def __init__(self, limit: int) -> None:
    self._limit = limit
    self._items: list[DanmakuItem] = []

  def acquire(self) -> DanmakuItem:
    return self._items.pop() if self._items else DanmakuItem()

  def release(self, item: DanmakuItem) -> None:
    item.release()
    if len(self._items) < self._limit:
      self._items.append(item)

  def clear(self) -> None:
    self._items.clear()
