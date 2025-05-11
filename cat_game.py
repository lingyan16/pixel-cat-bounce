# -*- coding: utf-8 -*-
import os
from warnings import catch_warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # 解决线程错误
import pygame
import sys
import math
import random
from enum import Enum

# 初始化pygame
pygame.init()

# 定义常量
WIDTH, HEIGHT = 800, 600
# 1920 1080
cat_size = 40

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

# 屏幕设置
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("像素猫咪团子弹射解谜")

# 字体初始化
try:
    zh_font = pygame.font.SysFont("SimHei", 24)
    zh_big_font = pygame.font.SysFont("SimHei", 36)
except Exception as e:
    print(f"字体加载失败: {e}, 使用默认字体")
    zh_font = pygame.font.Font(None, 24)
    zh_big_font = pygame.font.Font(None, 36)

# 抽象加载图片方法 folder:文件夹名 file_name:文件名 width:长度 height:宽度
def get_img_dir(folder, file_name, width, height):
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, folder, file_name)
    try:
        image = pygame.image.load(filepath).convert_alpha()
        return pygame.transform.scale(image, (width, height))  # 确保缩放
    except Exception as e:
        print(f"图片加载失败: {e}")
        fallback = pygame.Surface((width, height))  # 使用传入的宽高
        fallback.fill((230, 230, 250))
        return fallback  # 返回回退背景
def is_fallback(surface, expected_color=(230, 230, 250)):
    """检查 Surface 是否是回退背景（纯色）"""
    # 生成一个临时纯色 Surface 用于对比
    fallback_surf = pygame.Surface(surface.get_size())
    fallback_surf.fill(expected_color)
    # 比较两个 Surface 的像素数据是否相同
    return pygame.image.tostring(surface, 'RGB') == pygame.image.tostring(fallback_surf, 'RGB')

