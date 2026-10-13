import asyncio
import json
from collections.abc import Callable
from enum import Enum, auto

import websockets


class ClientStatus(Enum):
  CONNECTING = auto()
  CONNECTED = auto()
  RECONNECTING = auto()
  STOPPED = auto()


class DanmakuClient:
  def __init__(
    self,
    url: str,
    on_message: Callable[[str, str, int], None],
    on_status: Callable[[ClientStatus], None],
    max_text=80,
  ) -> None:
    self._url = url
    self._on_message = on_message
    self._on_status = on_status
    self._outbox: asyncio.Queue = asyncio.Queue(maxsize=1000)
    self._task: asyncio.Task | None = None
    self._closed = False
    self._max_text = max_text

  def start(self) -> None:
    if self._task is None:
      self._task = asyncio.create_task(self._run())

  async def _run(self) -> None:
    delay = 0.6
    while not self._closed:
      try:
        async with websockets.connect(
          self._url,
          max_size=64 * 1024,
          ping_interval=20,
          ping_timeout=20,
          open_timeout=5,
        ) as ws:
          self._on_status(ClientStatus.CONNECTED)
          delay = 0.6

          recv = asyncio.create_task(self._recv_loop(ws))
          send = asyncio.create_task(self._send_loop(ws))
          _done, pending = await asyncio.wait(
            {recv, send}, return_when=asyncio.FIRST_COMPLETED
          )
          for t in pending:
            t.cancel()
          await asyncio.gather(*pending, return_exceptions=True)
      except asyncio.CancelledError:
        break
      except Exception:  # noqa: BLE001
        self._on_status(ClientStatus.RECONNECTING)

      if self._closed:
        break
      await asyncio.sleep(delay)
      delay = min(delay * 1.6, 10.0)
    self._on_status(ClientStatus.STOPPED)

  async def _recv_loop(self, ws) -> None:
    async for raw in ws:
      if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "ignore")
      try:
        msg = json.loads(raw)
      except ValueError:
        continue
      items = msg.get("items") if msg.get("type") == "batch" else (msg,)
      for m in items or ():
        if not isinstance(m, dict) or m.get("type") != "danmaku":
          continue
        text = str(m.get("text", "")).strip()
        if not text:
          continue
        try:
          size = int(m.get("size", 18))
        except (TypeError, ValueError):
          size = 18
        self._on_message(
          text[: self._max_text],
          str(m.get("color", "#FFFFFF")),
          size,
        )

  async def _send_loop(self, ws) -> None:
    while True:
      data = await self._outbox.get()
      if data is None:
        return
      await ws.send(data)

  def push(self, text, color=None, size=None) -> bool:
    if self._closed:
      return False
    payload = {"type": "danmaku", "text": text}
    if color is not None:
      payload["color"] = color
    if size is not None:
      payload["size"] = size
    try:
      self._outbox.put_nowait(json.dumps(payload, ensure_ascii=False))
      return True
    except asyncio.QueueFull:
      return False

  def stop(self) -> None:
    self._closed = True
    if self._task is not None:
      self._task.cancel()
      self._task = None
