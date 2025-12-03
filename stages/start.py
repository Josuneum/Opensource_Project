import pygame
from core.button import Button

class StartScreen:
    def __init__(self, engine):
        self.engine = engine
        self.start_button = Button(300, 380, 200, 60, "Start", 40, self.start_game)
        self.end_button = Button(300, 460, 200, 60, "Good bye", 40, self.end_game)

    def start_game(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))

    def end_game(self):
        pygame.quit()
        exit()

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((50, 50, 50))
        self.start_button.draw(screen)
        self.end_button.draw(screen)

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.end_button.handle_event(event)
