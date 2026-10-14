from __future__ import annotations

import asyncio
from typing import cast

import qasync
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
  QApplication,
  QHBoxLayout,
  QLineEdit,
  QPushButton,
  QVBoxLayout,
  QWidget,
)

from pydanmaku_engine import DanmakuWidget


class MainWindow(QWidget):
  def __init__(self) -> None:
    super().__init__()
    self.setWindowTitle("PySide6 弹幕 Demo")
    self.resize(1040, 660)

    self.canvas = DanmakuWidget(parent=self)
    self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # 输入区
    self.input = QLineEdit()
    self.input.setPlaceholderText("输入弹幕 回车发送")
    self.input.returnPressed.connect(self._send_from_input)
    self.input.installEventFilter(self)

    self.send_btn = QPushButton("发送")
    self.send_btn.clicked.connect(self._send_from_input)

    bottom = QHBoxLayout()
    bottom.setContentsMargins(10, 0, 10, 10)
    bottom.addWidget(self.input, 1)
    bottom.addWidget(self.send_btn)

    root = QVBoxLayout(self)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)
    root.addWidget(self.canvas, 1)
    root.addLayout(bottom)

    self._hide_input()

  def _show_input(self) -> None:
    self.input.show()
    self.send_btn.show()
    self.input.setFocus()

  def _hide_input(self) -> None:
    self.input.clear()
    self.input.hide()
    self.send_btn.hide()
    self.canvas.setFocus()

  def _send_from_input(self) -> None:
    text = self.input.text().strip()
    if not text:
      return
    self.canvas.enqueue(f"{text}", "#FF0000", 20)
    self._hide_input()

  def keyPressEvent(self, event) -> None:
    if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
      if not self.input.isVisible():
        self._show_input()
        return
      self.input.setFocus()
      return
    super().keyPressEvent(event)

  def eventFilter(self, obj, event: QEvent) -> bool:
    if isinstance(event, QKeyEvent):
      if obj is not self.input:
        return False
      key_event = cast(QKeyEvent, event)
      if (
        key_event.type() == QEvent.Type.KeyPress
        and key_event.key() == Qt.Key.Key_Escape
      ):
        self._hide_input()
        return True
    return super().eventFilter(obj, event)

  def closeEvent(self, event) -> None:
    super().closeEvent(event)


def main() -> None:
  app = QApplication()

  loop = qasync.QEventLoop(app)
  asyncio.set_event_loop(loop)

  w = MainWindow()
  w.show()

  with loop:
    loop.run_forever()


if __name__ == "__main__":
  main()
