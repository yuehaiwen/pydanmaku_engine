class DanmakuEngine:
  def __init__(self, name: str) -> None:
    self.name = name

  def launch(self, message: str) -> None:
    print(f"[{self.name}] 弹幕发射: {message}")

  def hello(self) -> str:
    return f"Hello from {self.name}!"
