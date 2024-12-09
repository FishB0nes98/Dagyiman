import pygame
import random
import sys
import os
import warnings
import math
from pygame.locals import *
from map import load_map

# Initialize Pygame and suppress warnings
pygame.init()
pygame.mixer.init()
warnings.filterwarnings('ignore')

# Constants
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900
CELL_SIZE = 30
FPS = 60

# Game settings
MEDICINE_SPAWN_TIME = 3000   # Spawn medicine every 3 seconds
AMBULANCE_SPAWN_TIME = 30000  # Spawn ambulance every 30 seconds
CHAIR_RESPAWN_TIME = 60000   # Chairs respawn every 60 seconds
MIN_MEDICINES = 15           # More medicines on the map
MIN_AMBULANCES = 2
ENEMY_SPEED = 3.5           # Increased chair speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
MENU_HIGHLIGHT = (128, 128, 255)
GRAY = (128, 128, 128)

# Game states
MENU = 0
LOADING = 1
PLAYING = 2

def load_player_image():
    try:
        image_path = os.path.join('assets', 'player.png')
        if os.path.exists(image_path):
            image = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(image, (CELL_SIZE*2, CELL_SIZE*2))
    except (pygame.error, FileNotFoundError):
        surface = pygame.Surface([CELL_SIZE*2, CELL_SIZE*2])
        surface.fill(YELLOW)
        return surface

