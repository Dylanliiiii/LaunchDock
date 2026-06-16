from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QColor, QIcon, QImage, QPixmap

APP_ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
BACKGROUND_REMOVE_THRESHOLD = 34


def image_has_alpha(image: QImage) -> bool:
    if not image.hasAlphaChannel():
        return False
    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixelColor(x, y).alpha() < 255:
                return True
    return False


def remove_solid_icon_background(image: QImage) -> QImage:
    result = image.convertToFormat(QImage.Format.Format_ARGB32)
    if image_has_alpha(result):
        return result

    corners = [
        result.pixelColor(0, 0),
        result.pixelColor(result.width() - 1, 0),
        result.pixelColor(0, result.height() - 1),
        result.pixelColor(result.width() - 1, result.height() - 1),
    ]
    background = max(corners, key=lambda color: sum(1 for item in corners if color_distance(color, item) <= 6))

    for y in range(result.height()):
        for x in range(result.width()):
            color = result.pixelColor(x, y)
            distance = color_distance(color, background)
            if distance <= BACKGROUND_REMOVE_THRESHOLD:
                color.setAlpha(0)
            elif distance <= BACKGROUND_REMOVE_THRESHOLD * 2:
                color.setAlpha(min(255, int((distance - BACKGROUND_REMOVE_THRESHOLD) / BACKGROUND_REMOVE_THRESHOLD * 255)))
            result.setPixelColor(x, y, color)
    return result


def color_distance(first: QColor, second: QColor) -> int:
    return max(abs(first.red() - second.red()), abs(first.green() - second.green()), abs(first.blue() - second.blue()))


@lru_cache(maxsize=1)
def app_icon() -> QIcon:
    if APP_ICON_PATH.exists():
        image = QImage(str(APP_ICON_PATH))
        if not image.isNull():
            return QIcon(QPixmap.fromImage(remove_solid_icon_background(image)))
    return QIcon()
