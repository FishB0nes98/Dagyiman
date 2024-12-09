import pygame

# Map layout
# W = wall
# P = player starting position
# E = enemy starting position
# M = medicine pickup (collectible points)
# A = ambulance (extra life)

GAME_MAP = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WW    MM      MM      WW      MM      MM    WW",
    "WW    MM      MM      WW      MM      MM    WW",
    "WW  WWWWWW  WWWWWW  WWWW  WWWWWW  WWWWWW  WW",
    "WW  WWWWWW  WWWWWW  WWWW  WWWWWW  WWWWWW  WW",
    "WW    MM      MM      EE      MM      MM    WW",
    "WW    MM  AA  MM      EE      MM  AA  MM    WW",
    "WW  WWWWWW  WWWWWWWWWWWWWWWWWWWW  WWWWWW  WW",
    "WW  WWWWWW  WWWWWWWWWWWWWWWWWWWW  WWWWWW  WW",
    "WW    MM      MM  WWWWWWWW  MM      MM    WW",
    "WW    MM      MM  WWWWWWWW  MM      MM    WW",
    "WWWWWWWW  WWWWWW    EE    WWWWWW  WWWWWWWWWW",
    "WWWWWWWW  WWWWWW    EE    WWWWWW  WWWWWWWWWW",
    "WW    EE                            EE    WW",
    "WW    EE          PP  PP            EE    WW",
    "WWWWWWWW  WWWWWW  WWWWWW  WWWWWW  WWWWWWWWWW",
    "WWWWWWWW  WWWWWW  WWWWWW  WWWWWW  WWWWWWWWWW",
    "WW    MM      MM      MM      MM      MM    WW",
    "WW    MM  AA  MM      MM      MM  AA  MM    WW",
    "WW  WWWWWW  WWWWWWWWWWWWWWWWWWWW  WWWWWW  WW",
    "WW  WWWWWW  WWWWWWWWWWWWWWWWWWWW  WWWWWW  WW",
    "WW    MM      MM      MM      MM      MM    WW",
    "WW    MM  AA  MM      MM      MM  AA  MM    WW",
    "WW  WWWWWW  WWWWWW  WWWW  WWWWWW  WWWWWW  WW",
    "WW  WWWWWW  WWWWWW  WWWW  WWWWWW  WWWWWW  WW",
    "WW    MM      MM      MM      MM      MM    WW",
    "WW    MM      MM      MM      MM      MM    WW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
]

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, cell_size):
        super().__init__()
        self.image = pygame.Surface([cell_size, cell_size])
        self.image.fill((0, 0, 255))  # Blue walls
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def load_map(cell_size):
    walls = pygame.sprite.Group()
    player_start = None
    enemy_starts = []
    medicine_positions = []
    ambulance_positions = []

    for row, line in enumerate(GAME_MAP):
        for col, char in enumerate(line):
            x = col * cell_size
            y = row * cell_size
            
            if char == 'W':
                wall = Wall(x, y, cell_size)
                walls.add(wall)
            elif char == 'P':
                player_start = (x, y)
            elif char == 'E':
                enemy_starts.append((x, y))
            elif char == 'M':
                medicine_positions.append((x, y))
            elif char == 'A':
                ambulance_positions.append((x, y))

    return walls, player_start, enemy_starts, medicine_positions, ambulance_positions 