import pygame

class Button:
    #버튼의 위치 x , y 버튼의 가로(width) 세로(height) ,버튼에 표시될 문자(text)와 크기, 버튼을 누르면 적용될 함수
    def __init__(self, x, y, width, height, text, text_size, callback):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_size = text_size
        self.callback = callback
        self.font = pygame.font.SysFont(None, text_size)
        self.color = (200, 200, 200)
        self.hover_color = (255, 255, 255)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
