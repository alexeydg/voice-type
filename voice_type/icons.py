from __future__ import annotations

from PIL import Image, ImageDraw


def make_icon(state: str = "idle", size: int = 64) -> Image.Image:
    """Simple tray icon: idle=mic, recording=red mic, busy=amber."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    colors = {
        "idle": ((70, 130, 180, 255), (40, 80, 120, 255)),
        "recording": ((220, 60, 60, 255), (140, 30, 30, 255)),
        "busy": ((230, 160, 40, 255), (150, 100, 20, 255)),
    }
    fill, outline = colors.get(state, colors["idle"])

    cx = cy = size // 2
    # Mic capsule
    r = size // 5
    top = cy - size // 5
    bottom = cy + size // 10
    draw.rounded_rectangle(
        (cx - r, top, cx + r, bottom),
        radius=r,
        fill=fill,
        outline=outline,
        width=max(1, size // 32),
    )
    # Stand
    stand_y = bottom + size // 16
    draw.arc(
        (cx - r - 2, bottom - r, cx + r + 2, stand_y + r),
        start=0,
        end=180,
        fill=outline,
        width=max(2, size // 20),
    )
    draw.line((cx, stand_y + r // 2, cx, size - size // 8), fill=outline, width=max(2, size // 20))
    draw.line(
        (cx - r // 1.5, size - size // 8, cx + r // 1.5, size - size // 8),
        fill=outline,
        width=max(2, size // 20),
    )
    return img
