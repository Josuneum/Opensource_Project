import pygame
from core.button import Button

class StartScreen:
    def __init__(self, engine):
        self.engine = engine
        self.button = Button(300, 250, 200, 60, "Start", self.start_game)

    def start_game(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((50, 50, 50))
        self.button.draw(screen)

    def handle_event(self, event):
        self.button.handle_event(event)
