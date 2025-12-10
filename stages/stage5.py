import pygame
import sys
import os
import time
import numpy as np
import librosa

from core.button import Button
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

# -------------------------------------------------------
# 상대 경로 지정
# -------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)                   
PROJECT_ROOT = os.path.dirname(BASE_DIR)               

AUDIO_DIR = os.path.join(PROJECT_ROOT, "assets", "audio")
ASSET_DIR = os.path.join(PROJECT_ROOT, "assets")       
SONG_PATH = os.path.join(AUDIO_DIR, "song.wav")

# -------------------------------------------------------
# 화면 설정
# -------------------------------------------------------
WIDTH = SCREEN_WIDTH     # 800
HEIGHT = SCREEN_HEIGHT   # 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (15, 15, 20)
GRAY = (120, 120, 120)
GREEN = (0, 220, 0)
RED = (220, 60, 60)
BLUE = (80, 160, 255)
YELLOW = (250, 220, 50)


# -------------------------------------------------------
# Note 클래스
# -------------------------------------------------------
class Note:
    def __init__(self, target_time, spawn_time, x, y_start, y_hit, speed):
        self.target_time = target_time
        self.spawn_time = spawn_time
        self.x = x
        self.y = y_start
        self.y_start = y_start
        self.y_hit = y_hit
        self.speed = speed
        self.active = False
        self.judged = False

    def update(self, song_time):
        if self.judged:
            return

        if not self.active:
            if song_time >= self.spawn_time:
                self.active = True
            else:
                return

        dt = song_time - self.spawn_time
        self.y = self.y_start + self.speed * dt

        if self.y > self.y_hit + 80:
            self.judged = True

    def draw(self, screen):
        if not self.active or self.judged:
            return

        width = 80
        height = 25
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (self.x, int(self.y))
        pygame.draw.rect(screen, BLUE, rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)


# -------------------------------------------------------
# Beat 추출 (librosa)
# -------------------------------------------------------
def extract_beats(audio_path, max_beats=80, mode="onset"):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"오디오 파일 없음: {audio_path}")

    print("오디오 로딩:", audio_path)
    y, sr = librosa.load(audio_path, sr=None)
    print(f"SampleRate={sr}, Length={len(y)/sr:.2f}s")

    if mode == "beat":
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, (list, np.ndarray)):
            tempo_val = float(tempo[0])
        else:
            tempo_val = float(tempo)
        print(f"[BEAT] BPM={tempo_val:.1f}")
        times = librosa.frames_to_time(beat_frames, sr=sr)
    else:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            backtrack=True
        )
        times = librosa.frames_to_time(onset_frames, sr=sr)
        print(f"[ONSET] 검출 타격 수: {len(times)}")

    # 너무 많으면 2개 중 1개만 사용
    times = times[::2]

    if len(times) > max_beats:
        times = times[:max_beats]

    print("사용할 노트 수:", len(times))
    return times


# -------------------------------------------------------
# Font util
# -------------------------------------------------------
def load_font(size):
    return pygame.font.SysFont("malgungothic", size)


