from collections import OrderedDict

from PySide6.QtCore import Qt
from PySide6.QtGui import (
  QColor,
  QFont,
  QFontMetricsF,
  QPainter,
  QPainterPath,
  QPen,
  QPixmap,
)

GlyphEntry = tuple[QPixmap, float, int]  # (pixmap, advance, pad)


class GlyphCache:
  def __init__(self, limit: int) -> None:
    self._limit = limit
    self._cache: OrderedDict[tuple, GlyphEntry] = OrderedDict()

  def clear(self) -> None:
    self._cache.clear()

  def get(
    self,
    ch: str,
    size: int,
    family: str,
    color: QColor,
    shadow: bool,
    dpr: float,
  ) -> GlyphEntry:
    key = (ch, size, family, color.rgba(), shadow, dpr)
    entry = self._cache.get(key)
    if entry is not None:
      self._cache.move_to_end(key)
      return entry

    entry = self._render_glyph(ch, size, family, color, shadow, dpr)
    self._cache[key] = entry
    if len(self._cache) > self._limit:
      self._cache.popitem(last=False)
    return entry

  @staticmethod
  def _render_glyph(
    ch: str,
    size: int,
    family: str,
    color: QColor,
    shadow: bool,
    dpr: float,
  ) -> GlyphEntry:
    font = QFont(family, size)
    font.setBold(True)
    fm = QFontMetricsF(font)

    path = QPainterPath()
    path.addText(0.0, fm.ascent(), font, ch)

    stroke_width = max(2.0, size / 7.0)
    pen = QPen(QColor(0, 0, 0, 205), stroke_width)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    advance = fm.horizontalAdvance(ch)
    h = fm.height()
    pad = int(stroke_width + 3)

    pm_w = int((advance + pad * 2) * dpr + 0.5)
    pm_h = int((h + pad * 2) * dpr + 0.5)

    pixmap = QPixmap(pm_w, pm_h)
    pixmap.setDevicePixelRatio(dpr)
    pixmap.fill(Qt.GlobalColor.transparent)

    pp = QPainter(pixmap)
    pp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pp.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    pp.translate(pad, pad)

    if shadow:
      off = max(1.0, stroke_width * 0.45)
      pp.translate(off, off)
      pp.fillPath(path, QColor(0, 0, 0, 130))
      pp.translate(-off, -off)

    pp.strokePath(path, pen)
    pp.fillPath(path, color)
    pp.end()

    return pixmap, advance, pad
