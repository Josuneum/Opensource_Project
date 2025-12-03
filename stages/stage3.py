import pygame
from core.button import Button

class Stage3:
    def __init__(self, engine):
        self.engine = engine
        self.buttons = [
            Button(15, 15, 40, 40, "Back", 15, self.back_to_start)
        ]

    def back_to_start(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))
        
    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 255))  # 파란 화면 표시
        for btn in self.buttons:
            btn.draw(screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
