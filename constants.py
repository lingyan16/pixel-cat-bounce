from enum import Enum
import pygame

# 屏幕尺寸
WIDTH, HEIGHT = 1280, 720
CAT_SIZE = 60

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
DARK_GRAY = (80, 80, 80)
LIGHT_PINK = (255, 100, 100)

# 字体设置
FONT_NAME = "SimHei"
FONT_SIZE = int(24 * min(WIDTH/1280, HEIGHT/720))
BIG_FONT_SIZE = int(36 * min(WIDTH/1280, HEIGHT/720))

# menu
BUTTON_SIZE = 80 # 选择按钮
BAR_WIDTH = 160 # 血条宽度
BAR_HEIGHT = 8 # 血条高度
CARD_WIDTH = 180 # 猫咪卡片容器（宽度）（增加高度容纳下方按钮）
CARD_HEIGHT = 320 # 猫咪卡片容器（高度）（增加高度容纳下方按钮）

# begin
KAISHI_SIZE_WIDTH, KAISHI_SIZE_HEIGHT = 200, 80

# stage_1
CAT_SIZE_STAGE_1 = 60

# 第一关物品
DESK_WIDTH, DESK_HEIGHT = 750, 200