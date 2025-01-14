import pygame
import random
import math
import os
import time
from asset_manager_optimized import GameAssetManager
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv()
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        self.asset_manager = GameAssetManager()
        self.assets = {}
        
    def show_loading_screen(self):
        """Display loading screen while assets download"""
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        loading_text = font.render("Loading Game Assets...", True, (255, 255, 255))
        text_rect = loading_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.screen.blit(loading_text, text_rect)
        pygame.display.flip()


    def load_assets(self):
        """Load all game assets"""
        cache_dir = 'local_assets'
        
        # Show loading screen
        self.show_loading_screen()
        
        # Try to load from S3
        if self.asset_manager.create_asset_cache(cache_dir):
            # Load cached assets into pygame
            for asset_file in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, asset_file)
                try:
                    if asset_file.endswith(('.png', '.jpg', '.JPG')):
                        self.assets[asset_file] = pygame.image.load(file_path).convert_alpha()
                    elif asset_file.endswith(('.wav', '.mp3')):
                        self.assets[asset_file] = pygame.mixer.Sound(file_path)
                except pygame.error as e:
                    print(f"Failed to load asset {asset_file}: {e}")
        else:
            print("Failed to load assets from S3, falling back to local assets")
            self.load_local_assets()





# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
FLOOR_HEIGHT = 300
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Water Jump Platformer")

# Water pool properties
pool_width = 80
pool_height = 20
pools = []

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (34, 139, 34)
GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
RED = (255, 0, 0)

# Initialize game
def test_s3_connection():
    asset_manager = GameAssetManager()
    if asset_manager.is_available():
        assets = asset_manager.list_assets()
        print("Found assets:", assets)
    else:
        print("S3 connection failed")

# Add this to your main game initialization
test_s3_connection()
game = Game()
    
    # Upload assets to S3 (only need to do this once)
    # game.upload_initial_assets('original_assets')
    
    # Load assets from S3 cache
game.load_assets()

# Load assets
try:
    # Player and backgrounds
    player_img = game.assets['hero.png']
    player_img = pygame.transform.scale(player_img, (40, 60))
    
    background_img_1 = game.assets['day_background1.jpg']
    background_img_1 = pygame.transform.scale(background_img_1, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
    background_img_2 = game.assets['night_background.JPG']
    background_img_2 = pygame.transform.scale(background_img_2, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Adversary
    adversary_img = game.assets['witch.png']
    adversary_img = pygame.transform.scale(adversary_img, (50, 70))
    
    heart_img = game.assets['heart.png']
    heart_img = pygame.transform.scale(heart_img, (30, 30))
    
    pothole_img = game.assets['pothole.png']
    pothole_img = pygame.transform.scale(pothole_img, (pool_width, pool_height + 10))  # Making it slightly taller for depth effect
    
except:
    print("Couldn't load some images. Using fallback shapes.")
    player_img = None
    background_img_1 = None
    background_img_2 = None
    adversary_img = None
    heart_img = None
    pothole_img = None

# Load sounds
try:
    jump_sound = game.assets['audio.mp3']
    #adversary_sound = pygame.mixer.Sound(os.path.join('assets', 'adversary.wav'))
    #level_complete_sound = pygame.mixer.Sound(os.path.join('assets', 'level_complete.wav'))
    # Sound to be played when cheating
    #cheat_sound = pygame.mixer.Sound(os.path.join('assets', 'cheat.wav'))
    adversary_sound = None
    level_complete_sound = None
    cheat_sound = None
except:
    print("Couldn't load some sounds.")
    jump_sound = None
    adversary_sound = None
    level_complete_sound = None
    cheat_sound = None

# First, let's create a Particle class to manage individual water particles
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)  # Random horizontal velocity
        self.dy = random.uniform(-4, 0)  # Initial upward velocity
        self.lifetime = random.randint(20, 40)  # How long the particle lives
        self.gravity = 0.2
        self.alpha = 255  # Transparency
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity  # Apply gravity
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - 5)  # Fade out
        
        
    def draw(self, screen):
        if self.lifetime > 0:
            particle_surface = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                (64, 164, 223, self.alpha),  # Blue color with alpha
                (self.size//2, self.size//2),  # Center of circle
                self.size//2  # Radius
            )            
            screen.blit(particle_surface, (int(self.x), int(self.y)))

