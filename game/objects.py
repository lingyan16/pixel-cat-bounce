import pygame
import math
import random
from enum import Enum
from constants import (
    WHITE, GREEN, RED, BLUE, BLACK, PINK, GRAY, HEIGHT, WIDTH, CAT_SIZE_STAGE_1, TARGET_SIZE
)
from game.characters import CatType, CatCharacter
from game.utils import get_img_dir
from constants import GRAVITY, ELASTICITY, FRICTION, WIDTH


class ObstacleType(Enum):
    BLOWER = 1
    CAT_TREE = 2
    CATNIP = 3
    TREAT = 4
    BLOCK = 5
    DESK = 6
    TAI = 7
    BAN = 8
    GUI = 9
    LIGHT = 10
    ROCK = 11


class Obstacle:
    def __init__(self, x, y, width, height, obs_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = None
        self.type = obs_type
        self.setup_obstacle()

        # 创建遮罩，优化碰撞检测
        if self.image:
            # 转换为带Alpha通道的格式，提高碰撞检测精度
            self.image = self.image.convert_alpha() if self.image.get_alpha() else self.image.convert()
            # 创建遮罩，使用阈值确保只有完全不透明的像素才会被计入碰撞
            self.mask = pygame.mask.from_surface(self.image, threshold=127)
        else:
            # 如果没有图片，创建一个矩形遮罩
            self.mask = pygame.mask.Mask((width, height), True)

        # 缓存边缘像素，用于更精确的碰撞响应
        self.edge_pixels = self.calculate_edge_pixels()

    def setup_obstacle(self):
        obstacle_info = {
            ObstacleType.BLOWER: {"color": (200, 230, 255), "effect": "blow"},
            ObstacleType.CAT_TREE: {"color": (160, 82, 45), "effect": "bounce_vertical"},
            ObstacleType.CATNIP: {"color": (144, 238, 144), "effect": "stick"},
            ObstacleType.TREAT: {"color": (255, 215, 0), "effect": "boost"},
            ObstacleType.BLOCK: {
                "image": get_img_dir("img/screen_3/level/01", "01_bingxiang.png", self.rect.width, self.rect.height),
                "effect": None
            },
            ObstacleType.DESK: {
                "image": get_img_dir("img/screen_3/level/01", "01_di.png", self.rect.width, self.rect.height),
                "effect": None
            },
            ObstacleType.TAI: {
                "image": get_img_dir("img/screen_3/level/02", "02_tai.png", self.rect.width, self.rect.height),
                "effect": None
            },
            ObstacleType.BAN: {
                "image": get_img_dir("img/screen_3/level/02", "02_ban.png", self.rect.width, self.rect.height),
                "effect": None
            },
            ObstacleType.GUI: {
                "image": get_img_dir("img/screen_3/level/03", "03_gui.png", self.rect.width, self.rect.height),
                "effect": None
            },
            ObstacleType.LIGHT: {
                "image": get_img_dir("img/screen_3/level/03", "03_light.png", self.rect.width, self.rect.height),
                "effect": None
            },
            ObstacleType.ROCK: {
                "image": get_img_dir("img/screen_3/level/03", "03_rock.png", self.rect.width, self.rect.height),
                "effect": None
            }
        }
        if self.type in obstacle_info and "image" in obstacle_info[self.type]:
            self.image = obstacle_info[self.type]["image"]
        else:
            # 保持原有颜色逻辑
            self.color = obstacle_info[self.type]["color"]
        self.effect = obstacle_info[self.type]["effect"]

    def apply_effect(self, ball):
        if self.effect == "blow":
            ball.velocity[0] += random.uniform(-5, 5)
            ball.velocity[1] -= random.uniform(2, 5)
        elif self.effect == "bounce_vertical":
            ball.velocity[1] = -abs(ball.velocity[0]) * 0.8
            ball.velocity[0] *= 0.3
        elif self.effect == "stick":
            ball.velocity = [0, 0]
            ball.is_launched = False
        elif self.effect == "boost":
            ball.velocity[0] *= 1.5
            ball.velocity[1] *= 1.5

    def calculate_edge_pixels(self):
        """计算障碍物边缘像素，用于更精确的碰撞响应"""
        edge_pixels = {
            'left': [],
            'right': [],
            'top': [],
            'bottom': []
        }

        if not self.mask:
            return edge_pixels

        mask_size = self.mask.get_size()

        # 只检查边缘区域，提高性能
        edge_width = min(5, mask_size[0] // 4)
        edge_height = min(5, mask_size[1] // 4)

        # 检查左边缘
        for y in range(mask_size[1]):
            for x in range(edge_width):
                if self.mask.get_at((x, y)):
                    edge_pixels['left'].append((x, y))
                    break

        # 检查右边缘
        for y in range(mask_size[1]):
            for x in range(mask_size[0] - 1, mask_size[0] - edge_width - 1, -1):
                if self.mask.get_at((x, y)):
                    edge_pixels['right'].append((x, y))
                    break

        # 检查上边缘
        for x in range(mask_size[0]):
            for y in range(edge_height):
                if self.mask.get_at((x, y)):
                    edge_pixels['top'].append((x, y))
                    break

        # 检查下边缘
        for x in range(mask_size[0]):
            for y in range(mask_size[1] - 1, mask_size[1] - edge_height - 1, -1):
                if self.mask.get_at((x, y)):
                    edge_pixels['bottom'].append((x, y))
                    break

        return edge_pixels

    def get_collision_normal(self, ball_rect):
        """根据碰撞位置计算碰撞法线"""
        # 获取球的中心点
        ball_center = ball_rect.center

        # 计算球中心相对于障碍物各边的位置
        dx = min(max(ball_center[0], self.rect.left), self.rect.right) - ball_center[0]
        dy = min(max(ball_center[1], self.rect.top), self.rect.bottom) - ball_center[1]

        # 根据最近的边确定碰撞法线
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        else:
            return (0, 1 if dy > 0 else -1)

    def draw(self, screen):
        if self.image:  # 优先绘制图片
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            if self.type == ObstacleType.BLOWER:
                pygame.draw.circle(screen, WHITE, self.rect.center, 5)
            elif self.type == ObstacleType.CAT_TREE:
                pygame.draw.line(screen, BLACK, (self.rect.centerx, self.rect.top),
                                 (self.rect.centerx, self.rect.bottom), 3)
            elif self.type == ObstacleType.CATNIP:
                pygame.draw.polygon(screen, GREEN, [
                    (self.rect.centerx, self.rect.top + 5),
                    (self.rect.left + 5, self.rect.bottom - 5),
                    (self.rect.right - 5, self.rect.bottom - 5)
                ])
            elif self.type == ObstacleType.TREAT:
                pygame.draw.ellipse(screen, RED, self.rect.inflate(-20, -10))


class Target:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TARGET_SIZE, TARGET_SIZE)
        self.color = GREEN
        self.is_achieved = False

    def draw(self, screen):
        if not self.is_achieved:
            target_img = get_img_dir("img/screen_3/iteam", "bouns.png", self.rect.width, self.rect.height)
            screen.blit(target_img, self.rect)


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TARGET_SIZE, TARGET_SIZE)
        self.color = GREEN
        self.is_achieved = False

    def draw(self, screen):
        target_img = get_img_dir("img/screen_3/iteam", "cat_coin.png", self.rect.width, self.rect.height)
        screen.blit(target_img, self.rect)


class CatBall:
    def __init__(self, x, y, character):
        self.x = x
        self.y = y
        self.character = character
        self.size = CAT_SIZE_STAGE_1
        self.image = pygame.transform.smoothscale(character.image_ball, (CAT_SIZE_STAGE_1, CAT_SIZE_STAGE_1))
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.velocity = [0, 0]
        self.is_launched = False
        self.is_colliding = False
        self.collision_count = 0
        self.wall_bounces = 0
        self.max_bounces = character.traits.get("bounce", 3)  # 默认3次弹跳

        # 优化遮罩创建
        # 将图像转换为带Alpha通道的格式，提高碰撞检测精度
        self.image = self.image.convert_alpha()
        # 创建遮罩，并设置阈值，只有完全不透明的像素才会被计入碰撞
        self.mask = pygame.mask.from_surface(self.image, threshold=127)

        # 缓存上一次位置，用于优化碰撞检测
        self.last_x = x
        self.last_y = y

    def update(self):
        # 保存上一次位置，用于碰撞后恢复
        self.last_x = self.x
        self.last_y = self.y

        # 应用重力
        self.velocity[1] += GRAVITY

        # 更新位置
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # 更新矩形位置
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # 只有当位置发生显著变化时才更新掩码，提高性能
        if abs(self.x - self.last_x) > 0.5 or abs(self.y - self.last_y) > 0.5:
            # 更新掩码，使用阈值确保只有完全不透明的像素才会被计入碰撞
            self.mask = pygame.mask.from_surface(self.image, threshold=127)

        # 边界碰撞检测
        if self.x < 0 or self.x > WIDTH - self.size:
            # 水平边界碰撞
            self.velocity[0] *= -ELASTICITY
            self.x = max(0, min(WIDTH - self.size, self.x))
            self.wall_bounces += 1

            # 灰猫特殊能力：墙壁弹跳增强
            if (self.character.type == CatType.GRAY and
                    self.wall_bounces <= self.max_bounces and
                    abs(self.velocity[0]) > 2):
                self.velocity[0] *= 1.5

        if self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size
            self.velocity[1] *= -0.5
            self.velocity[0] *= 0.8
            if abs(self.velocity[1]) < 1:
                self.velocity[1] = 0
                self.is_launched = False

        # 增加更严格的速度阈值判断
        VELOCITY_THRESHOLD = 0.1
        if abs(self.velocity[0]) < VELOCITY_THRESHOLD:
            self.velocity[0] = 0
        if abs(self.velocity[1]) < VELOCITY_THRESHOLD:
            self.velocity[1] = 0

        if not self.is_colliding:
            self.velocity[0] *= 0.98

        # 新增：如果小球在水平物体上且速度很小，强制停止
        if self.velocity[1] == 0 and abs(self.velocity[0]) < 0.01:
            self.velocity[0] = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def launch(self, power, angle):
        power *= self.character.traits["power"]
        self.velocity[0] = power * math.cos(angle)
        self.velocity[1] = power * math.sin(angle)  # 移除负号，保持与鼠标方向一致
        self.is_launched = True
        self.collision_count = 0
        self.wall_bounces = 0
        if self.character.type == CatType.WHITE and power > 10:
            self.velocity[0] *= 1.2
            self.velocity[1] *= 1.2


class FireflyParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_size = random.uniform(2.0, 4.0)
        self.color = (
            random.randint(200, 255),  # R: 暖黄色调
            random.randint(180, 230),  # G
            random.randint(50, 100)  # B: 少量蓝色成分
        )
        # 运动参数
        self.speed = random.uniform(0.3, 0.8)
        self.direction = random.uniform(0, 2 * math.pi)
        # 闪烁参数
        self.frequency = random.uniform(0.8, 1.2)  # 闪烁频率
        self.phase = random.uniform(0, 2 * math.pi)  # 随机相位
        self.lifetime = random.randint(300, 500)  # 较长生命周期

    def update(self):
        # 自然飘动轨迹
        self.direction += random.uniform(-0.1, 0.1)
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

        # 随机改变方向(5%概率)
        if random.random() < 0.05:
            self.direction = random.uniform(0, 2 * math.pi)

        # 生命周期管理
        self.lifetime -= 1

    def get_brightness(self):
        """使用正弦波计算当前亮度(0.0-1.0)"""
        time_factor = pygame.time.get_ticks() * 0.001 * self.frequency
        return (math.sin(time_factor + self.phase) + 1) * 0.5  # 转换为0-1范围

    def draw(self, screen):
        # 当前亮度和大小
        brightness = self.get_brightness()
        current_alpha = int(30 + brightness * 225)  # 基础亮度+波动
        current_size = self.base_size * (0.7 + brightness * 0.5)

        # 创建发光效果(三层)
        for i in range(3):
            glow_size = current_size * (1 + i * 0.8)
            glow_alpha = int(current_alpha * (0.6 - i * 0.2))
            glow_color = (*self.color[:3], glow_alpha)

            pygame.draw.circle(
                screen, glow_color,
                (int(self.x), int(self.y)),
                int(glow_size)
            )

        # 绘制核心亮点
        pygame.draw.circle(
            screen, (255, 255, 180, current_alpha),
            (int(self.x), int(self.y)),
            int(current_size * 0.6)
        )