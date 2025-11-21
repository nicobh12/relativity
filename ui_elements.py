import pygame
pygame.font.init()


FONT = pygame.font.SysFont("arial", 28)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
        color = (180, 180, 255) if self.is_hovered() else (120, 120, 200)
        pygame.draw.rect(screen, color, self.rect, border_radius=12)

        label = FONT.render(self.text, True, (10, 10, 20))
        screen.blit(label, (self.rect.x + self.rect.width//2 - label.get_width()//2,
                            self.rect.y + self.rect.height//2 - label.get_height()//2))

    def is_hovered(self):
        mx, my = pygame.mouse.get_pos()
        return self.rect.collidepoint(mx, my)
