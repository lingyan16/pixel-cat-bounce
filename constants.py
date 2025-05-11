from enum import Enum
import pygame

# 屏幕尺寸
WIDTH, HEIGHT = 1280, 720
CAT_SIZE = 100

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
PINK = (255, 182, 193)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)
GREEN = (46, 139, 87)
CLEAR = (0, 0, 255, 128)
ORANGE = (255, 165, 0)

# 字体设置
FONT_NAME = "SimHei"
FONT_SIZE = int(24 * min(WIDTH/1280, HEIGHT/720))
BIG_FONT_SIZE = int(36 * min(WIDTH/1280, HEIGHT/720))