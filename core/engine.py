import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.scene = None

    def change_scene(self, scene):
        self.scene = scene

    def run(self, start_scene):
        self.change_scene(start_scene)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.scene:
                    self.scene.handle_event(event)

            if self.scene:
                self.scene.update()
                self.scene.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
