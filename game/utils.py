import os
import pygame
from constants import WIDTH, HEIGHT, WHITE, BLUE, FONT_SIZE, BIG_FONT_SIZE, FONT_NAME


def get_img_dir(folder, file_name, width, height):
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.dirname(current_dir)
    filepath = os.path.join(base_dir, folder, file_name)
    try:
        image = pygame.image.load(filepath).convert_alpha()
        return pygame.transform.scale(image, (width, height))
    except Exception as e:
        print(f"图片加载失败: {e}")
        fallback = pygame.Surface((width, height))
        fallback.fill((230, 230, 250))
        return fallback

def get_obs_dir(filename):
    return os.path.join("img", "screen_3/iteam", filename)

def create_pixel_cat(base_color):
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surface, base_color, (20, 20), 20)
    ear_points = [(10, 10), (13, 13), (8, 13)]
    pygame.draw.polygon(surface, tuple(max(c-50,0) for c in base_color), ear_points)
    pygame.draw.circle(surface, WHITE, (13, 20), 5)
    pygame.draw.circle(surface, BLUE, (13, 20), 2)
    pygame.draw.circle(surface, WHITE, (27, 20), 5)
    pygame.draw.circle(surface, BLUE, (27, 20), 2)
    return surface

def is_fallback(surface, expected_color=(230, 230, 250)):
    fallback_surf = pygame.Surface(surface.get_size())
    fallback_surf.fill(expected_color)
    return pygame.image.tostring(surface, 'RGB') == pygame.image.tostring(fallback_surf, 'RGB')

def init_fonts():
    try:
        zh_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        zh_big_font = pygame.font.SysFont(FONT_NAME, BIG_FONT_SIZE)
    except:
        zh_font = pygame.font.Font(None, FONT_SIZE)
        zh_big_font = pygame.font.Font(None, BIG_FONT_SIZE)
    return zh_font, zh_big_font