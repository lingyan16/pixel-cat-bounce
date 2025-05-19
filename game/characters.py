from enum import Enum
from constants import ORANGE, GRAY, WHITE, CAT_SIZE
from game.utils import get_img_dir, create_pixel_cat, is_fallback


class CatType(Enum):  # 定义独立的枚举类
    ORANGE = 1
    GRAY = 2
    WHITE = 3


class CatCharacter:
    def __init__(self, cat_type: CatType):  # 使用独立枚举类
        self.type = cat_type
        self.size = CAT_SIZE
        self.image_ball = self.create_cat_image_ball()
        self.image_menu = self.create_cat_image_menu()
        self.traits = self.set_traits()

    def create_cat_image_ball(self):
        file_names = {
            CatType.ORANGE: "ball_b.png",
            CatType.GRAY: "ball_buou.png",
            CatType.WHITE: "ball_ju.png"
        }
        color_map = {
            CatType.ORANGE: ORANGE,
            CatType.GRAY: GRAY,
            CatType.WHITE: WHITE
        }

        image = get_img_dir("img/screen_3/cat_ball", file_names[self.type], self.size, self.size)
        if is_fallback(image):
            image = create_pixel_cat(color_map[self.type])
        return image

    def create_cat_image_menu(self):
        file_names = {
            CatType.ORANGE: "cat_b.png",
            CatType.GRAY: "cat_buou.png",
            CatType.WHITE: "cat_ju.png"
        }
        color_map = {
            CatType.ORANGE: ORANGE,
            CatType.GRAY: GRAY,
            CatType.WHITE: WHITE
        }

        image = get_img_dir("img/screen_3/cat_ball", file_names[self.type], self.size, self.size)
        if is_fallback(image):
            image = create_pixel_cat(color_map[self.type])
        return image

    def set_traits(self):
        base_traits = {
            "power": 1.0,
            "aim_assist": 0,
            "special": None
        }
        type_traits = {
            CatType.ORANGE: {
                "power": 1.6,
                "aim_assist": 1,
                "special": "power_shot"
            },
            CatType.GRAY: {
                "power": 1.3,
                "aim_assist": 3,
                "special": "wall_jump"
            },
            CatType.WHITE: {
                "power": 1,
                "aim_assist": 2,
                "special": "quick_charge"
            }
        }
        base_traits.update(type_traits[self.type])
        return base_traits