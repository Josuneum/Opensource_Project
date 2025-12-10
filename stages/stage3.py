# Conway's Game of Life 기반 생존 게임, 아래의 오픈소스를 참고하여 수정:
# https://github.com/marcpaulo15/game_of_life

import pygame
import random
import numpy as np
from core.button import Button
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

CELL = 20
GRID_W = 20
GRID_H = 20
BOARD_SIZE = GRID_W * CELL   # 400px board

SCREEN_W = SCREEN_WIDTH
SCREEN_H = SCREEN_HEIGHT

OFFSET_X = (SCREEN_W - BOARD_SIZE) // 2
OFFSET_Y = (SCREEN_H - BOARD_SIZE) // 2


class Stage3:
    def __init__(self, engine):
        self.engine = engine
        self.buttons = [
            Button(15, 15, 60, 40, "Back", 18, self.back_to_start)
        ]

        # Universe & Player 초기화
        self.universe = np.zeros((GRID_H, GRID_W), dtype=int)
        self.random_seed(self.universe, density=0.25)

        self.player_x = GRID_H // 2
        self.player_y = GRID_W // 2

        # 턴 시스템
        self.survive_turns = 0
        self.target_turns = 20

        # 입력 쿨타임
        self.last_move_time = 0
        self.move_cooldown = 300  # 0.3초

        # 게임 상태
        self.is_clear = False
        self.is_dead = False

    # ================================================================
    # 버튼 콜백
    # ================================================================
    def back_to_start(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))


    # ================================================================
    # Game of Life 규칙
    # ================================================================
    def survival(self, x, y, universe):
        num = np.sum(universe[x-1:x+2, y-1:y+2]) - universe[x, y]
        if universe[x, y] == 1:
            return 1 if 2 <= num <= 3 else 0
        else:
            return 1 if num == 3 else 0

    def generation(self, universe, player_pos):
        px, py = player_pos
        new_u = universe.copy()

        for i in range(GRID_H):
            for j in range(GRID_W):
                if (i, j) == (px, py):  # 플레이어 위치는 Life에서 제외
                    new_u[i, j] = 0
                    continue
                new_u[i, j] = self.survival(i, j, universe)

        return new_u

    def player_dead(self, universe, px, py):
        x1, x2 = max(px - 1, 0), min(px + 2, GRID_H)
        y1, y2 = max(py - 1, 0), min(py + 2, GRID_W)
        neighbors = np.sum(universe[x1:x2, y1:y2])
        return neighbors >= 4


    # ================================================================
    # 랜덤 Seed
    # ================================================================
    def random_seed(self, universe, density= 0.4):
        for i in range(GRID_H):
            for j in range(GRID_W):
                universe[i][j] = 1 if random.random() < density else 0


    # ================================================================
    # 업데이트 로직
    # ================================================================
    def update(self):

        # 이미 CLEAR 또는 DEAD 상태라면 게임 로직 중지
        if self.is_clear or self.is_dead:
            return

        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        moved = False

        # 이동 쿨타임 체크
        if now - self.last_move_time >= self.move_cooldown:

            if keys[pygame.K_LEFT] and self.player_y > 0:
                self.player_y -= 1
                moved = True

            elif keys[pygame.K_RIGHT] and self.player_y < GRID_W - 1:
                self.player_y += 1
                moved = True

            elif keys[pygame.K_UP] and self.player_x > 0:
                self.player_x -= 1
                moved = True

            elif keys[pygame.K_DOWN] and self.player_x < GRID_H - 1:
                self.player_x += 1
                moved = True

        # 이동 시 Life 1턴 진행
        if moved:
            self.last_move_time = now

            self.universe = self.generation(
                self.universe,
                (self.player_x, self.player_y)
            )
            self.survive_turns += 1

            # 사망 판정 ①: 과잉번식
            if self.player_dead(self.universe, self.player_x, self.player_y):
                self.is_dead = True
                return

            # 사망 판정 ②: Life가 플레이어 칸 생성
            if self.universe[self.player_x, self.player_y] == 1:
                self.is_dead = True
                return

            # 클리어 판정
            if self.survive_turns >= self.target_turns:
                self.is_clear = True


    # ================================================================
    # 화면 그리기
    # ================================================================
    def draw(self, screen):
        screen.fill((0, 0, 0))

        # Life 셀
        for i in range(GRID_H):
            for j in range(GRID_W):
                if self.universe[i, j] == 1:
                    pygame.draw.rect(
                        screen,
                        (150, 150, 255),
                        (OFFSET_X + j * CELL,
                         OFFSET_Y + i * CELL,
                         CELL, CELL)
                    )

        # 플레이어
        pygame.draw.rect(
            screen,
            (255, 60, 60),
            (OFFSET_X + self.player_y * CELL,
             OFFSET_Y + self.player_x * CELL,
             CELL, CELL)
        )

        # 생존 턴 텍스트
        font = pygame.font.SysFont(None, 24)
        msg = font.render(
            f"Survive: {self.survive_turns}/{self.target_turns}",
            True, (255, 255, 255)
        )
        screen.blit(msg, (OFFSET_X, OFFSET_Y + BOARD_SIZE + 10))

        # CLEAR 표시
        if self.is_clear:
            clear_font = pygame.font.SysFont(None, 70)
            text = clear_font.render("CLEAR!", True, (255, 255, 0))
            rect = text.get_rect(center=(SCREEN_W // 2, 80))
            screen.blit(text, rect)

        # DEAD 표시
        if self.is_dead:
            dead_font = pygame.font.SysFont(None, 70)
            text = dead_font.render("DEAD!", True, (255, 80, 80))
            rect = text.get_rect(center=(SCREEN_W // 2, 80))
            screen.blit(text, rect)

        # 버튼
        for btn in self.buttons:
            btn.draw(screen)


    # ================================================================
    # 이벤트 처리
    # ================================================================
    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
