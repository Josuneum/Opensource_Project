import pygame
import os
import csv
import random
import time
from tinydb import TinyDB
from rapidfuzz import fuzz

from core.button import Button
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

# --------------------------------------------------
# 상대 경로 설정
# --------------------------------------------------
BASE_DIR = os.path.dirname(__file__)               
PROJECT_ROOT = os.path.dirname(BASE_DIR)            
DATA_DIR = os.path.join(PROJECT_ROOT, "data") 
FONT_DIR = os.path.join(BASE_DIR, "fonts")
ASSET_DIR = os.path.join(BASE_DIR, "assets")


os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "mistakes.json")
db = TinyDB(DB_PATH)

# 화면 크기 통일
WIDTH = SCREEN_WIDTH
HEIGHT = SCREEN_HEIGHT
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
GRAY = (120, 120, 120)
GREEN = (0, 200, 0)
RED = (220, 50, 50)
BLUE = (50, 130, 230)


# --------------------------------------------------
# Font Loader
# --------------------------------------------------
def load_font(size):
    font_path = os.path.join(FONT_DIR, "NanumGothic.ttf")
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    return pygame.font.SysFont("malgungothic", size)


# --------------------------------------------------
# Draw Utility
# --------------------------------------------------
def draw_text(surface, text, font, color, x, y, center=True):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


# --------------------------------------------------
# Vocab Manager
# --------------------------------------------------
class VocabManager:
    def __init__(self, path=os.path.join(DATA_DIR, "vocab.csv")):
        self.vocabs = []
        self.load_csv(path)

    def load_csv(self, path):
        if not os.path.exists(path):
            print("[경고] vocab.csv 없음:", path)
            return

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row.get("word", "").strip()
                meaning = row.get("meaning", "").strip()
                if word and meaning:
                    self.vocabs.append({"word": word, "meaning": meaning})

        print("단어 로딩:", len(self.vocabs))

    def get_random_vocab(self):
        if not self.vocabs:
            return {"word": "[NO_VOCAB]", "meaning": "vocab.csv 확인 필요"}
        return random.choice(self.vocabs)


# --------------------------------------------------
# Game State
# --------------------------------------------------
class GameState:
    def __init__(self, vocab_manager, total_questions=10, mode="normal", review_list=None):
        self.vocab_manager = vocab_manager
        self.mode = mode
        self.review_list = review_list or []

        if self.mode == "review" and self.review_list:
            self.total_questions = len(self.review_list)
        else:
            self.total_questions = total_questions

        self.reset()

    def reset(self):
        self.typed_text = ""
        self.question_index = 1
        self.correct_count = 0
        self.wrong_count = 0
        self.wrong_list = []

        self.word_y = 60
        self.word_speed = 80.0

        self.running = True
        self.start_time = time.time()

        self.current = self._get_question_by_index(1)

    def _get_question_by_index(self, idx):
        if self.mode == "review" and self.review_list:
            if 1 <= idx <= len(self.review_list):
                return self.review_list[idx - 1]
            return None
        return self.vocab_manager.get_random_vocab()

    def next_question(self):
        if self.question_index >= self.total_questions:
            self.running = False
            return

        self.question_index += 1
        self.current = self._get_question_by_index(self.question_index)
        self.typed_text = ""
        self.word_y = 60

        if self.current is None:
            self.running = False

    def update_fall(self, dt):
        if not self.running or self.current is None:
            return

        self.word_y += self.word_speed * dt
        if self.word_y > HEIGHT - 120:
            self.register_answer(auto_timeout=True)

    def handle_char_input(self, ch):
        if ch.isprintable():
            self.typed_text += ch

    def handle_backspace(self):
        if self.typed_text:
            self.typed_text = self.typed_text[:-1]

    def _normalize(self, text):
        return text.strip().replace(" ", "")

    def _is_answer_correct(self, user_answer, meaning_str, auto_timeout):
        if auto_timeout:
            return False, 0.0

        user_norm = self._normalize(user_answer)
        if not user_norm:
            return False, 0.0

        candidates = [
            self._normalize(m)
            for m in meaning_str.split("/")
            if m.strip()
        ]

        best = 0.0
        for c in candidates:
            score = fuzz.ratio(user_norm, c)
            best = max(best, score)

        return best >= 80.0, best

    def register_answer(self, auto_timeout=False):
        if not self.current:
            self.running = False
            return

        meaning_str = self.current["meaning"]
        user_answer = self.typed_text

        ok, score = self._is_answer_correct(user_answer, meaning_str, auto_timeout)

        if ok:
            self.correct_count += 1
        else:
            self.wrong_count += 1
            wrong_item = {
                "word": self.current["word"],
                "meaning": meaning_str,
                "user_answer": user_answer.strip() if user_answer.strip() else "(미입력)",
                "similarity": score,
                "timestamp": time.time()
            }
            self.wrong_list.append(wrong_item)
            db.insert(wrong_item)

        self.next_question()