# 绘画像素猫咪
def create_pixel_cat(base_color):
    """创建像素风格的猫咪"""
    surface = pygame.Surface((cat_size, cat_size), pygame.SRCALPHA)
    # 身体（圆形）
    pygame.draw.circle(surface, base_color, (cat_size // 2, cat_size // 2), cat_size // 2)
    # 耳朵（三角形）
    ear_points = [
        (cat_size // 4, cat_size // 4),
        (cat_size // 3, cat_size // 3),
        (cat_size // 6, cat_size // 3)
    ]
    pygame.draw.polygon(surface, (max(0, base_color[0] - 50), max(0, base_color[1] - 50), max(0, base_color[2] - 50)), ear_points)
    # 眼睛
    eye_size = cat_size // 8
    pygame.draw.circle(surface, WHITE, (cat_size // 3, cat_size // 2), eye_size)
    pygame.draw.circle(surface, BLUE, (cat_size // 3, cat_size // 2), eye_size // 2)
    pygame.draw.circle(surface, WHITE, (2 * cat_size // 3, cat_size // 2), eye_size)
    pygame.draw.circle(surface, BLUE, (2 * cat_size // 3, cat_size // 2), eye_size // 2)
    return surface

# 加载全局背景
background = get_img_dir("img", "background.png", WIDTH, HEIGHT)
# 加载菜单猫咪背景
menu_cat_background_image = get_img_dir("img", "menu_cat_background.png", 100, 100)
# 加载猫咪图片（保留原有逻辑）
orange_cat_img = get_img_dir("img", "cat1.png", cat_size, cat_size)
gray_cat_img = get_img_dir("img", "cat2.png", cat_size, cat_size)
white_cat_img = get_img_dir("img", "cat3.png", cat_size, cat_size)
# 检查是否是回退背景，如果是则生成像素猫
if is_fallback(orange_cat_img):
    orange_cat_img = create_pixel_cat(ORANGE)  # 橘猫
if is_fallback(gray_cat_img):
    gray_cat_img = create_pixel_cat(GRAY)  # 灰猫
if is_fallback(white_cat_img):
    white_cat_img = create_pixel_cat(WHITE)  # 白猫

# 猫咪角色类型
class CatType(Enum):
    ORANGE = 1  # 橘猫 - 力量型
    GRAY = 2  # 灰猫 - 技巧型
    WHITE = 3  # 白猫 - 速度型

# 障碍物类型
class ObstacleType(Enum):
    BLOWDRYER = 1  # 吹风机
    CAT_TREE = 2  # 猫爬架
    CATNIP = 3  # 木天蓼
    TREAT = 4  # 猫条
    BLOCK = 5  # 普通障碍物

# 猫咪角色类
class CatCharacter:
    def __init__(self, cat_type):
        self.type = cat_type
        self.size = 40
        self.image = self.create_cat_image()
        self.traits = self.set_traits()

    def create_cat_image(self):
        """根据猫咪类型返回对应的图片"""
        if self.type == CatType.ORANGE:
            return orange_cat_img
        elif self.type == CatType.GRAY:
            return gray_cat_img
        elif self.type == CatType.WHITE:
            return white_cat_img

    def set_traits(self):
        """设置角色特性"""
        base_traits = {
            "power": 1.0,  # 击发力
            "aim_assist": 0,  # 辅助线
            "bounce": 0,  # 弹跳
            "special": None  # 特殊能力
        }
        type_traits = {
            CatType.ORANGE: {
                "power": 1.5,
                "aim_assist": 1,
                "special": "power_shot"  # 强力一击
            },
            CatType.GRAY: {
                "aim_assist": 3,
                "bounce": 2,
                "special": "wall_jump"  # 墙壁跳跃
            },
            CatType.WHITE: {
                "power": 0.8,
                "aim_assist": 2,
                "special": "quick_charge"  # 快速蓄力
            }
        }
        base_traits.update(type_traits[self.type])
        return base_traits

# 弹珠/猫咪球类
class CatBall:
    def __init__(self, x, y, character):
        self.x = x
        self.y = y
        self.character = character
        self.size = character.size
        self.image = character.image
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.velocity = [0, 0]
        self.is_launched = False
        self.is_colliding = False
        self.collision_count = 0
        self.wall_bounces = 0
        self.max_bounces = character.traits["bounce"]

    def update(self):
        """更新猫咪球的位置和状态"""
        # 应用重力
        self.velocity[1] += 0.3

        # 更新位置
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y

        # 边界检查
        if self.x < 0 or self.x > WIDTH - self.size:
            self.velocity[0] *= -0.7
            self.x = max(0, min(WIDTH - self.size, self.x))
            self.wall_bounces += 1

            # 灰猫特殊能力：墙壁跳跃
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

        # 速度衰减
        if not self.is_colliding:
            self.velocity[0] *= 0.98

    def draw(self, screen):
        """在屏幕上绘制猫咪球"""
        screen.blit(self.image, (self.x, self.y))

    def launch(self, power, angle):
        """发射弹珠"""
        power *= self.character.traits["power"]
        self.velocity[0] = power * math.cos(angle)
        self.velocity[1] = -power * math.sin(angle)
        self.is_launched = True
        self.collision_count = 0
        self.wall_bounces = 0

        # 白猫特殊能力：快速蓄力
        if self.character.type == CatType.WHITE and power > 10:
            self.velocity[0] *= 1.2
            self.velocity[1] *= 1.2

# 障碍物类
class Obstacle:
    def __init__(self, x, y, width, height, obs_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obs_type
        self.setup_obstacle()

    def setup_obstacle(self):
        """设置障碍物属性"""
        obstacle_info = {
            ObstacleType.BLOWDRYER: {
                "color": (200, 230, 255),
                "effect": "blow"  # 吹飞效果
            },
            ObstacleType.CAT_TREE: {
                "color": (160, 82, 45),
                "effect": "bounce_vertical"  # 垂直弹跳
            },
            ObstacleType.CATNIP: {
                "color": (144, 238, 144),
                "effect": "stick"  # 粘住
            },
            ObstacleType.TREAT: {
                "color": (255, 215, 0),
                "effect": "boost"  # 加速
            },
            ObstacleType.BLOCK: {
                "color": PINK,
                "effect": None
            }
        }
        self.color = obstacle_info[self.type]["color"]
        self.effect = obstacle_info[self.type]["effect"]

    def apply_effect(self, ball):
        """应用障碍物效果"""
        if self.effect == "blow":
            # 吹风机效果 - 随机方向吹飞
            ball.velocity[0] += random.uniform(-5, 5)
            ball.velocity[1] -= random.uniform(2, 5)
        elif self.effect == "bounce_vertical":
            # 猫爬架效果 - 垂直弹跳
            ball.velocity[1] = -abs(ball.velocity[0]) * 0.8
            ball.velocity[0] *= 0.3
        elif self.effect == "stick":
            # 木天蓼效果 - 粘住
            ball.velocity = [0, 0]
            ball.is_launched = False
        elif self.effect == "boost":
            # 猫条效果 - 加速
            ball.velocity[0] *= 1.5
            ball.velocity[1] *= 1.5

    def draw(self, screen):
        """在屏幕上绘制障碍物"""
        pygame.draw.rect(screen, self.color, self.rect)
        # 添加障碍物图标
        if self.type == ObstacleType.BLOWDRYER:
            pygame.draw.circle(screen, WHITE, (self.rect.centerx, self.rect.centery), 5)
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
            pygame.draw.ellipse(screen, RED,
                                (self.rect.centerx - 10, self.rect.centery - 5, 20, 10))

# 目标类
class Target:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = GREEN
        self.is_achieved = False

    def draw(self, screen):
        """在屏幕上绘制目标"""
        if not self.is_achieved:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=20)
            pygame.draw.rect(screen, WHITE, self.rect.inflate(-10, -10), border_radius=10)

# 游戏主类
class CatBounceGame:
    def __init__(self):
        self.font = zh_font  # 使用中文字体
        self.big_font = zh_big_font
        self.state = "menu"  # menu, playing, level_complete, game_over
        self.selected_cat = None
        self.cat_options = [
            CatCharacter(CatType.ORANGE),
            CatCharacter(CatType.GRAY),
            CatCharacter(CatType.WHITE)
        ]
        self.level = 1
        self.max_levels = 3
        self.balls_left = 3
        self.score = 0
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        self.cat_ball = None
        self.obstacles = []
        self.targets = []
        self.launch_power = 0
        self.max_power = 25
        self.charging = False
        self.aim_line = []
        self.setup_level()

    def setup_level(self):
        """设置关卡障碍物和目标"""
        self.obstacles = []
        self.targets = []

        # 根据关卡设置不同的障碍物布局
        level_layouts = {
            1: {
                "obstacles": [
                    Obstacle(300, 400, 200, 20, ObstacleType.BLOCK),
                    Obstacle(200, 300, 150, 20, ObstacleType.BLOCK),
                    Obstacle(500, 350, 100, 20, ObstacleType.CAT_TREE)
                ],
                "targets": [Target(700, 550)]
            },
            2: {
                "obstacles": [
                    Obstacle(250, 450, 150, 20, ObstacleType.BLOCK),
                    Obstacle(400, 350, 100, 20, ObstacleType.BLOWDRYER),
                    Obstacle(300, 250, 200, 20, ObstacleType.TREAT),
                    Obstacle(150, 150, 100, 20, ObstacleType.CATNIP)
                ],
                "targets": [Target(650, 100)]
            },
            3: {
                "obstacles": [
                    Obstacle(200, 500, 100, 20, ObstacleType.BLOCK),
                    Obstacle(350, 400, 100, 20, ObstacleType.BLOWDRYER),
                    Obstacle(500, 300, 100, 20, ObstacleType.TREAT),
                    Obstacle(300, 200, 200, 20, ObstacleType.CAT_TREE),
                    Obstacle(150, 100, 100, 20, ObstacleType.CATNIP)
                ],
                "targets": [Target(700, 550), Target(700, 400)]
            }
        }
        layout = level_layouts[self.level]
        self.obstacles = layout["obstacles"]
        self.targets = layout["targets"]

        # 重置弹珠位置
        if self.selected_cat:
            self.cat_ball = CatBall(100, HEIGHT - 100, self.selected_cat)

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 检查选择了哪个猫咪角色
                    mouse_pos = pygame.mouse.get_pos()
                    for i, cat in enumerate(self.cat_options):
                        cat_rect = pygame.Rect(200 + i * 150, 300, 100, 100)
                        if cat_rect.collidepoint(mouse_pos):
                            self.selected_cat = cat
                            self.state = "playing"
                            self.reset_game()
                            break

            elif self.state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN and not self.cat_ball.is_launched and self.balls_left > 0:
                    self.charging = True
                    self.aim_line = []

                if event.type == pygame.MOUSEBUTTONUP and self.charging:
                    if self.launch_power > 5:  # 最小发射力度
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        dx = mouse_x - self.cat_ball.x
                        dy = mouse_y - self.cat_ball.y
                        angle = math.atan2(dy, dx)
                        power = min(self.launch_power, self.max_power)
                        self.cat_ball.launch(power, angle)
                        self.balls_left -= 1
                    self.charging = False
                    self.launch_power = 0

            elif self.state in ["level_complete", "game_over"]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "level_complete" and self.level < self.max_levels:
                        self.level += 1
                        self.balls_left = 3
                        self.reset_game()
                        self.state = "playing"
                    elif self.state == "game_over" or self.level == self.max_levels:
                        self.level = 1
                        self.balls_left = 3
                        self.score = 0
                        self.state = "menu"

        return True

    def update(self):
        """更新游戏状态"""
        if self.state != "playing":
            return

        # 蓄力过程
        if self.charging:
            self.launch_power = min(self.launch_power + 0.5, self.max_power)

            # 计算辅助线（根据猫咪特性）
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.cat_ball.x
            dy = mouse_y - self.cat_ball.y
            angle = math.atan2(dy, dx)
            power = min(self.launch_power, self.max_power)

            # 生成辅助线点
            self.aim_line = []
            steps = 20 + self.selected_cat.traits["aim_assist"] * 10
            for i in range(1, steps):
                t = i * 0.1
                vx = power * math.cos(angle)
                vy = -power * math.sin(angle)
                x = self.cat_ball.x + vx * t
                y = self.cat_ball.y + vy * t + 0.5 * 0.3 * t * t  # 考虑重力

                if x < 0 or x > WIDTH or y > HEIGHT:
                    break

                self.aim_line.append((x, y))

        # 更新猫咪球
        if self.cat_ball:
            self.cat_ball.update()

            # 检查与障碍物的碰撞
            self.cat_ball.is_colliding = False
            for obstacle in self.obstacles:
                if self.cat_ball.rect.colliderect(obstacle.rect):
                    self.cat_ball.is_colliding = True
                    self.cat_ball.collision_count += 1

                    # 橘猫特殊能力：碰撞3次后重置惯性
                    if (self.selected_cat.type == CatType.ORANGE and
                            self.cat_ball.collision_count >= 3 and
                            abs(self.cat_ball.velocity[0]) > 5):
                        self.cat_ball.velocity[0] *= 1.5
                        self.cat_ball.collision_count = 0

                    # 应用障碍物效果
                    obstacle.apply_effect(self.cat_ball)

                    # 基本碰撞反弹
                    if obstacle.effect != "stick":  # 木天蓼会粘住不反弹
                        # 简单碰撞反弹
                        if abs(self.cat_ball.rect.centerx - obstacle.rect.centerx) > abs(
                                self.cat_ball.rect.centery - obstacle.rect.centery):
                            self.cat_ball.velocity[0] *= -0.7
                        else:
                            self.cat_ball.velocity[1] *= -0.7

                    # 调整位置防止卡住
                    if self.cat_ball.velocity[0] > 0 and self.cat_ball.rect.left < obstacle.rect.left:
                        self.cat_ball.x = obstacle.rect.left - self.cat_ball.size
                    elif self.cat_ball.velocity[0] < 0 and self.cat_ball.rect.right > obstacle.rect.right:
                        self.cat_ball.x = obstacle.rect.right

                    if self.cat_ball.velocity[1] > 0 and self.cat_ball.rect.top < obstacle.rect.top:
                        self.cat_ball.y = obstacle.rect.top - self.cat_ball.size
                    elif self.cat_ball.velocity[1] < 0 and self.cat_ball.rect.bottom > obstacle.rect.bottom:
                        self.cat_ball.y = obstacle.rect.bottom

            # 检查是否到达目标
            for target in self.targets:
                if not target.is_achieved and self.cat_ball.rect.colliderect(target.rect):
                    target.is_achieved = True
                    self.score += 100 * self.level

            # 检查关卡是否完成
            if all(target.is_achieved for target in self.targets):
                self.state = "level_complete"
            elif self.balls_left <= 0 and not self.cat_ball.is_launched:
                self.state = "game_over"

    def draw(self):
        """绘制游戏界面"""
        screen.blit(background, (0, 0))

        if self.state == "menu":
            # 绘制菜单界面
            # 绘制菜单界面（保持原有代码不变）
            # 为了让文字更清晰，可以在文字下方添加半透明背景
            menu_bg = pygame.Surface((WIDTH - 100, 400), pygame.SRCALPHA)
            menu_bg.fill((255, 255, 255, 180))  # 半透明白色
            screen.blit(menu_bg, (50, 50))

            title = self.big_font.render("像素猫咪团子弹射解谜", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

            instruction = self.font.render("选择你的猫咪角色:", True, BLACK)
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 250))

            # 绘制猫咪选项
            for i, cat in enumerate(self.cat_options):
                # 绘制时正确调用 blit，仅传递 (x, y)
                pos_x = 200 + i * 150
                screen.blit(menu_cat_background_image, (pos_x, 300))  # 仅传(x, y)
                screen.blit(cat.image, (pos_x + 30, 330))

                # 显示猫咪特性
                traits_text = self.font.render(f"力量: {cat.traits['power']:.1f}", True, BLACK)
                screen.blit(traits_text, (200 + i * 150, 420))

                traits_text = self.font.render(f"辅助: {cat.traits['aim_assist']}", True, BLACK)
                screen.blit(traits_text, (200 + i * 150, 450))

        elif self.state == "playing":
            # 绘制游戏元素
            for obstacle in self.obstacles:
                obstacle.draw(screen)

            for target in self.targets:
                target.draw(screen)

            if self.cat_ball:
                self.cat_ball.draw(screen)

            # 绘制辅助线
            if self.charging and self.selected_cat.traits["aim_assist"] > 0:
                for i in range(len(self.aim_line) - 1):
                    alpha = 255 * (i + 1) / len(self.aim_line)
                    color = (100, 100, 255, min(200, int(alpha)))
                    pygame.draw.line(screen, color, self.aim_line[i], self.aim_line[i + 1], 2)

            # 绘制蓄力条
            if self.charging:
                power_width = 200 * (self.launch_power / self.max_power)
                pygame.draw.rect(screen, RED, (50, 50, power_width, 20))
                pygame.draw.rect(screen, BLACK, (50, 50, 200, 20), 2)
                power_text = self.font.render(f"力度: {int(self.launch_power)}", True, BLACK)
                screen.blit(power_text, (60, 55))

            # 绘制游戏信息
            level_text = self.font.render(f"关卡: {self.level}", True, BLACK)
            screen.blit(level_text, (WIDTH - 150, 20))

            balls_text = self.font.render(f"剩余弹珠: {self.balls_left}", True, BLACK)
            screen.blit(balls_text, (WIDTH - 150, 50))

            score_text = self.font.render(f"分数: {self.score}", True, BLACK)
            screen.blit(score_text, (WIDTH - 150, 80))

        elif self.state == "level_complete":
            # 绘制关卡完成界面
            complete_text = self.big_font.render(f"关卡 {self.level} 完成!", True, BLACK)
            screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 2 - 50))

            if self.level < self.max_levels:
                next_text = self.font.render("点击继续下一关", True, BLACK)
            else:
                next_text = self.font.render("恭喜通关! 点击返回主菜单", True, BLACK)
            screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 20))

        elif self.state == "game_over":
            # 绘制游戏结束界面
            over_text = self.big_font.render("游戏结束", True, BLACK)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))

            score_text = self.font.render(f"最终分数: {self.score}", True, BLACK)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

            restart_text = self.font.render("点击返回主菜单", True, BLACK)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

# 运行游戏
if __name__ == "__main__":
    game = CatBounceGame()
    game.run()
    pygame.quit()
    sys.exit()
