import pygame
import math
import random
from enum import Enum
from constants import (
    WHITE, GREEN, RED, BLUE, BLACK, PINK, GRAY, HEIGHT, WIDTH
)
from game.characters import CatType,CatCharacter

class ObstacleType(Enum):
    BLOWER = 1
    CAT_TREE = 2
    CATNIP = 3
    TREAT = 4
    BLOCK = 5

class Obstacle:
    def __init__(self, x, y, width, height, obs_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obs_type
        self.setup_obstacle()

    def setup_obstacle(self):
        obstacle_info = {
            ObstacleType.BLOWER: {"color": (200, 230, 255), "effect": "blow"},
            ObstacleType.CAT_TREE: {"color": (160, 82, 45), "effect": "bounce_vertical"},
            ObstacleType.CATNIP: {"color": (144, 238, 144), "effect": "stick"},
            ObstacleType.TREAT: {"color": (255, 215, 0), "effect": "boost"},
            ObstacleType.BLOCK: {"color": PINK, "effect": None}
        }
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

    def draw(self, screen):
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
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = GREEN
        self.is_achieved = False

    def draw(self, screen):
        if not self.is_achieved:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=20)
            pygame.draw.rect(screen, WHITE, self.rect.inflate(-10, -10), border_radius=10)

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
        self.velocity[1] += 0.3
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y

        if self.x < 0 or self.x > WIDTH - self.size:
            self.velocity[0] *= -0.7
            self.x = max(0, min(WIDTH - self.size, self.x))
            self.wall_bounces += 1
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

        if not self.is_colliding:
            self.velocity[0] *= 0.98

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def launch(self, power, angle):
        power *= self.character.traits["power"]
        self.velocity[0] = power * math.cos(angle)
        self.velocity[1] = -power * math.sin(angle)
        self.is_launched = True
        self.collision_count = 0
        self.wall_bounces = 0
        if self.character.type == CatType.WHITE and power > 10:
            self.velocity[0] *= 1.2
            self.velocity[1] *= 1.2


class Particle:
    def __init__(self, x, y, effect_type="star"):
        self.x = x
        self.y = y
        self.alpha = 255  # 初始完全不透明
        self.lifetime = random.randint(50, 100)

        # 根据效果类型初始化属性
        if effect_type == "star":
            self.size = random.randint(3, 6)
            self.color = (255, 255, 200)  # 星光的浅黄色
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-1, -0.5)
        elif effect_type == "sparkle":
            self.size = random.randint(2, 4)
            self.color = (random.randint(200, 255), random.randint(100, 200), 50)  # 金色火花
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-2, -1)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha = max(0, self.alpha - 3)  # 逐渐透明化[7](@ref)
        self.lifetime -= 1

    def draw(self, screen):
        color = (*self.color, self.alpha)  # 带透明度的颜色[7](@ref)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)