import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from game.game_logic import CatBounceGame

def main():
    pygame.init()
    game = CatBounceGame()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()