from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPixmap

from .glyph_cache import GlyphCache


class TextRenderer:
  def __init__(self, glyphs: GlyphCache) -> None:
    self._glyphs = glyphs

  def build(
    self,
    text: str,
    size: int,
    family: str,
    color: QColor,
    shadow: bool,
    dpr: float,
  ) -> tuple[QPixmap, float, float, int]:
    font = QFont(family, size)
    font.setBold(True)
    fm = QFontMetricsF(font)

    entries = [self._glyphs.get(ch, size, family, color, shadow, dpr) for ch in text]
    total_advance = sum(adv for _, adv, _ in entries)

    h = fm.height()
    pad = entries[0][2]

    pm_w = int((total_advance + pad * 2) * dpr + 0.5)
    pm_h = int((h + pad * 2) * dpr + 0.5)

    pixmap = QPixmap(pm_w, pm_h)
    pixmap.setDevicePixelRatio(dpr)
    pixmap.fill(Qt.GlobalColor.transparent)

    pp = QPainter(pixmap)
    pp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
    x = float(pad)
    for glyph_pm, adv, gpad in entries:
      pp.drawPixmap(QPointF(x - gpad, pad), glyph_pm)
      x += adv
    pp.end()
    return pixmap, total_advance, h, pad
