import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT
import cv2

class Stage1:
    def __init__(self, engine):
        self.engine = engine

        #플레이어가 움직이게 하는 검은 네모 모형
        self.player_image = "assets/images/black_rect.png"
        self.player = pygame.image.load(self.player_image)
        self.player_rect = self.player.get_rect()
        self.player_rect.centerx = SCREEN_WIDTH // 2 #위치 가로: 중앙, 세로에서 50px
        self.player_rect.bottom = SCREEN_HEIGHT - 50

        #플레이어가 먹을 빨간 네모
        self.eated_image = "assets/images/red_rect.png"
        self.eated = pygame.image.load(self.eated_image)
        self.eated_rect = self.eated.get_rect()
        self.eated_rect.centerx = SCREEN_WIDTH // 2
        self.eated_rect.bottom = SCREEN_HEIGHT // 2
        self.is_eated = False

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.player_rect.left > 0:
            self.player_rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.player_rect.right < SCREEN_WIDTH:
            self.player_rect.x += 5 
        if keys[pygame.K_UP] or keys[pygame.K_w] and self.player_rect.top > 0:
            self.player_rect.y -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and self.player_rect.bottom < SCREEN_HEIGHT:
            self.player_rect.y += 5

        if self.player_rect.colliderect(self.eated_rect):
            img1 = cv2.imread(self.player_image)
            img2 = cv2.imread(self.eated_image)
            merged_img = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)
            cv2.imwrite("assets/images/merged_rect.png", merged_img)
            self.player = pygame.image.load("assets/images/merged_rect.png")
            self.is_eated = True

    def draw(self, screen):
        screen.fill((50, 50, 50))
        screen.blit(self.player, self.player_rect)
        if self.is_eated == False:
            screen.blit(self.eated, self.eated_rect)

    def handle_event(self, event):
        pass
