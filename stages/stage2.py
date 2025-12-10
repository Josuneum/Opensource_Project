import pygame
from math import *
import random
from core.button import Button

class Stage2:
    def __init__(self, engine):
        self.engine = engine

        # 버튼 UI 위치 변경: Back + Check를 왼쪽 세로 배치
        self.buttons = [
            Button(15, 15, 60, 40, "Back", 18, self.back_to_start),
            Button(15, 70, 60, 40, "Check", 18, self.check_answer)
        ]

        self.function_name = "tan(x)"

        # 문제 그래프
        self.problems = [
            ("sin(x)", lambda x: sin(x)),
            ("cos(x)", lambda x: cos(x)),
            ("tan(x)", lambda x: tan(x)),
            ("x^2",    lambda x: x*x),
            ("x^3",    lambda x: x*x*x),
            ("exp(x)/5", lambda x: exp(x)/5),
            ("ln(x+6)", lambda x: log(x+6)),  # x > -6에서 정의됨
            ("abs(x)", lambda x: abs(x)),
            ]
        self.function_name, self.current_function = random.choice(self.problems)

        # 정답 그래프 렌더러
        self.graph = GraphRenderer(width=600, height=600, size=20, rate=1000,
                           func=self.current_function)

        # 플레이어 그래프 (여러 선을 저장)
        self.player_lines = []
        self.current_line = []
        self.drawing = False

        # 정답 오버레이 표시 여부
        self.show_answer_overlay = False

        # 정확도 결과
        self.accuracy = None

    def back_to_start(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))

    # ---------------------------
    # Check 버튼 → 정답 비교
    # ---------------------------
    def check_answer(self):
        self.show_answer_overlay = True
        self.accuracy = self.compare_graphs()

    # ---------------------------
    # 정확도 비교 알고리즘
    # ---------------------------
    def compare_graphs(self):

        all_points = []
        for line in self.player_lines:
            all_points.extend(line)

        if len(all_points) < 5:
            return 0

        player_math = []
        for sx, sy in all_points:
            mx = (sx - self.graph_center_x - self.graph.WIDTH/2) / (self.graph.WIDTH / self.graph.SIZE)
            my = -(sy - self.graph_center_y - self.graph.HEIGHT/2) / (self.graph.HEIGHT / self.graph.SIZE)
            player_math.append((mx, my))

        total_error = 0
        n = 0

        for mx, my in player_math:
            try:
                correct_y = tan(mx)
            except:
                continue

            if abs(correct_y) > self.graph.SIZE:
                continue

            total_error += abs(correct_y - my)
            n += 1

        if n == 0:
            return 0

        avg_error = total_error / n
        accuracy = max(0, 100 - avg_error * 3)

        return round(accuracy, 2)

    # ---------------------------
    def update(self):
        pass

    # ---------------------------
    def draw(self, screen):

        screen.fill((20, 20, 20))

        # 플레이어 그래프 영역 중앙 위치 계산
        self.graph_center_x = screen.get_width() // 2 - self.graph.WIDTH // 2
        self.graph_center_y = screen.get_height() // 2 - self.graph.HEIGHT // 2

        # 그래프 배경
        pygame.draw.rect(screen, (50, 50, 50),
                         (self.graph_center_x, self.graph_center_y, self.graph.WIDTH, self.graph.HEIGHT))

        # 축 + grid 그리기
        self.graph.draw_axes(screen, self.graph_center_x, self.graph_center_y)

        # 플레이어 선 그리기
        for line in self.player_lines:
            if len(line) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, line, 2)

        if len(self.current_line) > 1:
            pygame.draw.lines(screen, (0, 255, 0), False, self.current_line, 2)

        # 정답 오버레이
        if self.show_answer_overlay:
            self.graph.draw_transparent(screen, self.graph_center_x, self.graph_center_y)

        # 정확도 텍스트
        font = pygame.font.Font(None, 28)
        if self.accuracy is not None:
            small_font = pygame.font.Font(None, 24)
            acc = small_font.render(f"Accuracy: {self.accuracy}%", True, (255, 255, 0))
            screen.blit(acc, (self.graph_center_x + 10, self.graph_center_y + 10))

        # 버튼 그리기
        for btn in self.buttons:
            btn.draw(screen)

        # 함수 이름을 Check 버튼 아래 표시
        fname = font.render(self.function_name, True, (255, 255, 255))
        screen.blit(fname, (15, 130))

    # ---------------------------
    def handle_event(self, event):

        # 버튼 처리
        for btn in self.buttons:
            btn.handle_event(event)

        graph_rect = pygame.Rect(self.graph_center_x, self.graph_center_y,
                                 self.graph.WIDTH, self.graph.HEIGHT)

        # 드로잉 시작
        if event.type == pygame.MOUSEBUTTONDOWN:
            if graph_rect.collidepoint(event.pos):
                self.drawing = True
                self.current_line = [event.pos]

        # 드로잉 끝
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.drawing:
                self.drawing = False
                if len(self.current_line) > 1:
                    self.player_lines.append(self.current_line)
                self.current_line = []

        # 드로잉 중
        elif event.type == pygame.MOUSEMOTION and self.drawing:
            if graph_rect.collidepoint(event.pos):
                self.current_line.append(event.pos)


