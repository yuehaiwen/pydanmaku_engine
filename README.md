# PyDanmaku Engine

PyDanmaku Engine is a Python library for building real-time bullet-screen / danmaku experiences in PySide6 applications. It includes:

- a high-performance danmaku renderer for Qt widgets
- track scheduling and item lifecycle management
- WebSocket-based client support for receiving and sending danmaku messages in real time
- easy customization of speed, font, background, and coverage

## Features

- Render danmaku items in a QWidget with smooth animation
- Maintain multiple tracks and spawn scheduling automatically
- Support custom text color, size, and background styling
- Receive danmaku payloads from a server via WebSocket
- Push local messages back to the server for broadcast scenarios

## Installation

Install from PyPI:

```bash
pip install pydanmaku_engine
```

## Requirements

- Python >= 3.13
- PySide6
- websockets
- qasync

## Quick start

The core widget is `DanmakuWidget` and the networking helper is `DanmakuClient`.

```python
from PySide6.QtWidgets import QApplication
from pydanmaku_engine.client import DanmakuClient
from pydanmaku_engine.widget import DanmakuWidget

app = QApplication([])
widget = DanmakuWidget()
widget.resize(960, 540)
widget.show()

client = DanmakuClient(
    "ws://127.0.0.1:18765",
    on_message=lambda text, color, size: widget.enqueue(text, color, size),
    on_status=lambda status: None,
)
client.start()

widget.enqueue("Hello, danmaku!", color="#FFFFFF", size=24)

app.exec()
```

## Widget usage

```python
from pydanmaku_engine.widget import DanmakuWidget

widget = DanmakuWidget()
widget.set_speed(240.0)
widget.set_font("Microsoft YaHei", 24)
widget.set_background("#16161f", "#0a0a0f")
widget.enqueue("Welcome to PyDanmaku Engine!", "#FFD700", 28)
```

## Client usage

```python
from pydanmaku_engine.client import DanmakuClient

client = DanmakuClient(
    "ws://127.0.0.1:18765",
    on_message=lambda text, color, size: print(text, color, size),
    on_status=lambda status: print(status),
)

client.start()
client.push("Test danmaku", color="#00FFAA", size=20)
```

## Example project

A complete demo is included in the repository under `examples/quick_start.py`.

## Contributing

Contributions are welcome. If you find a bug or want to propose a feature, please open an issue or submit a pull request in the project repository.
