from __future__ import annotations

import time
from collections import deque

from PySide6.QtGui import QColor

from .config import DanmakuConfig
from .item import DanmakuItem, ItemPool
from .renderer import TextRenderer
from .track import TrackManager


class DanmakuEngine:
  def __init__(
    self,
    config: DanmakuConfig,
    renderer: TextRenderer,
    tracks: TrackManager,
    pool: ItemPool,
  ) -> None:
    self.cfg = config
    self.renderer = renderer
    self.tracks = tracks
    self.pool = pool

    self.items: list[DanmakuItem] = []
    self.pending: deque[tuple[str, str | None, int | None]] = deque()

    self._view_w = 0.0
    self._view_h = 0.0
    self._dpr = 1.0

  # ---------- 视图参数 ----------
  def set_viewport(self, width: float, height: float, dpr: float) -> None:
    self._view_w = float(width)
    self._view_h = float(height)
    self._dpr = float(dpr) or 1.0

  # ---------- 入队 / 立即发送 ----------
  def enqueue(
    self, text: str, color: str | None = None, size: int | None = None
  ) -> bool:
    text = (text or "").strip()
    if not text:
      return False
    if len(self.pending) >= self.cfg.pending_limit:
      return False
    self.pending.append((text, color, size))
    return True

  def send(self, text: str, color: str | None = None, size: int | None = None) -> bool:
    text = (text or "").strip()
    if not text:
      return False

    size = int(size or self.cfg.font_size)
    track = self.tracks.pick(self.items, self._view_w, self._view_h, self.cfg.coverage)
    if track is None:
      return False

    c = QColor(color) if color else QColor(255, 255, 255)
    pixmap, w, h, pad = self.renderer.build(
      text,
      size,
      self.cfg.font_family,
      c,
      self.cfg.shadow_enabled,
      self._dpr,
    )

    y = (
      self.cfg.top_margin
      + track * self.cfg.track_height
      + (self.cfg.track_height - h) / 2.0
    )
    item = self.pool.acquire()
    item.setup(pixmap, w, h, pad, self._view_w, y, track)
    self.items.append(item)
    return True

  # ---------- 生命周期 ----------
  def clear(self) -> None:
    for it in self.items:
      self.pool.release(it)
    self.items.clear()
    self.pending.clear()

  def prune(self, max_track: int) -> None:
    keep: list[DanmakuItem] = []
    for it in self.items:
      if it.track > max_track:
        self.pool.release(it)
      else:
        keep.append(it)
    self.items = keep

  # ---------- 帧推进 ----------
  def tick(self, dt: float) -> None:
    self._drain_pending()

    items = self.items
    if not items:
      return

    dx = self.cfg.speed * dt
    i = 0
    while i < len(items):
      it = items[i]
      it.x -= dx
      if it.x + it.w <= 0.0:
        self.pool.release(it)
        items[i] = items[-1]
        items.pop()
      else:
        i += 1

  def _drain_pending(self) -> None:
    if not self.pending:
      return
    start = time.perf_counter()
    n = 0
    while self.pending and n < self.cfg.spawn_max_per_tick:
      text, color, size = self.pending.popleft()
      self.send(text, color, size)
      n += 1
      if (time.perf_counter() - start) * 1000.0 >= self.cfg.spawn_budget_ms:
        break