class LoadingScreen:
    def __init__(self):
        self.angle = 0
        self.player_image = load_player_image()
        self.font = pygame.font.Font(None, 74)
        self.loading_text = self.font.render("Loading...", True, WHITE)
        self.text_rect = self.loading_text.get_rect(centerx=WINDOW_WIDTH//2, 
                                                  centery=WINDOW_HEIGHT//2 + 100)
        
    def update(self):
        self.angle += 5  # Rotate 5 degrees per frame
        
    def draw(self, screen):
        screen.fill(BLACK)
        # Get the rotated player image
        rotated_image = pygame.transform.rotate(self.player_image, self.angle)
        rotated_rect = rotated_image.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(rotated_image, rotated_rect)
        screen.blit(self.loading_text, self.text_rect)

class Menu:
    def __init__(self):
        self.font_big = pygame.font.Font(None, 74)
        self.font_options = pygame.font.Font(None, 54)
        self.font_volume = pygame.font.Font(None, 36)  # Smaller font for volume
        self.selected_option = 0
        self.options = ["Let's Dagyi!", "Ühm"]  # Removed Volume from menu options
        self.volume = 0.1  # 10% volume by default
        
        # Position slider in top right corner
        slider_width = 150
        slider_height = 15
        margin = 20
        self.slider_rect = pygame.Rect(
            WINDOW_WIDTH - slider_width - margin,
            margin,
            slider_width,
            slider_height
        )
        self.slider_handle = pygame.Rect(
            self.slider_rect.x + (self.volume * slider_width) - 5,
            margin - 2,
            10,  # Smaller handle
            slider_height + 4
        )
        self.dragging_slider = False
        
        # Load and start music
        try:
            self.music_path = os.path.join('assets', 'Danci és a Szék Fatality.mp3')
            if os.path.exists(self.music_path):
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                pygame.mixer.music.set_volume(self.volume)
            else:
                print("Music file not found:", self.music_path)
        except (pygame.error, FileNotFoundError) as e:
            print("Error loading music:", str(e))
        
    def draw(self, screen):
        # Draw title
        title = self.font_big.render("DAGYIMAN", True, YELLOW)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//3)
        screen.blit(title, title_rect)
        
        # Draw menu options
        for i, option in enumerate(self.options):
            color = MENU_HIGHLIGHT if i == self.selected_option else WHITE
            text = self.font_options.render(option, True, color)
            rect = text.get_rect(centerx=WINDOW_WIDTH//2, 
                               y=WINDOW_HEIGHT//2 + i * 60)
            screen.blit(text, rect)
        
        # Draw volume control in top right
        volume_label = self.font_volume.render("Volume", True, WHITE)
        volume_label_rect = volume_label.get_rect(
            right=self.slider_rect.left - 10,
            centery=self.slider_rect.centery
        )
        screen.blit(volume_label, volume_label_rect)
        
        # Draw slider background
        pygame.draw.rect(screen, GRAY, self.slider_rect)
        # Draw slider handle
        pygame.draw.rect(screen, WHITE, self.slider_handle)
        # Draw volume percentage
        volume_text = self.font_volume.render(f"{int(self.volume * 100)}%", True, WHITE)
        volume_rect = volume_text.get_rect(
            left=self.slider_rect.right + 10,
            centery=self.slider_rect.centery
        )
        screen.blit(volume_text, volume_rect)
    
    def handle_input(self, event):
        if event.type == KEYDOWN:
            if event.key in [K_UP, K_DOWN]:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == K_RETURN:
                if self.selected_option == 0:  # Let's Dagyi!
                    return PLAYING
                elif self.selected_option == 1:  # Ühm (quit)
                    pygame.quit()
                    sys.exit()
        
        # Handle mouse events for volume slider
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.slider_rect.collidepoint(event.pos):
                    self.dragging_slider = True
                    self.update_volume(event.pos[0])
        
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = False
        
        elif event.type == MOUSEMOTION:
            if self.dragging_slider:
                self.update_volume(event.pos[0])
        
        return MENU
    
    def update_volume(self, x_pos):
        # Calculate volume based on slider position
        slider_x = max(self.slider_rect.left, min(x_pos, self.slider_rect.right))
        self.volume = (slider_x - self.slider_rect.left) / self.slider_rect.width
        # Update slider handle position
        self.slider_handle.centerx = slider_x
        # Update music volume
        pygame.mixer.music.set_volume(self.volume)

# Load images with fallback
def load_game_image(filename, fallback_color):
    try:
        image_path = os.path.join('assets', filename)
        if os.path.exists(image_path):
            image = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(image, (CELL_SIZE-4, CELL_SIZE-4))
    except (pygame.error, FileNotFoundError):
        pass
    
    # Fallback to colored rectangle
    surface = pygame.Surface([CELL_SIZE-4, CELL_SIZE-4])
    surface.fill(fallback_color)
    return surface

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_game_image('player.png', YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
        self.lives = 3
        self.score = 0
        self.original_pos = (x, y)

    def update(self, walls):
        old_x = self.rect.x
        old_y = self.rect.y
        
        keys = pygame.key.get_pressed()
        # WASD movement
        if keys[K_a] or keys[K_LEFT]:
            self.rect.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            self.rect.x += self.speed
        if keys[K_w] or keys[K_UP]:
            self.rect.y -= self.speed
        if keys[K_s] or keys[K_DOWN]:
            self.rect.y += self.speed

        wall_hits = pygame.sprite.spritecollide(self, walls, False)
        if wall_hits:
            self.rect.x = old_x
            self.rect.y = old_y

    def reset_position(self):
        self.rect.x = self.original_pos[0]
        self.rect.y = self.original_pos[1]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = (CELL_SIZE*2-4, CELL_SIZE*2-4)
        self.image = pygame.Surface(self.size)
        try:
            image_path = os.path.join('assets', 'enemy.png')
            if os.path.exists(image_path):
                loaded_image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(loaded_image, self.size)
            else:
                self.image.fill(RED)
        except (pygame.error, FileNotFoundError):
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = ENEMY_SPEED
        self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.spawn_time = pygame.time.get_ticks()

    def should_respawn(self, current_time):
        return current_time - self.spawn_time >= CHAIR_RESPAWN_TIME

    def respawn(self, walls, all_sprites):
        new_pos = find_empty_position(walls, all_sprites, self.size)
        if new_pos:
            self.rect.x, self.rect.y = new_pos
            self.spawn_time = pygame.time.get_ticks()
            self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

    def update(self, walls):
        old_x = self.rect.x
        old_y = self.rect.y
        
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Wall collision
        wall_hits = pygame.sprite.spritecollide(self, walls, False)
        if wall_hits:
            self.rect.x = old_x
            self.rect.y = old_y
            # Change direction when hitting a wall
            possible_directions = [(1,0), (-1,0), (0,1), (0,-1)]
            possible_directions.remove((-self.direction[0], -self.direction[1]))
            self.direction = random.choice(possible_directions)

class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_game_image('medicine.png', WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x + CELL_SIZE // 2
        self.rect.centery = y + CELL_SIZE // 2

class Ambulance(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_game_image('ambulance.png', BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def find_empty_position(walls, all_sprites, size, player_pos=None):
    max_attempts = 50  # Reduced max attempts
    attempts = 0
    safe_distance = CELL_SIZE * 6
    
    # Pre-calculate valid x and y positions
    valid_x = list(range(CELL_SIZE*2, WINDOW_WIDTH - size[0], CELL_SIZE))
    valid_y = list(range(CELL_SIZE*2, WINDOW_HEIGHT - size[1], CELL_SIZE))
    
    while attempts < max_attempts:
        x = random.choice(valid_x)
        y = random.choice(valid_y)
        
        # If player position is provided, check safe distance
        if player_pos:
            player_x, player_y = player_pos
            distance = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
            if distance < safe_distance:
                attempts += 1
                continue
        
        # Quick boundary check for optimization
        if x < 0 or x > WINDOW_WIDTH - size[0] or y < 0 or y > WINDOW_HEIGHT - size[1]:
            attempts += 1
            continue
            
        # Create a temporary sprite to check collisions
        temp = pygame.sprite.Sprite()
        temp.rect = pygame.Rect(x, y, size[0], size[1])
        
        # Optimize collision check by checking walls first
        if pygame.sprite.spritecollideany(temp, walls):
            attempts += 1
            continue
            
        # Only check all_sprites if wall check passes
        if not pygame.sprite.spritecollideany(temp, all_sprites):
            return x, y
        
        attempts += 1
    
    return None

def draw_fatality(screen):
    # Create big font for FATALITY
    fatality_font = pygame.font.Font(None, 150)  # Bigger font size
    game_over_font = pygame.font.Font(None, 74)  # Regular game over size
    
    # Draw FATALITY text with shadow effect
    shadow_offset = 4
    fatality_shadow = fatality_font.render('FATALITY', True, (100, 0, 0))  # Dark red shadow
    fatality_text = fatality_font.render('FATALITY', True, (255, 0, 0))  # Bright red
    
    # Center the text
    shadow_rect = fatality_shadow.get_rect(center=(WINDOW_WIDTH//2 + shadow_offset, 
                                                  WINDOW_HEIGHT//2 + shadow_offset))
    text_rect = fatality_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    
    # Draw Game Over text below FATALITY
    game_over_text = game_over_font.render('Game Over!', True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, 
                                                    WINDOW_HEIGHT//2 + 80))
    
    # Draw the texts
    screen.blit(fatality_shadow, shadow_rect)
    screen.blit(fatality_text, text_rect)
    screen.blit(game_over_text, game_over_rect)

def main():
    # Initialize mixer with higher quality
    pygame.mixer.quit()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Dagyiman')
    clock = pygame.time.Clock()
    game_state = MENU
    menu = Menu()
    loading_screen = LoadingScreen()

    # Make sure music is playing
    if not pygame.mixer.music.get_busy():
        try:
            music_path = os.path.join('assets', 'Danci és a Szék Fatality.mp3')
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(menu.volume)
        except (pygame.error, FileNotFoundError) as e:
            print("Error reloading music:", str(e))

    # Game initialization (do this once, outside the game loop)
    walls = None
    player = None
    enemies = None
    pickups = None
    ambulances = None
    all_sprites = None

    while True:
        if game_state == MENU:
            screen.fill(BLACK)
            menu.draw(screen)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                game_state = menu.handle_input(event)
            
            if game_state == PLAYING:
                game_state = LOADING
                loading_start_time = pygame.time.get_ticks()
            
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if game_state == LOADING:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            
            loading_screen.update()
            loading_screen.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

            # Only proceed to game after loading screen finishes
            if current_time - loading_start_time >= 2000:
                # Initialize game objects
                walls, player_start, enemy_starts, medicine_positions, ambulance_positions = load_map(CELL_SIZE)

                # Sprite Groups
                all_sprites = pygame.sprite.Group()
                enemies = pygame.sprite.Group()
                pickups = pygame.sprite.Group()
                ambulances = pygame.sprite.Group()
                all_sprites.add(walls)

                # Create player
                player = Player(player_start[0], player_start[1])
                all_sprites.add(player)

                # Create enemies with proper spawning, avoiding player area
                for pos in enemy_starts:
                    enemy_pos = find_empty_position(walls, all_sprites, 
                                                  (CELL_SIZE*2-4, CELL_SIZE*2-4),
                                                  player_pos=(player_start[0], player_start[1]))
                    if enemy_pos:
                        enemy = Enemy(enemy_pos[0], enemy_pos[1])
                        all_sprites.add(enemy)
                        enemies.add(enemy)

                # Create initial pickups
                for _ in range(MIN_MEDICINES):
                    pickup_pos = find_empty_position(walls, all_sprites, (10, 10))
                    if pickup_pos:
                        pickup = Pickup(pickup_pos[0], pickup_pos[1])
                        all_sprites.add(pickup)
                        pickups.add(pickup)

                # Create initial ambulances
                for _ in range(MIN_AMBULANCES):
                    ambulance_pos = find_empty_position(walls, all_sprites, (CELL_SIZE-4, CELL_SIZE-4))
                    if ambulance_pos:
                        ambulance = Ambulance(ambulance_pos[0], ambulance_pos[1])
                        all_sprites.add(ambulance)
                        ambulances.add(ambulance)

                # Initialize spawn timers
                last_medicine_spawn = pygame.time.get_ticks()
                last_ambulance_spawn = pygame.time.get_ticks()
                
                game_state = PLAYING
            continue

        # Game loop
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                game_state = MENU
                break

        if game_state == MENU:
            continue

        # Check for chair respawning
        for enemy in enemies:
            if enemy.should_respawn(current_time):
                enemy_pos = find_empty_position(walls, all_sprites, 
                                             (CELL_SIZE*2-4, CELL_SIZE*2-4),
                                             player_pos=(player.rect.x, player.rect.y))
                if enemy_pos:
                    enemy.rect.x, enemy.rect.y = enemy_pos
                    enemy.spawn_time = current_time

        # Optimize medicine spawning
        if len(pickups) < MIN_MEDICINES and current_time - last_medicine_spawn >= MEDICINE_SPAWN_TIME:
            # Try to spawn up to 3 medicines at once to reduce spawn frequency
            spawn_count = min(MIN_MEDICINES - len(pickups), 3)
            for _ in range(spawn_count):
                pickup_pos = find_empty_position(walls, all_sprites, (10, 10))
                if pickup_pos:
                    pickup = Pickup(pickup_pos[0], pickup_pos[1])
                    all_sprites.add(pickup)
                    pickups.add(pickup)
            last_medicine_spawn = current_time

        # Spawn new ambulance if needed
        if len(ambulances) < MIN_AMBULANCES and current_time - last_ambulance_spawn >= AMBULANCE_SPAWN_TIME:
            ambulance_pos = find_empty_position(walls, all_sprites, (CELL_SIZE-4, CELL_SIZE-4))
            if ambulance_pos:
                ambulance = Ambulance(ambulance_pos[0], ambulance_pos[1])
                all_sprites.add(ambulance)
                ambulances.add(ambulance)
                last_ambulance_spawn = current_time

        # Update
        player.update(walls)
        for enemy in enemies:
            enemy.update(walls)

        # Collision detection
        pickup_collisions = pygame.sprite.spritecollide(player, pickups, True)
        for pickup in pickup_collisions:
            player.score += 10

        ambulance_collisions = pygame.sprite.spritecollide(player, ambulances, True)
        for ambulance in ambulance_collisions:
            player.lives += 1

        enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
        if enemy_collisions:
            player.lives -= 1
            if player.lives <= 0:
                # Show FATALITY message
                screen.fill(BLACK)  # Clear screen
                draw_fatality(screen)
                pygame.display.flip()
                pygame.time.wait(5000)  # Wait 5 seconds
                game_state = MENU
                continue
            else:
                player.reset_position()

        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main() 