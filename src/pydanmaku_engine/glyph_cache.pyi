from PySide6.QtGui import QColor, QPixmap

type GlyphEntry = tuple[QPixmap, float, int]

class GlyphCache:
  def __init__(self, limit: int) -> None: ...
  def clear(self) -> None: ...
  def get(
    self, ch: str, size: int, family: str, color: QColor, shadow: bool, dpr: float
  ) -> GlyphEntry: ...