# --------------------------------------------------
# Stage4 Scene
# --------------------------------------------------
class Stage4:
    def __init__(self, engine):
        self.engine = engine

        # Back 버튼
        self.back_button = Button(15, 15, 60, 40, "Back", 20, self.back_to_menu)

        self.title_font = load_font(48)
        self.menu_font = load_font(24)
        self.small_font = load_font(18)
        self.answer_font = load_font(26)

        self.vocab_manager = VocabManager(os.path.join(DATA_DIR, "vocab.csv"))
        self.state = "menu"
        self.game_state = None
        self.menu_message = ""

    # -------------------------------
    # Scene control
    # -------------------------------
    def back_to_menu(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))

    # -------------------------------
    # Event handler
    # -------------------------------
    def handle_event(self, event):
        self.back_button.handle_event(event)

        if self.state == "menu":
            self._handle_menu_event(event)
        elif self.state == "game":
            self._handle_game_event(event)
        elif self.state == "result":
            self._handle_result_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game_state = GameState(self.vocab_manager, total_questions=10, mode="normal")
                self.state = "game"
            elif event.key == pygame.K_r:
                mistakes = db.all()
                if not mistakes:
                    self.menu_message = "저장된 오답이 없습니다."
                else:
                    review_list = [
                        {"word": m["word"], "meaning": m["meaning"]}
                        for m in mistakes
                    ]
                    self.game_state = GameState(self.vocab_manager, mode="review", review_list=review_list)
                    self.state = "game"

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game_state.register_answer(auto_timeout=False)
                if not self.game_state.running:
                    self.state = "result"
            elif event.key == pygame.K_BACKSPACE:
                self.game_state.handle_backspace()

        elif event.type == pygame.TEXTINPUT:
            self.game_state.handle_char_input(event.text)

    def _handle_result_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 동일 모드 재시작
                if self.game_state.mode == "normal":
                    self.game_state = GameState(self.vocab_manager, total_questions=10, mode="normal")
                else:
                    mistakes = db.all()
                    if mistakes:
                        review_list = [
                            {"word": m["word"], "meaning": m["meaning"]}
                            for m in mistakes
                        ]
                        self.game_state = GameState(self.vocab_manager, mode="review", review_list=review_list)
                    else:
                        self.menu_message = "오답 없음"
                        self.state = "menu"
                        return
                self.state = "game"

    # -------------------------------
    # Update
    # -------------------------------
    def update(self):
        if self.state == "game" and self.game_state and self.game_state.running:
            dt = self.engine.clock.get_time() / 1000.0
            self.game_state.update_fall(dt)
            if not self.game_state.running:
                self.state = "result"

    # -------------------------------
    # Draw
    # -------------------------------
    def draw(self, screen):
        screen.fill(BLACK)

        self.back_button.draw(screen)

        if self.state == "menu":
            self._draw_menu(screen)
        elif self.state == "game":
            self._draw_game(screen)
        elif self.state == "result":
            self._draw_result(screen)

    # -------------------------------
    # Drawing functions
    # -------------------------------
    def _draw_menu(self, screen):
        draw_text(screen, "영단어 뜻 맞추기 게임", self.title_font, WHITE, WIDTH//2, 150)
        draw_text(screen, "[SPACE] 일반 모드 시작", self.menu_font, GREEN, WIDTH//2, 260)
        draw_text(screen, "[R] 오답 복습 모드", self.menu_font, BLUE, WIDTH//2, 300)

        if self.menu_message:
            draw_text(screen, self.menu_message, self.small_font, RED, WIDTH//2, 350)

    def _draw_game(self, screen):
        gs = self.game_state

        draw_text(screen, f"{gs.question_index}/{gs.total_questions}", self.small_font, WHITE, 20, 70, center=False)
        draw_text(screen, f"맞음:{gs.correct_count}  틀림:{gs.wrong_count}",
                  self.small_font, WHITE, WIDTH - 180, 70, center=False)

        if gs.current:
            draw_text(screen, gs.current["word"], self.title_font, WHITE, WIDTH//2, int(gs.word_y))
        else:
            draw_text(screen, "(문제 없음)", self.menu_font, GRAY, WIDTH//2, HEIGHT//2)

        # 입력 창
        pygame.draw.rect(screen, (25, 25, 60), (80, HEIGHT - 120, WIDTH - 160, 60), border_radius=12)
        pygame.draw.rect(screen, BLUE, (80, HEIGHT - 120, WIDTH - 160, 60), 2, border_radius=12)

        draw_text(screen, "뜻:", self.small_font, GRAY, 100, HEIGHT - 90, center=False)
        draw_text(screen, gs.typed_text, self.answer_font, WHITE, 160, HEIGHT - 90, center=False)

    def _draw_result(self, screen):
        gs = self.game_state

        draw_text(screen, "결과", self.title_font, WHITE, WIDTH//2, 80)
        draw_text(screen, f"총 문제: {gs.total_questions}", self.menu_font, WHITE, WIDTH//2, 160)
        draw_text(screen, f"맞음: {gs.correct_count}", self.menu_font, GREEN, WIDTH//2, 200)
        draw_text(screen, f"틀림: {gs.wrong_count}", self.menu_font, RED, WIDTH//2, 240)

        draw_text(screen, "틀린 단어 목록", self.small_font, WHITE, WIDTH//2, 300)

        y = 330
        for item in gs.wrong_list[:5]:
            line = f"{item['word']} | 정답: {item['meaning']} | 입력: {item['user_answer']}"
            draw_text(screen, line, self.small_font, WHITE, WIDTH//2, y)
            y += 26

        draw_text(screen, "[SPACE] 다시 하기", self.small_font, BLUE, WIDTH//2, HEIGHT - 40)
