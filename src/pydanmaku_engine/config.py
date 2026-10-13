from dataclasses import dataclass


@dataclass
class DanmakuConfig:
  # 布局
  track_height: int = 44
  top_margin: int = 12
  gap: int = 28
  # 资源上限
  pool_limit: int = 512
  glyph_limit: int = 4096
  pending_limit: int = 300
  spawn_budget_ms: float = 3.0
  spawn_max_per_tick: int = 32
  # 外观
  font_family: str = "Microsoft YaHei"
  font_size: int = 18
  shadow_enabled: bool = False
  bg_top: str = "#16161f"
  bg_bottom: str = "#0a0a0f"
  # 运动
  speed: float = 160.0
  fps: int = 120
  coverage: float = 1.0
