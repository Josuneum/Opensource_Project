import pygame
from core.button import Button

class StageSelectScreen:
    def __init__(self, engine):
        self.engine = engine
        self.buttons = [
            Button(300, 200, 200, 60, "Stage 1", 40, self.start_stage1),
            Button(300, 300, 200, 60, "Stage 2", 40, self.start_stage2),
            Button(300, 400, 200, 60, "Stage 3", 40,self.start_stage3),
            Button(15, 15, 40, 40, "Back", 15, self.back_to_start)
        ]

    def start_stage1(self):
        from .stage1 import Stage1
        self.engine.change_scene(Stage1(self.engine))

    def start_stage2(self):
        from .stage2 import Stage2
        self.engine.change_scene(Stage2(self.engine))

    def start_stage3(self):
        from .stage3 import Stage3
        self.engine.change_scene(Stage3(self.engine))

    def back_to_start(self):
        from .start import StartScreen
        self.engine.change_scene(StartScreen(self.engine))

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((100, 100, 100))
        for btn in self.buttons:
            btn.draw(screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
