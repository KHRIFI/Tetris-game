import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Dimensions et couleurs
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 700
GRID_WIDTH, GRID_HEIGHT = 10, 20
BLOCK_SIZE = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialisation des sons
pygame.mixer.init()
MOVE_SOUND = pygame.mixer.Sound("sounds/move.wav")
PAUSE_SOUND = pygame.mixer.Sound("sounds/pause.wav")
LINE_CLEAR_SOUND = pygame.mixer.Sound("sounds/line_clear.wav")

# Couleurs des pièces
COLORS = {
    "I": (0, 255, 255),
    "O": (255, 255, 0),
    "T": (128, 0, 128),
    "S": (0, 255, 0),
    "Z": (255, 0, 0),
    "J": (0, 0, 255),
    "L": (255, 165, 0),
}

# Formes des pièces
TETRIMINOS = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

# Initialisation de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Enhanced Visuals")
clock = pygame.time.Clock()

# Boutons
buttons = {
    "pause": {"color": GREEN, "pos": (70, 620), "radius": 30, "action": "pause"},
    "reset": {"color": RED, "pos": (140, 620), "radius": 30, "action": "reset"},
    "rotate": {"color": BLUE, "pos": (300, 580), "radius": 30, "action": "rotate"},
    "left": {"color": BLUE, "pos": (240, 640), "radius": 30, "action": "left"},
    "right": {"color": BLUE, "pos": (360, 640), "radius": 30, "action": "right"},
    "down": {"color": BLUE, "pos": (300, 640), "radius": 30, "action": "down"},
}

# Classe pour gérer la grille
class Grid:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def draw(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(150 + x * BLOCK_SIZE, 50 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, self.grid[y][x], rect)
                pygame.draw.rect(screen, GRAY, rect, 1)

    def add_piece(self, piece, position):
        px, py = position
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[py + i][px + j] = piece.color

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)

        if lines_to_clear:
            for _ in range(5):  # Animation de clignotement
                for y in lines_to_clear:
                    for x in range(GRID_WIDTH):
                        self.grid[y][x] = WHITE if self.grid[y][x] != WHITE else BLACK
                self.draw()
                pygame.display.flip()
                pygame.time.delay(100)

            for y in lines_to_clear:
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            LINE_CLEAR_SOUND.play()

        return len(lines_to_clear)


# Classe pour les pièces
class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = GRID_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def draw(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(150 + (self.x + j) * BLOCK_SIZE, 50 + (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(screen, WHITE, rect.inflate(10, 10), border_radius=5)  # Grosse lueur blanche
                    pygame.draw.rect(screen, self.color, rect)  # La pièce elle-même
                    pygame.draw.rect(screen, WHITE, rect, 1)  # Bordure


# Classe principale pour le jeu
class Tetris:
    def __init__(self):
        self.grid = Grid()
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.is_paused = False

    def new_piece(self):
        shape_name = random.choice(list(TETRIMINOS.keys()))
        shape = TETRIMINOS[shape_name]
        color = COLORS[shape_name]
        return Piece(shape, color)

    def move_piece(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        if self.collision():
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            if dy:
                self.lock_piece()
        else:
            if dx != 0:
                MOVE_SOUND.play()

    def rotate_piece(self):
        self.current_piece.rotate()
        if self.collision():
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()

    def collision(self):
        piece = self.current_piece
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x, y = piece.x + j, piece.y + i
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                        return True
                    if y >= 0 and self.grid.grid[y][x] != BLACK:
                        return True
        return False

    def lock_piece(self):
        self.grid.add_piece(self.current_piece, (self.current_piece.x, self.current_piece.y))
        lines_cleared = self.grid.clear_lines()
        self.update_score(lines_cleared)
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if self.collision():
            self.game_over()

    def update_score(self, lines_cleared):
        self.lines_cleared += lines_cleared
        self.score += lines_cleared * 100
        self.level = 1 + self.lines_cleared // 10

    def game_over(self):
        print("Game Over")
        pygame.quit()
        sys.exit()

    def draw(self):
        self.grid.draw()
        self.current_piece.draw()
        self.draw_next_piece()
        self.draw_info()
        self.draw_buttons()

    def draw_next_piece(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Prochain:", True, WHITE)
        screen.blit(text, (10, 50))
        for i, row in enumerate(self.next_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(10 + j * BLOCK_SIZE, 80 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(screen, self.next_piece.color, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)

    def draw_info(self):
        font = pygame.font.SysFont("Arial", 20)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Niveau: {self.level}", True, WHITE)
        lines_text = font.render(f"Lignes: {self.lines_cleared}", True, WHITE)
        screen.blit(score_text, (10, 200))
        screen.blit(level_text, (10, 230))
        screen.blit(lines_text, (10, 260))

    def draw_buttons(self):
        font = pygame.font.SysFont("Arial", 15)
        for key, btn in buttons.items():
            pygame.draw.circle(screen, btn["color"], btn["pos"], btn["radius"])
            text = font.render(key.capitalize(), True, BLACK)
            screen.blit(
                text,
                (
                    btn["pos"][0] - text.get_width() // 2,
                    btn["pos"][1] - text.get_height() // 2,
                ),
            )


# Détecter si un bouton est cliqué
def button_clicked(pos, buttons):
    for key, btn in buttons.items():
        bx, by = btn["pos"]
        if (pos[0] - bx) ** 2 + (pos[1] - by) ** 2 <= btn["radius"] ** 2:
            return btn["action"]
    return None


# Fonction principale
def main():
    game = Tetris()
    drop_time = 500
    last_drop = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                action = button_clicked(mouse_pos, buttons)
                if action:
                    if action == "pause":
                        game.is_paused = not game.is_paused
                        PAUSE_SOUND.play()
                    elif action == "reset":
                        main()
                    elif action == "rotate":
                        game.rotate_piece()
                    elif action == "left":
                        game.move_piece(-1, 0)
                    elif action == "right":
                        game.move_piece(1, 0)
                    elif action == "down":
                        game.move_piece(0, 1)

        if not game.is_paused and pygame.time.get_ticks() - last_drop > drop_time - game.level * 50:
            game.move_piece(0, 1)
            last_drop = pygame.time.get_ticks()

        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