# Create a class to manage splash effects
class SplashEffect:
    def __init__(self, x, y):
        self.particles = []
        self.x = x
        self.y = y
        self.create_particles()

    def create_particles(self):
        for _ in range(20):  # Create 20 particles per splash
            self.particles.append(Particle(self.x, self.y))

    def update(self):
        # Update all particles and remove dead ones
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)


class Adversary:
    def __init__(self):
        self.width = 50
        self.height = 70
        self.x = WINDOW_WIDTH
        self.y = FLOOR_HEIGHT - self.height
        self.speed = 5
        self.jump_timer = 0
        self.jump_interval = random.randint(60, 120)  # Frames between jumps
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -15

    def update(self):
        self.x -= self.speed
        self.jump_timer += 1
        
        if self.jump_timer >= self.jump_interval:
            self.jump_timer = 0
            self.jump_interval = random.randint(60, 120)
            self.velocity_y = self.jump_speed
            if adversary_sound:
                adversary_sound.play()

        self.y += self.velocity_y
        self.velocity_y += self.gravity

        if self.y >= FLOOR_HEIGHT - self.height:
            self.y = FLOOR_HEIGHT - self.height
            self.velocity_y = 0

    def draw(self, screen):
        if adversary_img:
            screen.blit(adversary_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

class GameState:
    def __init__(self):
        self.lives = 3
        self.score = 0
        self.level = 1
        self.game_speed = 5
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 2000
        self.distance_covered = 0
        self.level_length = 5000  # Increased level length (adjust as needed)
        self.transitioning = False
        self.transition_start = 0
        self.transition_duration = 2000  # 2 seconds
        self.max_level = 3  # Cap at level 3
        self.cheat_activated = False  # Track if cheat is activated

    def activate_level_2(self):
        self.level = 2
        self.distance_covered = 0
        self.cheat_activated = True
        if cheat_sound:
            cheat_sound.play()
        return self.reset_player_position()
    
    def reset_player_position(self):
        return 100, FLOOR_HEIGHT - player_height

def change_background_music(level):
    pygame.mixer.music.stop()
    try:
        bck_music = game.assets['bckground.mp3']
        bck_music.play(-1)  # -1 means loop indefinitely
        bck_music.set_volume(0.3) 
    except:
        print(f"Couldn't load music for level {level}")

def level_transition(game_state):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render(f"Level {game_state.level}", True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(2)
    
    # Reset level state
    game_state.distance_covered = 0
    pools.clear()
    change_background_music(game_state.level)
    return []  # Return empty adversaries list

def draw_lives(screen, lives):
    if heart_img:
        for i in range(lives):
            screen.blit(heart_img, (10 + i * 35, 10))
    else:
        for i in range(lives):
            pygame.draw.circle(screen, RED, (25 + i * 35, 25), 10)
            
def draw_pothole(screen, x, y):
    if pothole_img:
        screen.blit(pothole_img, (x, y))
    else:
        pygame.draw.ellipse(screen, GRAY, (x, y, pool_width, pool_height + 5))
        pygame.draw.ellipse(screen, BLUE, (x + 5, y + 5, pool_width - 10, pool_height - 5))
    
    # # Add ambient water particles
    # if random.random() < 0.1:  # 10% chance each frame to create a new particle
    #     water_particles.append(Particle(
    #         x + random.randint(10, pool_width - 10),
    #         y + pool_height//2
    #     ))

def show_start_screen():
    screen.fill(BLACK)
    font_large = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 36)
    
    # Title
    title = font_large.render("Choota Pandit Jump", True, WHITE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3))
    
    # Instructions
    instructions = font_small.render("Press SPACE to Start", True, WHITE)
    inst_rect = instructions.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    
    screen.blit(title, title_rect)
    screen.blit(instructions, inst_rect)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    return True
    return False




