import pygame
import random
import sys
import asyncio

# --- CONFIGURATION CONSTANTS ---
WIDTH, HEIGHT = 800, 600
BLUE = (158, 235, 247)
WHITE = (255, 255, 255)
MUSIC_FILE = "baby-shark-tune.ogg"
MUSIC_START_TIME = 1  # seconds


class BabySharkGame:
    def __init__(self):
        # Initialize pygame and mixer
        pygame.init()
        pygame.mixer.init()
        # Set up display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Baby Shark's Ocean Adventure")
        # Load and scale background image
        self.background_img = pygame.image.load("oceanBackground2.png").convert()
        self.background_img = pygame.transform.scale(self.background_img, (WIDTH, HEIGHT))
        # Fonts for various UI elements
        self.font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.instructions_font = pygame.font.SysFont("Arial", 24)
        self.button_font = pygame.font.SysFont("Arial", 32, bold=True)
        # Load and scale shark image
        self.shark_img = pygame.image.load("babyShark2.png").convert_alpha()
        self.shark_img = pygame.transform.scale(self.shark_img, (170, 100))
        # Load and scale fish images
        self.fish_images = [
            pygame.transform.scale(pygame.image.load("fish1.png").convert_alpha(), (60, 40)),
            pygame.transform.scale(pygame.image.load("fish2.png").convert_alpha(), (70, 50)),
            pygame.transform.scale(pygame.image.load("fish3.png").convert_alpha(), (80, 60)),
        ]
        self.fish_scores = [10, 20, 30]
        # Load and scale obstacle images
        self.obstacle_images = [
            pygame.transform.scale(pygame.image.load("obstacle1.png").convert_alpha(), (50, 80)),
            pygame.transform.scale(pygame.image.load("obstacle2.png").convert_alpha(), (70, 60)),
            pygame.transform.scale(pygame.image.load("obstacle3.png").convert_alpha(), (40, 70)),
        ]
        # Set up game clock
        self.clock = pygame.time.Clock()
        # Ensure replay rect is always defined
        self.replay_rect = pygame.Rect(0, 0, 0, 0)
        # Touch button rects
        self.up_btn_rect = pygame.Rect(WIDTH - 110, HEIGHT - 160, 90, 60)
        self.down_btn_rect = pygame.Rect(WIDTH - 110, HEIGHT - 90, 90, 60)
        # Initialize game state
        self.reset_game()

    def create_fish(self):
        """Create a new fish object with random image and position."""
        idx = random.randint(0, len(self.fish_images) - 1)
        img = self.fish_images[idx]
        sizex, sizey = img.get_width(), img.get_height()
        # Place fish at right edge, random vertical position
        rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT - sizey - 50), sizex, sizey)
        return {"rect": rect, "img": img, "score": self.fish_scores[idx]}

    def create_obstacle(self):
        """Create a new obstacle object with random image and position."""
        idx = random.randint(0, len(self.obstacle_images) - 1)
        img = self.obstacle_images[idx]
        sizex, sizey = img.get_width(), img.get_height()
        # Place obstacle further to the right, random vertical position
        rect = pygame.Rect(WIDTH + 400, random.randint(50, HEIGHT - sizey - 50), sizex, sizey)
        return {"rect": rect, "img": img}

    def reset_game(self):
        """Reset the game state to initial conditions."""
        # Shark starting position
        self.shark_rect = self.shark_img.get_rect()
        self.shark_rect.topleft = (100, HEIGHT // 2)
        # Create first fish and obstacle
        self.fish = self.create_fish()
        self.obstacle = self.create_obstacle()
        # Reset score and game state
        self.score = 0
        self.game_over = False
        self.final_time = None
        self.start_ticks = pygame.time.get_ticks()
        # Start background music
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1, MUSIC_START_TIME)

    def draw_window(self):
        """Draw all game elements on the screen."""
        self.screen.fill(BLUE)
        self.screen.blit(self.background_img, (0, 0))
        # Draw game title at the top center
        title_text = self.title_font.render("Feed the Baby Shark", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        # Draw shark, fish, and obstacle
        self.screen.blit(self.shark_img, self.shark_rect)
        self.screen.blit(self.fish["img"], self.fish["rect"])
        self.screen.blit(self.obstacle["img"], self.obstacle["rect"])
        # Draw score at top left
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        # Draw timer at top right
        if self.final_time is not None:
            elapsed_seconds = self.final_time
        else:
            elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        timer_text = self.font.render(f"Time: {elapsed_seconds}s", True, WHITE)
        timer_rect = timer_text.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(timer_text, timer_rect)
        # Draw instructions at the bottom center
        instructions_text = self.instructions_font.render(
            "Use UP and DOWN arrow keys to move the shark", True, WHITE
        )
        instructions_rect = instructions_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        self.screen.blit(instructions_text, instructions_rect)
        # Draw touch buttons (always visible)
        pygame.draw.rect(self.screen, (0, 120, 255), self.up_btn_rect, border_radius=15)
        pygame.draw.rect(self.screen, (0, 120, 255), self.down_btn_rect, border_radius=15)
        up_text = self.button_font.render("Up", True, WHITE)
        down_text = self.button_font.render("Down", True, WHITE)
        self.screen.blit(up_text, up_text.get_rect(center=self.up_btn_rect.center))
        self.screen.blit(down_text, down_text.get_rect(center=self.down_btn_rect.center))
        # Draw game over message and buttons if game is over
        if self.game_over:
            over_text = self.font.render("Game Over!", True, WHITE)
            self.screen.blit(over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 40))
            # Draw Replay button
            replay_text = self.button_font.render("Replay", True, WHITE)
            self.replay_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 20, 100, 50)
            pygame.draw.rect(self.screen, (0, 150, 0), self.replay_rect)
            self.screen.blit(replay_text, replay_text.get_rect(center=self.replay_rect.center))
        pygame.display.update()

    async def run(self):
        """Main game loop."""
        fish_speed = 6
        obstacle_speed = 7
        running = True
        move_up = False
        move_down = False
        while running:
            self.clock.tick(60)
            await asyncio.sleep(0)
            # Restart music if it stops and game is not over
            if not self.game_over and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1, MUSIC_START_TIME)
            # Increase speed after certain intervals
            elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
            if elapsed_seconds >= 10:
                fish_speed = 8
                obstacle_speed = 10
            elif elapsed_seconds >= 20:
                fish_speed = 10
                obstacle_speed = 12
            elif elapsed_seconds >= 30:
                fish_speed = 12
                obstacle_speed = 14
            if not self.game_over:
                # Move fish and obstacle leftward
                self.fish["rect"].x -= fish_speed
                self.obstacle["rect"].x -= obstacle_speed
                # Respawn fish/obstacle if off screen
                if self.fish["rect"].right < 0:
                    self.fish = self.create_fish()
                if self.obstacle["rect"].right < 0:
                    self.obstacle = self.create_obstacle()
                # Check for collisions
                if self.shark_rect.colliderect(self.fish["rect"]):
                    self.score += self.fish["score"]
                    self.fish = self.create_fish()
                if self.shark_rect.colliderect(self.obstacle["rect"]):
                    self.game_over = True
                    if self.final_time is None:
                        self.final_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
                    pygame.mixer.music.stop()
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Touch/mouse button down
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.up_btn_rect.collidepoint(mouse_pos):
                        move_up = True
                    if self.down_btn_rect.collidepoint(mouse_pos):
                        move_down = True
                    if self.game_over and event.button == 1:
                        if self.replay_rect.collidepoint(mouse_pos):
                            self.reset_game()
                # Touch/mouse button up
                if event.type == pygame.MOUSEBUTTONUP:
                    move_up = False
                    move_down = False
            # Handle keyboard input for shark movement
            keys = pygame.key.get_pressed()
            if not self.game_over:
                if (keys[pygame.K_UP] or move_up) and self.shark_rect.top > 0:
                    self.shark_rect.y -= 5
                if (keys[pygame.K_DOWN] or move_down) and self.shark_rect.bottom < HEIGHT:
                    self.shark_rect.y += 5
            # Draw everything
            self.draw_window()
        # Only quit/exit if not running in pygbag/web
        if 'PYGBAG' not in sys.modules:
            pygame.quit()
            sys.exit()

async def main():
    # Initialize the game
    game = BabySharkGame()
    # Run the game loop
    await game.run()

if __name__ == "__main__":
    # Start the game
    asyncio.run(main())