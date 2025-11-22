import pygame
import sys
from ui_elements import Button
from perihelio import PerihelioSim
from gps import GPSSim

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Relatividad General")

# --------------------------
# FUENTES
# --------------------------

TITLE_FONT = pygame.font.SysFont("lucida sans", 54, bold=True)
SMALL = pygame.font.SysFont("lucida sans", 24)

# --------------------------
# Imagen con aspect ratio fijo
# --------------------------
def load_img_keep_ratio(path, max_w, max_h):
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()

    scale = min(max_w / w, max_h / h)  # mantiene proporción
    new_size = (int(w * scale), int(h * scale))

    return pygame.transform.smoothscale(img, new_size)


# --------------------------
# Cargar imágenes
# --------------------------
bg_space = pygame.image.load("space_bg.jpg")
bg_space = pygame.transform.scale(bg_space, (WIDTH, HEIGHT))

peri_img = load_img_keep_ratio("p.png", 130, 130)
gps_img = load_img_keep_ratio("gps.png", 130, 130)

# --------------------------
# Botón estilizado con glow
# --------------------------
class ImageButton:
    def __init__(self, x, y, w, h, text, img):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.img = img
        self.font = pygame.font.SysFont("lucida sans", 20, bold=True)

        # Glow
        self.glow = pygame.Surface((w + 40, h + 40), pygame.SRCALPHA)
        pygame.draw.rect(self.glow, (255, 255, 200, 70),
                         self.glow.get_rect(), border_radius=26)

    # ----------- NEW: función para dividir texto -----------
    def wrap_text(self, text, max_width):
        words = text.replace("\n", " \n ").split(" ")
        lines = []
        current = ""

        for w in words:
            if w == "\n":
                lines.append(current)
                current = ""
                continue

            test = current + (" " if current else "") + w
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = w

        if current:
            lines.append(current)

        return lines

    def draw(self, screen):
        hovered = self.is_hovered()

        # Glow
        if hovered:
            screen.blit(self.glow, (self.rect.x - 20, self.rect.y - 20))

        # Fondo del botón
        pygame.draw.rect(screen, (30, 30, 45), self.rect, border_radius=18)
        pygame.draw.rect(screen, (200, 200, 230), self.rect, 3, border_radius=18)

        # --------------------------------------------------
        # Imagen centrada (arriba)
        # --------------------------------------------------
        img_x = self.rect.centerx - self.img.get_width() // 2
        img_y = self.rect.y + 18   # margen superior
        screen.blit(self.img, (img_x, img_y))

        # --------------------------------------------------
        # Texto multilínea centrado
        # --------------------------------------------------
        lines = self.wrap_text(self.text, self.rect.width - 20)

        total_height = len(lines) * self.font.get_height()
        start_y = self.rect.bottom - total_height - 18

        for i, line in enumerate(lines):
            surf = self.font.render(line, True, (255, 255, 255))
            screen.blit(
                surf,
                (self.rect.centerx - surf.get_width() // 2,
                 start_y + i * self.font.get_height())
            )

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())


# --------------------------
# MAIN MENU
# --------------------------
def main_menu():
    clock = pygame.time.Clock()

    peri_btn = ImageButton(
        WIDTH // 2 - 320, 300, 260, 220,
        "Precesión del Perihelio de Mercurio",
        peri_img
    )

    gps_btn = ImageButton(
        WIDTH // 2 + 60, 300, 260, 220,
        "Navegación por GPS",
        gps_img
    )

    running = True
    while running:
        screen.blit(bg_space, (0, 0))

        # Oscurecer fondo suavemente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))

        # Título
        title = TITLE_FONT.render("Simulador de Relatividad General", True, (241, 194, 50))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        # Botones
        peri_btn.draw(screen)
        gps_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if peri_btn.is_hovered():
                    PerihelioSim(screen).run()
                if gps_btn.is_hovered():
                    GPSSim(screen).run()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
