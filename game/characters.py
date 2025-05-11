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
        self.image = self.create_cat_image()
        self.traits = self.set_traits()

    def create_cat_image(self):
        file_names = {
            CatType.ORANGE: "b_cat.png",
            CatType.GRAY: "buou_cat.png",
            CatType.WHITE: "jumao.png"
        }
        color_map = {
            CatType.ORANGE: ORANGE,
            CatType.GRAY: GRAY,
            CatType.WHITE: WHITE
        }

        image = get_img_dir("img/screen_menu", file_names[self.type], self.size, self.size)
        if is_fallback(image):
            image = create_pixel_cat(color_map[self.type])
        return image

    def set_traits(self):
        base_traits = {
            "power": 1.0,
            "aim_assist": 0,
            "bounce": 0,
            "special": None
        }
        type_traits = {
            CatType.ORANGE: {
                "power": 1.5,
                "aim_assist": 1,
                "special": "power_shot"
            },
            CatType.GRAY: {
                "aim_assist": 3,
                "bounce": 2,
                "special": "wall_jump"
            },
            CatType.WHITE: {
                "power": 0.8,
                "aim_assist": 2,
                "special": "quick_charge"
            }
        }
        base_traits.update(type_traits[self.type])
        return base_traits