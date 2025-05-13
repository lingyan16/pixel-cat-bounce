import random
import pygame
import sys
import math
from game.characters import CatType, CatCharacter
from game.objects import Obstacle, Target, CatBall, ObstacleType, Particle
from game.utils import get_img_dir, init_fonts
from constants import WIDTH, HEIGHT, BLACK, RED, WHITE, GREEN, CAT_SIZE, DESK_WIDTH, DESK_HEIGHT, BUTTON_SIZE, \
    BAR_WIDTH, BAR_HEIGHT, KAISHI_SIZE_WIDTH, KAISHI_SIZE_HEIGHT, DARK_GRAY, LIGHT_PINK, CARD_WIDTH, CARD_HEIGHT, \
    TARGET_SIZE


class CatBounceGame:
    def __init__(self):
        self.transition_rect = None
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font, self.big_font = init_fonts()
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
        # 新增资源加载
        # 开始界面
        self.begin_background = get_img_dir("img/screen_begin", "screen_begin.png", WIDTH, HEIGHT)
        self.begin_button_img = get_img_dir("img/screen_begin", "kaishi.png", KAISHI_SIZE_WIDTH, KAISHI_SIZE_HEIGHT)
        self.button_rect = self.begin_button_img.get_rect(center=(WIDTH // 2, 500)) # 开始按钮位置
        # 菜单界面
        self.menu_background = get_img_dir("img/screen_menu", "screen_menu.png", WIDTH, HEIGHT) # 菜单背景
        self.select_button = get_img_dir("img/screen_menu", "select_button.png", BUTTON_SIZE, BUTTON_SIZE) # 加载选择按钮素材
        # 第一关
        self.level1_background = get_img_dir("img/screen_3/level/01", "stage_01.png", WIDTH, HEIGHT)
        # 第二关
        self.level2_background = get_img_dir("img/screen_3/level/02", "stage_02.png", WIDTH, HEIGHT)
        # 第三关
        self.level3_background = get_img_dir("img/screen_3/level/03", "stage_03.png", WIDTH, HEIGHT)
        # 游戏结束
        self.gameOver_background = get_img_dir("img", "game_over.png", WIDTH, HEIGHT)
        # self.click_sound = pygame.mixer.Sound('audio/click.wav')
        self.particles = []  # 存储活跃粒子
        self.particle_spawn_timer = 0  # 粒子生成计时器
        self.reset_game()
        # 修改初始化状态
        self.state = "begin"  # 新增初始状态

    def reset_game(self):
        self.cat_ball = None
        self.bgs = None
        self.obstacles = []
        self.targets = []
        self.launch_power = 0
        self.max_power = 25
        self.charging = False
        self.aim_line = []
        self.setup_level()

    def setup_level(self):
        level_layouts = {
            1: {
                "bgs": self.level1_background,
                "obstacles": [
                    Obstacle(3 * WIDTH // 5, 3 * HEIGHT // 12, 500, 550, ObstacleType.BLOCK),
                    # Obstacle(0, HEIGHT-DESK_HEIGHT, DESK_WIDTH, DESK_HEIGHT, ObstacleType.DESK),

                ],
                "targets": [Target(900, 130)]
            },
            2: {
                "bgs": self.level2_background,
                "obstacles": [
                    # Obstacle(250, 450, 150, 20, ObstacleType.BLOCK),
                    # Obstacle(400, 350, 100, 20, ObstacleType.BLOWER),
                    # Obstacle(300, 250, 200, 20, ObstacleType.TREAT),
                    # Obstacle(150, 150, 100, 20, ObstacleType.CATNIP)
                    Obstacle(WIDTH // 22, 13 * HEIGHT // 50, 400, 60, ObstacleType.BAN)
                ],
                "targets": [Target(WIDTH // 22 + 400 // 2, 13 * HEIGHT // 50 - TARGET_SIZE)]
            },
            3: {
                "bgs": self.level3_background,
                "obstacles": [
                    # Obstacle(200, 500, 100, 20, ObstacleType.BLOCK),
                    # Obstacle(350, 400, 100, 20, ObstacleType.BLOWER),
                    # Obstacle(500, 300, 100, 20, ObstacleType.TREAT),
                    # Obstacle(300, 200, 200, 20, ObstacleType.CAT_TREE),
                    # Obstacle(150, 100, 100, 20, ObstacleType.CATNIP)
                ],
                "targets": [Target(700, 550), Target(700, 400)]
            }
        }
        layout = level_layouts[self.level]
        self.bgs = layout["bgs"]
        self.obstacles = layout["obstacles"]
        self.targets = layout["targets"]
        if self.selected_cat:
            self.cat_ball = CatBall(100, HEIGHT-CAT_SIZE-DESK_HEIGHT, self.selected_cat)

    def spawn_particles(self, effect_type):
        if len(self.particles) > 100:  # 最大粒子数限制
            return
        """生成粒子群"""
        for _ in range(random.randint(3, 5)):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            self.particles.append(Particle(x, y, effect_type))

    def handle_events(self):
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 新增开始界面事件处理
            if self.state == "begin" and event.type == pygame.MOUSEBUTTONDOWN:
                button_rect = self.begin_button_img.get_rect(center=(WIDTH // 2, 500))
                if button_rect.collidepoint(event.pos):
                    # self.click_sound.play()
                    self.state = "menu"
                    # 在事件处理中触发过渡
                    self.transition_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
                    while self.transition_rect.width > 0:
                        self.transition_rect.inflate_ip(-10, -10)
                        pygame.display.update()

            elif self.state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mouse_pos = (mouse_pos[0] + 0.5, mouse_pos[1] + 0.5)
                option_spacing = 200  # 选项间距增加
                total_width = (len(self.cat_options) - 1) * (option_spacing + CAT_SIZE) + CAT_SIZE  # 总宽度包含按钮
                start_x = (WIDTH - total_width) // 2
                # 容器的y坐标
                base_y = 300
                for i, cat in enumerate(self.cat_options):
                    pos_x = start_x + i * option_spacing
                    cat_rect = pygame.Rect(pos_x + CARD_WIDTH // 2 - BUTTON_SIZE // 2, base_y + CAT_SIZE + 60, BUTTON_SIZE, BUTTON_SIZE)
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
                    if self.launch_power > 5:
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
                    else:
                        self.level = 1
                        self.balls_left = 3
                        self.score = 0
                        self.state = "menu"
        return True

    def update(self):
        if self.state != "playing":
            return

        if self.transition_rect:
            self.transition_rect.inflate_ip(-20, -20)
            if self.transition_rect.width <= 0:
                self.transition_rect = None

        if self.charging:
            self.launch_power = min(self.launch_power + 0.5, self.max_power)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.cat_ball.x
            dy = mouse_y - self.cat_ball.y
            angle = math.atan2(dy, dx)
            power = min(self.launch_power, self.max_power)

            self.aim_line = []
            steps = 20 + self.selected_cat.traits["aim_assist"] * 10
            for i in range(1, steps):
                t = i * 0.1
                vx = power * math.cos(angle)
                vy = -power * math.sin(angle)
                x = self.cat_ball.x + vx * t
                y = self.cat_ball.y + vy * t + 0.5 * 0.3 * t * t
                if x < 0 or x > WIDTH or y > HEIGHT:
                    break
                self.aim_line.append((x, y))

        if self.cat_ball:
            self.cat_ball.update()
            self.cat_ball.is_colliding = False
            for obstacle in self.obstacles:
                if self.cat_ball.rect.colliderect(obstacle.rect):
                    self.cat_ball.is_colliding = True
                    self.cat_ball.collision_count += 1
                    obstacle.apply_effect(self.cat_ball)
                    if obstacle.effect != "stick":
                        if abs(self.cat_ball.rect.centerx - obstacle.rect.centerx) > abs(
                                self.cat_ball.rect.centery - obstacle.rect.centery):
                            self.cat_ball.velocity[0] *= -0.7
                        else:
                            self.cat_ball.velocity[1] *= -0.7

            for target in self.targets:
                if not target.is_achieved and self.cat_ball.rect.colliderect(target.rect):
                    target.is_achieved = True
                    self.score += 100 * self.level

            if all(target.is_achieved for target in self.targets):
                self.state = "level_complete"
            elif self.balls_left <= 0 and not self.cat_ball.is_launched:
                self.state = "game_over"

    def draw(self):
        if self.screen is None:  # 检查屏幕是否有效
            return
        self.screen.blit(self.begin_background, (0, 0))

        if self.transition_rect:
            pygame.draw.rect(self.screen, BLACK, self.transition_rect)

        # 新增开始界面绘制
        if self.state == "begin":
            # 绘制动态背景
            self.screen.blit(self.begin_background, (0, 0))

            # 生成星光粒子（每帧生成）
            if random.random() < 0.2:
                self.spawn_particles("star")

            # 绘制所有粒子
            for p in self.particles:
                p.draw(self.screen)

            # 绘制开始按钮（带点击反馈）
            button_rect = self.begin_button_img.get_rect(center=(WIDTH // 2, 500))
            self.screen.blit(self.begin_button_img, button_rect)

            # 按钮悬停时的粒子喷发效果[5](@ref)
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                self.spawn_particles("sparkle")

            # # 标题文字动画
            # title_text = self.big_font.render("猫咪弹珠大冒险", True, (255, 215, 0))
            # pulsate = abs(pygame.time.get_ticks() % 1000 - 500) / 500  # 呼吸效果
            # scaled_title = pygame.transform.smoothscale(title_text,
            #                                             (int(title_text.get_width() * (1 + pulsate * 0.1)),
            #                                              int(title_text.get_height() * (1 + pulsate * 0.1))))
            # self.screen.blit(scaled_title, (WIDTH // 2 - scaled_title.get_width() // 2, 200))

            # 开发者信息
            credit_text = self.font.render("点击开始游戏", True, WHITE)
            self.screen.blit(credit_text, (WIDTH // 2 - credit_text.get_width() // 2, 550))


        # 菜单绘制逻辑
        elif self.state == "menu":
            self.screen.blit(self.menu_background, (0, 0))

            # # 菜单主面板
            # menu_bg = pygame.Surface((WIDTH - 200, 500), pygame.SRCALPHA)
            # menu_bg.fill((30, 30, 30, 220))
            # self.screen.blit(menu_bg, (100, 50))
            #
            # # 装饰边框
            # pygame.draw.rect(self.screen, (100, 100, 100),
            #                  (95, 45, WIDTH - 190, 510), 5, border_radius=15)

            # 角色选择提示
            instruction = self.big_font.render("选择你的猫咪:", True, WHITE)
            self.screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 200))

            # 动态布局计算
            option_spacing = 200  # 选项间距增加
            total_width = (len(self.cat_options) - 1) * (option_spacing + CAT_SIZE) + CAT_SIZE # 总宽度包含按钮
            start_x = (WIDTH - total_width) // 2
            base_y = 300  # 基础Y坐标

            # 绘制角色选项
            for i, cat in enumerate(self.cat_options):
                pos_x = start_x + i * option_spacing

                # 猫咪卡片容器（增加高度容纳下方按钮）
                pygame.draw.rect(self.screen, (245, 245, 245, 50),
                                 (pos_x, base_y, CARD_WIDTH, CARD_HEIGHT),
                                 border_radius=10)

                # 角色图片区域
                img_pos = (pos_x + CARD_WIDTH // 2 - CAT_SIZE // 2, base_y + 20)  # 居中显示
                self.screen.blit(cat.image_menu, img_pos)

                # 选择按钮（位于图片下方40px处）
                button_y = base_y + CAT_SIZE + 60  # 图片高度 + 间隔60
                button_rect = self.select_button.get_rect(topleft=(pos_x + CARD_WIDTH // 2 - BUTTON_SIZE // 2, button_y))
                self.screen.blit(self.select_button, button_rect)

                # 按钮文字
                text = self.font.render("选择", True, WHITE)
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)

                # 属性显示（下移避开按钮区域）
                # 力量进度条
                bar_x = pos_x + CARD_WIDTH // 2 - BAR_WIDTH // 2
                bar_y = button_y + 100  # 按钮下方间隔
                pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT))
                pygame.draw.rect(self.screen, LIGHT_PINK,
                                 (bar_x, bar_y, BAR_WIDTH * (cat.traits["power"] / 10), BAR_HEIGHT))

                # 文字属性（两列式布局）
                traits_positions = [
                    (bar_x, bar_y + 20),  # 力量数值
                    (bar_x, bar_y + 50)  # 辅助属性
                ]
                for j, (text, pos) in enumerate(zip(
                        [f"力量: {cat.traits['power']}", f"辅助: {cat.traits['aim_assist']}"],
                        traits_positions
                )):
                    text_surf = self.font.render(text, True, (200, 200, 200))
                    self.screen.blit(text_surf, pos)

        elif self.state == "playing":
            #self.screen.blit(self.level1_background, (0, 0))
            self.screen.blit(self.bgs, (0, 0))
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            for target in self.targets:
                target.draw(self.screen)
            if self.cat_ball:

                self.cat_ball.draw(self.screen)

            if self.charging and self.selected_cat.traits["aim_assist"] > 0:
                for i in range(len(self.aim_line)-1):
                    pygame.draw.line(self.screen, (100,100,255),
                                    self.aim_line[i], self.aim_line[i+1], 5)

            #绘制冰箱图层
            # select_bingxiang = get_img_dir("img/screen_3/level/01", "01_bingxiang.png", 1280, 720)
            # self.screen.blit(select_bingxiang, (0, -0))
            #select_di = get_img_dir("img/screen_3/level/01", "01_di.png", 1280, 720)
            #self.screen.blit(select_di, (0, -0))

            # 绘制蓄力条
            if self.charging:
                power_width = 200 * (self.launch_power / self.max_power)
                pygame.draw.rect(self.screen, RED, (50, 50, power_width, 20))
                pygame.draw.rect(self.screen, BLACK, (50, 50, 200, 20), 2)
                power_text = self.font.render(f"力度: {int(self.launch_power)}", True, BLACK)
                self.screen.blit(power_text, (60, 55))

            # 绘制游戏信息
            level_text = self.font.render(f"关卡: {self.level}", True, BLACK)
            self.screen.blit(level_text, (WIDTH - 150, 20))

            balls_text = self.font.render(f"剩余弹珠: {self.balls_left}", True, BLACK)
            self.screen.blit(balls_text, (WIDTH - 150, 50))

            score_text = self.font.render(f"分数: {self.score}", True, BLACK)
            self.screen.blit(score_text, (WIDTH - 150, 80))

        elif self.state == "level_complete":
            # 绘制关卡完成界面
            complete_text = self.big_font.render(f"关卡 {self.level} 完成!", True, BLACK)
            self.screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 2 - 50))

            if self.level < self.max_levels:
                next_text = self.font.render("点击继续下一关", True, BLACK)
            else:
                next_text = self.font.render("恭喜通关! 点击返回主菜单", True, BLACK)
            self.screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 20))

        elif self.state == "game_over":
            # 绘制游戏结束界面
            self.screen.blit(self.gameOver_background, (0, 0))
            over_text = self.big_font.render("游戏结束", True, BLACK)
            self.screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))

            score_text = self.font.render(f"最终分数: {self.score}", True, BLACK)
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

            restart_text = self.font.render("点击返回主菜单", True, BLACK)
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)