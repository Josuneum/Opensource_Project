import pygame
from core.button import Button

class StageSelectScreen:
    def __init__(self, engine):
        self.engine = engine
        self.buttons = [
            Button(300, 100, 200, 60, "Stage 1", 40, self.start_stage1),
            Button(300, 170, 200, 60, "Stage 2", 40, self.start_stage2),
            Button(300, 240, 200, 60, "Stage 3", 40,self.start_stage3),
            Button(300, 310, 200, 60, "Stage 4", 40, self.start_stage4),
            Button(300, 380, 200, 60, "Stage 5", 40, self.start_stage5),
            Button(15, 15, 40, 40, "Back", 15, self.back_to_start)
        ]

    def start_stage1(self):
        from .stage1_difficulty import Stage1DifficultyScreen
        self.engine.change_scene(Stage1DifficultyScreen(self.engine))

    def start_stage2(self):
        from .stage2 import Stage2
        self.engine.change_scene(Stage2(self.engine))

    def start_stage3(self):
        from .stage3 import Stage3
        self.engine.change_scene(Stage3(self.engine))

    def start_stage4(self):
        from .stage4 import Stage4
        self.engine.change_scene(Stage4(self.engine))

    def start_stage5(self):
        from .stage5 import Stage5
        self.engine.change_scene(Stage5(self.engine))

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