# ===================================================================
# GraphRenderer (축 + grid 기능 추가)
# https://github.com/las-r/graphing-calc-pygame?tab=readme-ov-file 를 참고하여 수정
# ===================================================================
class GraphRenderer:
    def __init__(self, width=600, height=600, size=20, rate=1000, func=None):
        self.WIDTH = width
        self.HEIGHT = height
        self.SIZE = size
        self.RATE = rate
        self.func = func
        self.compute_points()

        self.GRID = (80, 80, 80)
        self.AXES = (255, 255, 255)
        self.FNC = (255, 0, 0)

    def compute_points(self):
        self.fp = []
        cx = -self.SIZE / 2
        while cx <= self.SIZE / 2:
            try:
                y = self.func(cx)
                if -self.SIZE/2 <= y <= self.SIZE/2:
                    self.fp.append((cx, y))
            except:
                pass
            cx += 1 / self.RATE

    # 화면 세팅 변환
    def transform(self, x, y):
        sx = self.WIDTH // 2 + x * (self.WIDTH / self.SIZE)
        sy = self.HEIGHT // 2 - y * (self.HEIGHT / self.SIZE)
        return int(sx), int(sy)

    # 축과 grid 그리기
    def draw_axes(self, screen, ox, oy):

        # grid
        for i in range(0, self.WIDTH, self.WIDTH // 10):
            pygame.draw.line(screen, self.GRID,
                             (ox + i, oy),
                             (ox + i, oy + self.HEIGHT), 1)

        for i in range(0, self.HEIGHT, self.HEIGHT // 10):
            pygame.draw.line(screen, self.GRID,
                             (ox, oy + i),
                             (ox + self.WIDTH, oy + i), 1)

        # x축
        pygame.draw.line(screen, self.AXES,
                         (ox, oy + self.HEIGHT // 2),
                         (ox + self.WIDTH, oy + self.HEIGHT // 2), 2)

        # y축
        pygame.draw.line(screen, self.AXES,
                         (ox + self.WIDTH // 2, oy),
                         (ox + self.WIDTH // 2, oy + self.HEIGHT), 2)

    # 정답 오버레이
    def draw_transparent(self, screen, ox, oy):

        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        for x, y in self.fp:
            sx, sy = self.transform(x, y)
            pygame.draw.circle(overlay, (255, 0, 0, 140), (sx, sy), 3)

        screen.blit(overlay, (ox, oy))
    def draw_axes(self, screen, ox, oy):

        grid_step_x = self.WIDTH // 10
        grid_step_y = self.HEIGHT // 10

        font = pygame.font.Font(None, 20)  # 아주 작은 글씨

        # ============================
        # Grid Lines
        # ============================
        for i in range(11):
            # vertical grid
            x = ox + i * grid_step_x
            pygame.draw.line(screen, self.GRID, (x, oy), (x, oy + self.HEIGHT), 1)

            # horizontal grid
            y = oy + i * grid_step_y
            pygame.draw.line(screen, self.GRID, (ox, y), (ox + self.WIDTH, y), 1)

        # ============================
        # Axes
        # ============================
        # x-axis
        pygame.draw.line(screen, self.AXES,
                     (ox, oy + self.HEIGHT // 2),
                     (ox + self.WIDTH, oy + self.HEIGHT // 2), 2)

        # y-axis
        pygame.draw.line(screen, self.AXES,
                     (ox + self.WIDTH // 2, oy),
                     (ox + self.WIDTH // 2, oy + self.HEIGHT), 2)

        # ============================
        # Tick Labels (축 값 표시)
        # ============================
        for i in range(11):
            # -------------------- X축 눈금 값 --------------------
            tick_x_val = (i - 5) * (self.SIZE / 10)
            x_pos = ox + i * grid_step_x

            label = font.render(f"{tick_x_val:.1f}", True, (180, 180, 180))
            screen.blit(label, (x_pos - label.get_width()//2, oy + self.HEIGHT//2 + 3))

            # -------------------- Y축 눈금 값 --------------------
            tick_y_val = (5 - i) * (self.SIZE / 10)
            y_pos = oy + i * grid_step_y

            label = font.render(f"{tick_y_val:.1f}", True, (180, 180, 180))
            screen.blit(label, (ox + self.WIDTH//2 + 3, y_pos - label.get_height()//2))