def draw_text_center(surface, text, size, color, y):
    font = load_font(size)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(WIDTH // 2, y))
    surface.blit(img, rect)


# -------------------------------------------------------
# Stage5 Scene 클래스
# -------------------------------------------------------
class Stage5:
    def __init__(self, engine):
        self.engine = engine

        # Back 버튼
        self.back_btn = Button(15, 15, 60, 40, "Back", 20, self.back_to_menu)

        # 로딩 중 표시용 플래그
        self.loading = True
        self.error_message = ""
        self.notes = []
        self.playing = False
        self.start_time = None

        # 판정
        self.HIT_WINDOWS = {
            "PERFECT": 0.06,
            "GREAT": 0.12,
            "GOOD": 0.20,
        }
        self.last_judge_text = ""
        self.last_judge_color = WHITE
        self.last_judge_time = 0.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0

        # 먼저 비트 분석 시도
        try:
            self.beat_times = extract_beats(SONG_PATH)
            self.setup_notes()
        except Exception as e:
            self.error_message = str(e)

        self.loading = False

    # ---------------------------------------------------
    # Back 버튼 기능
    # ---------------------------------------------------
    def back_to_menu(self):
        from .select import StageSelectScreen
        self.engine.change_scene(StageSelectScreen(self.engine))

    # ---------------------------------------------------
    # 노트 구성
    # ---------------------------------------------------
    def setup_notes(self):
        y_start = -40
        y_hit = HEIGHT - 120
        travel_time = 1.2
        speed = (y_hit - y_start) / travel_time
        x_lane = WIDTH // 2

        self.notes = []
        for t in self.beat_times:
            spawn_time = t - travel_time
            if spawn_time < 0:
                spawn_time = 0
            self.notes.append(
                Note(t, spawn_time, x_lane, y_start, y_hit, speed)
            )

    # ---------------------------------------------------
    # Pygame Event
    # ---------------------------------------------------
    def handle_event(self, event):
        self.back_btn.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 판정 or 곡 시작
                if not self.playing:
                    self.start_song()
                else:
                    self.try_judge()
            elif event.key == pygame.K_ESCAPE:
                self.back_to_menu()

    # ---------------------------------------------------
    # 곡 시작
    # ---------------------------------------------------
    def start_song(self):
        if not os.path.exists(SONG_PATH):
            self.error_message = f"오디오 파일 없음: {SONG_PATH}"
            return

        pygame.mixer.music.load(SONG_PATH)
        pygame.mixer.music.play()
        self.playing = True
        self.start_time = time.time()

        # 초기화
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.last_judge_text = ""

        # 노트 상태 초기화
        for n in self.notes:
            n.judged = False
            n.active = False
            n.y = n.y_start

    # ---------------------------------------------------
    # 판정
    # ---------------------------------------------------
    def try_judge(self):
        if not self.playing:
            return

        song_time = time.time() - self.start_time

        cand = None
        best_delta = 999
        for note in self.notes:
            if note.judged:
                continue
            if note.target_time - song_time > 0.5:
                continue

            delta = abs(song_time - note.target_time)
            if delta < best_delta:
                best_delta = delta
                cand = note

        if cand is None:
            self.judge_result("MISS", RED, 0)
            return

        if best_delta <= self.HIT_WINDOWS["PERFECT"]:
            self.judge_result("PERFECT", YELLOW, 300)
            cand.judged = True
        elif best_delta <= self.HIT_WINDOWS["GREAT"]:
            self.judge_result("GREAT", GREEN, 200)
            cand.judged = True
        elif best_delta <= self.HIT_WINDOWS["GOOD"]:
            self.judge_result("GOOD", BLUE, 100)
            cand.judged = True
        else:
            self.judge_result("MISS", RED, 0)

    def judge_result(self, text, color, add_score):
        if text == "MISS":
            self.combo = 0
        else:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += add_score

        self.last_judge_text = text
        self.last_judge_color = color
        self.last_judge_time = time.time()

    # ---------------------------------------------------
    # Update
    # ---------------------------------------------------
    def update(self):
        if self.loading or self.error_message:
            return

        if self.playing:
            song_time = time.time() - self.start_time

            # 노트 업데이트
            for note in self.notes:
                before = note.judged
                note.update(song_time)
                if not before and note.judged and note.y > note.y_hit + 80:
                    self.judge_result("MISS", RED, 0)

            # 곡 종료 체크
            if not pygame.mixer.music.get_busy():
                self.playing = False

    # ---------------------------------------------------
    # Draw
    # ---------------------------------------------------
    def draw(self, screen):
        screen.fill(BLACK)
        self.back_btn.draw(screen)

        if self.loading:
            draw_text_center(screen, "비트 분석 중...", 40, WHITE, HEIGHT // 2)
            return

        if self.error_message:
            draw_text_center(screen, f"에러: {self.error_message}", 24, RED, HEIGHT // 2)
            return

        # 판정선
        pygame.draw.line(screen, GRAY, (0, HEIGHT - 120), (WIDTH, HEIGHT - 120), 3)
        pygame.draw.rect(screen, GRAY, (WIDTH//2 - 60, HEIGHT - 140, 120, 40), 2, border_radius=8)
        draw_text_center(screen, "HIT", 24, GRAY, HEIGHT - 120)

        # 노트 표시
        for note in self.notes:
            note.draw(screen)

        # 점수
        font = load_font(24)
        screen.blit(font.render(f"Score: {self.score}", True, WHITE), (20, 50))
        screen.blit(font.render(f"Combo: {self.combo}", True, WHITE), (20, 80))
        screen.blit(font.render(f"Max Combo: {self.max_combo}", True, WHITE), (20, 110))

        # 판정 텍스트
        if self.last_judge_text and (time.time() - self.last_judge_time) < 1.0:
            draw_text_center(screen, self.last_judge_text, 36, self.last_judge_color, HEIGHT // 2)

        # 곡이 끝났을 때
        if not self.playing:
            draw_text_center(screen, "SPACE: 다시 플레이 | ESC: 뒤로가기", 22, GRAY, HEIGHT - 40)
