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

class BackButtonUI:
    def __init__(self, x=12, y=12):
        self.rect = pygame.Rect(x, y, 42, 42)

    def draw(self, screen):
        # círculo
        pygame.draw.circle(screen, (30, 30, 30, 180), self.rect.center, 21)
        pygame.draw.circle(screen, (80, 80, 90), self.rect.center, 21, 2)

        # flecha "<"
        cx, cy = self.rect.center
        pygame.draw.line(screen, (240, 240, 255), (cx + 6, cy - 10), (cx - 6, cy), 3)
        pygame.draw.line(screen, (240, 240, 255), (cx - 6, cy), (cx + 6, cy + 10), 3)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
