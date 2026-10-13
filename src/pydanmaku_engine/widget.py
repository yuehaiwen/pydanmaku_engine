from __future__ import annotations

from PySide6.QtCore import QElapsedTimer, QPointF, Qt, QTimer
from PySide6.QtGui import (
  QColor,
  QHideEvent,
  QLinearGradient,
  QPainter,
  QPaintEvent,
  QPixmap,
  QResizeEvent,
  QShowEvent,
)
from PySide6.QtWidgets import QWidget

from .config import DanmakuConfig
from .engine import DanmakuEngine
from .glyph_cache import GlyphCache
from .item import ItemPool
from .renderer import TextRenderer
from .track import TrackManager


class DanmakuWidget(QWidget):
  def __init__(
    self, config: DanmakuConfig | None = None, parent: QWidget | None = None
  ) -> None:
    super().__init__(parent)
    self.cfg = config or DanmakuConfig()
    self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
    self.setMinimumSize(480, 240)

    # 组件
    self._glyphs = GlyphCache(self.cfg.glyph_limit)
    self._renderer = TextRenderer(self._glyphs)
    self._tracks = TrackManager(self.cfg)
    self._pool = ItemPool(self.cfg.pool_limit)
    self._engine = DanmakuEngine(self.cfg, self._renderer, self._tracks, self._pool)

    # 背景
    self._bg_pixmap: QPixmap | None = None
    self._bg_top = QColor(self.cfg.bg_top)
    self._bg_bottom = QColor(self.cfg.bg_bottom)

    # 时钟 / 定时器
    self._clock = QElapsedTimer()
    self._clock.start()
    self._timer = QTimer(self)
    self._timer.setTimerType(Qt.TimerType.PreciseTimer)
    self._apply_fps()
    self._timer.timeout.connect(self._on_tick)
    self._timer.start()

  # ---------- 对外 API ----------
  def set_fps(self, fps: int) -> None:
    fps = max(10, min(500, int(fps)))
    if fps == self.cfg.fps:
      return
    self.cfg.fps = fps
    self._apply_fps()

  def set_speed(self, px_per_sec: float) -> None:
    self.cfg.speed = max(20.0, float(px_per_sec))

  def set_coverage(self, ratio: float) -> None:
    ratio = max(0.1, min(1.0, float(ratio)))
    if abs(ratio - self.cfg.coverage) < 1e-9:
      return
    self.cfg.coverage = ratio
    self._engine.prune(self._tracks.count(self.height(), self.cfg.coverage) - 1)
    self.update()

  def set_font(self, family: str | None = None, size: int | None = None) -> None:
    changed = False
    if family and family != self.cfg.font_family:
      self.cfg.font_family = family
      changed = True
    if size and int(size) != self.cfg.font_size:
      self.cfg.font_size = int(size)
      changed = True
    if changed:
      self._glyphs.clear()
      self.update()

  def set_shadow_enabled(self, enabled: bool) -> None:
    enabled = bool(enabled)
    if enabled != self.cfg.shadow_enabled:
      self.cfg.shadow_enabled = enabled
      self._glyphs.clear()
      self.update()

  def set_background(self, top: str, bottom: str) -> None:
    self._bg_top = QColor(top)
    self._bg_bottom = QColor(bottom)
    self._bg_pixmap = None
    self.update()

  def enqueue(
    self, text: str, color: str | None = None, size: int | None = None
  ) -> bool:
    return self._engine.enqueue(text, color, size)

  def send(
    self, text: str, color: str | None = None, font_size: int | None = None
  ) -> bool:
    self._sync_viewport()
    return self._engine.send(text, color, font_size)

  def clear(self) -> None:
    self._engine.clear()
    self.update()

  # ---------- 内部：视图同步 ----------
  def _sync_viewport(self) -> None:
    self._engine.set_viewport(
      self.width(),
      self.height(),
      self.devicePixelRatioF() or 1.0,
    )

  def _apply_fps(self) -> None:
    self._timer.setInterval(max(1, round(1000.0 / self.cfg.fps)))
    self._max_dt = min(0.1, 4.0 / self.cfg.fps)
    self._last_ms = self._clock.elapsed()

  # ---------- 帧回调 ----------
  def _on_tick(self) -> None:
    now = self._clock.elapsed()
    dt = (now - self._last_ms) / 1000.0
    self._last_ms = now
    if dt <= 0.0:
      return
    dt = min(dt, self._max_dt)

    prev_count = len(self._engine.items)
    self._engine.tick(dt)
    if prev_count or self._engine.items:
      self.update()

  # ---------- 背景 ----------
  def _ensure_bg(self) -> QPixmap:
    dpr = self.devicePixelRatioF() or 1.0
    pm_w = int(self.width() * dpr + 0.5)
    pm_h = int(self.height() * dpr + 0.5)
    pm = self._bg_pixmap
    if pm is not None and pm.width() == pm_w and pm.height() == pm_h:
      return pm

    pm = QPixmap(pm_w, pm_h)
    pm.setDevicePixelRatio(dpr)
    p = QPainter(pm)
    grad = QLinearGradient(0, 0, 0, self.height())
    grad.setColorAt(0.0, self._bg_top)
    grad.setColorAt(1.0, self._bg_bottom)
    p.fillRect(0, 0, self.width(), self.height(), grad)
    p.end()
    self._bg_pixmap = pm
    return pm

  # ---------- 绘制 ----------
  def paintEvent(self, event: QPaintEvent) -> None:
    p = QPainter(self)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
    p.drawPixmap(0, 0, self._ensure_bg())

    for it in self._engine.items:
      if it.pixmap is not None:
        p.drawPixmap(QPointF(it.x - it.pad, it.y - it.pad), it.pixmap)

  # ---------- Qt 事件 ----------
  def resizeEvent(self, event: QResizeEvent) -> None:
    super().resizeEvent(event)
    self._bg_pixmap = None
    self._sync_viewport()
    self._engine.prune(self._tracks.count(self.height(), self.cfg.coverage) - 1)

  def showEvent(self, event: QShowEvent) -> None:
    super().showEvent(event)
    self._last_ms = self._clock.elapsed()
    self._sync_viewport()
    self._timer.start()

  def hideEvent(self, event: QHideEvent) -> None:
    self._timer.stop()
    super().hideEvent(event)
