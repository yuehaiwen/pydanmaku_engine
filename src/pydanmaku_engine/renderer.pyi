from PySide6.QtGui import QColor, QPixmap

from .glyph_cache import GlyphCache as GlyphCache

class TextRenderer:
  def __init__(self, glyphs: GlyphCache) -> None: ...
  def build(
    self, text: str, size: int, family: str, color: QColor, shadow: bool, dpr: float
  ) -> tuple[QPixmap, float, float, int]: ...
