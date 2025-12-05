import pygame
from core.button import Button

class Stage1DifficultyScreen:
    def __init__(self, engine):
        self.engine = engine
        self.buttons = []

        # 난이도 선택 버튼
        easy_btn = Button(300, 200, 200, 60, "Easy", 40,
                          callback=lambda: self.start_stage1(1))
        normal_btn = Button(300, 300, 200, 60, "Normal", 40,
                            callback=lambda: self.start_stage1(2))
        hard_btn = Button(300, 400, 200, 60, "Hard", 40,
                          callback=lambda: self.start_stage1(3))

        back_btn = Button(15, 15, 40, 40, "Back", 15,
                          callback=self.back_to_select)

        self.buttons.extend([easy_btn, normal_btn, hard_btn, back_btn])

    def start_stage1(self, difficulty):
        from .stage1 import Stage1
        self.engine.change_scene(Stage1(self.engine, difficulty=difficulty))

    def back_to_select(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((50, 50, 50))

        font = pygame.font.SysFont(None, 50)
        text = font.render("Select Difficulty", True, (255, 255, 255))
        screen.blit(text, (250, 120))

        for btn in self.buttons:
            btn.draw(screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