show_start_screen()
      
# Game loop
# Initialize game state
game_state = GameState()

# Player properties
player_width = 40
player_height = 60
player_x, player_y = game_state.reset_player_position()
player_speed = 5
jump_speed = -15
gravity = 0.8

player_velocity_y = 0
is_jumping = False


clock = pygame.time.Clock()
running = True
#game_state = GameState()
#pools = []
adversaries = []
splash_effects = []
water_particles = []

# Start background music
change_background_music(1)

def level_transition(game_state):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    if game_state.cheat_activated:
        text = font.render("CHEAT ACTIVATED", True, (255, 255, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 50))
        screen.blit(text, text_rect)
        
    text = font.render(f"Level {game_state.level}", True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(2)
    
    # Reset level state
    game_state.distance_covered = 0
    pools.clear()
    change_background_music(game_state.level)
    return []

while running:
    current_time = pygame.time.get_ticks()
    
    # Update game state
    game_state.distance_covered += game_state.game_speed

    # Generate water pools (only in levels 1 and 3)
    if game_state.level == 1 or game_state.level == 3:
        # In the main game loop where pools are drawn
        if len(pools) == 0 or pools[-1][0] < WINDOW_WIDTH - 300:
            pools.append([WINDOW_WIDTH, FLOOR_HEIGHT - pool_height])
        
        
        

    # Generate adversaries (only in levels 2 and 3)
    if game_state.level >= 2:
        if len(adversaries) == 0 or adversaries[-1].x < WINDOW_WIDTH - 400:
            adversaries.append(Adversary())

    # Update pools and adversaries
    for pool in pools:
        pool[0] -= game_state.game_speed
    pools = [pool for pool in pools if pool[0] > -pool_width]

    for adversary in adversaries:
        adversary.update()
    adversaries = [adv for adv in adversaries if adv.x > -adv.width]
    
    # Update existing effects
    for splash in splash_effects:
        splash.update()
    splash_effects = [splash for splash in splash_effects if splash.particles]

    # Update water particles
    for particle in water_particles:
        particle.update()
    water_particles = [p for p in water_particles if p.lifetime > 0]
    
    # Level transition
    if game_state.distance_covered >= game_state.level_length and not game_state.transitioning:
        if game_state.level < game_state.max_level:
            game_state.transitioning = True
            game_state.transition_start = current_time
            game_state.level += 1
            if level_complete_sound:
                level_complete_sound.play()
            # Clear all obstacles during transition
            pools.clear()
            adversaries.clear()
            adversaries = level_transition(game_state)
            game_state.transitioning = False
        else:
            running = False  # Or implement victory screen

    # Regular game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_jumping:
                player_velocity_y = jump_speed
                is_jumping = True
                if jump_sound:
                    jump_sound.play()
                    jump_sound.set_volume(0.3)

            # Cheat code using key 4
            if event.key == pygame.K_4:
                player_x, player_y = game_state.activate_level_2()
                player_velocity_y = 0
                pools.clear()  # Clear pools as level 2 doesn't have them
                adversaries.clear()  # Clear existing adversaries
                if level_complete_sound:
                    level_complete_sound.play()
                # Show level 2 transition screen
                level_transition(game_state)
    

    # Update player position
    player_y += player_velocity_y
    player_velocity_y += gravity

    # Ground collision
    if player_y >= FLOOR_HEIGHT - player_height:
        player_y = FLOOR_HEIGHT - player_height
        player_velocity_y = 0
        is_jumping = False



   

    # Collision detection
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    
     # Pool collisions (only check if in level 1 or 3)
    if game_state.level == 1 or game_state.level == 3:
        # for pool in pools:
        #     pool_rect = pygame.Rect(pool[0], pool[1], pool_width, pool_height)
        #     if player_rect.colliderect(pool_rect) and not game_state.is_invulnerable:
        #         game_state.lives -= 1
        #         game_state.is_invulnerable = True
        #         game_state.invulnerable_timer = current_time
        #         if game_state.lives <= 0:
        #             running = False
        #         else:
        #             player_x, player_y = game_state.reset_player_position()
        #             player_velocity_y = 0
        # Adjust the collision detection for more realistic pothole interaction
        for pool in pools:
            if (player_x + player_width > pool[0] + 10 and 
                player_x < pool[0] + pool_width - 10 and 
                player_y + player_height > pool[1]):
                if not game_state.is_invulnerable:
                    game_state.lives -= 1
                    game_state.is_invulnerable = True
                    game_state.invulnerable_timer = current_time
                    # Add splash effect
                    splash_effects.append(SplashEffect(
                        pool[0] + pool_width//2,
                        pool[1] + pool_height//2
                    ))
                    if game_state.lives <= 0:
                        running = False
                    else:
                        player_x, player_y = game_state.reset_player_position()
                        player_velocity_y = 0
        

    # Adversary collisions (only check if in level 2 or 3)
    if game_state.level >= 2:
        for adversary in adversaries:
            adversary_rect = pygame.Rect(adversary.x, adversary.y, adversary.width, adversary.height)
            if player_rect.colliderect(adversary_rect) and not game_state.is_invulnerable:
                game_state.lives -= 1
                game_state.is_invulnerable = True
                game_state.invulnerable_timer = current_time
                if game_state.lives <= 0:
                    running = False
                else:
                    player_x, player_y = game_state.reset_player_position()
                    player_velocity_y = 0

    # Drawing section
    def draw_cheat_indicator(screen, game_state):
        if game_state.cheat_activated:
            font = pygame.font.Font(None, 24)
            text = font.render("CHEAT MODE", True, (255, 255, 0))
            screen.blit(text, (10, WINDOW_HEIGHT - 30))
        
    background_img = background_img_1 if game_state.level == 1 else background_img_2
    if game_state.level == 3:
        background_img = background_img_2  # Use different background for level 3 if available
    
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(WHITE)

    # Draw ground
    pygame.draw.rect(screen, GRAY, (0, FLOOR_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - FLOOR_HEIGHT))

    if game_state.is_invulnerable:
        if current_time - game_state.invulnerable_timer >= game_state.invulnerable_duration:
            game_state.is_invulnerable = False
            
   # Draw player with blinking effect when invulnerable
    if not game_state.is_invulnerable or (current_time // 200) % 2:
        if player_img:
            screen.blit(player_img, (player_x, player_y))
        else:
            pygame.draw.rect(screen, BROWN, (player_x, player_y, player_width, player_height))
                 
     # Draw pools (only in levels 1 and 3)
    if game_state.level == 1 or game_state.level == 3:
        # for pool in pools:
        #     pygame.draw.rect(screen, BLUE, (pool[0], pool[1], pool_width, pool_height))
        for pool in pools:
            draw_pothole(screen, pool[0], pool[1])
            
        
        # Draw all particle effects
        for splash in splash_effects:
            splash.draw(screen)
        
        for particle in water_particles:
            particle.draw(screen)
    
    # Draw adversaries (only in levels 2 and 3)
    if game_state.level >= 2:
        for adversary in adversaries:
            adversary.draw(screen)

    # Draw lives and level
    draw_lives(screen, game_state.lives)
    draw_cheat_indicator(screen, game_state)
    font = pygame.font.Font(None, 36)
    level_text = font.render(f"Level: {game_state.level}", True, WHITE)
    screen.blit(level_text, (WINDOW_WIDTH - 120, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
