"""
Flappy Bird Game
---------------
A modern implementation of the classic Flappy Bird game using Pygame.
Features include:
- Smooth bird animation and physics
- High score tracking
- Pause functionality
- Modern UI with visual effects
- Multiple control options
"""

import pygame
from pygame.locals import *
import random
import json
import math


# ============================================================================
#                              GAME INITIALIZATION
# ============================================================================

pygame.init()

# Game window settings
clock = pygame.time.Clock()
fps = 60
screen_width = 500
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# ============================================================================
#                              FONT CONFIGURATION
# ============================================================================

font = pygame.font.SysFont('Bauhaus 93', 40)        # Main game font
small_font = pygame.font.SysFont('Bauhaus 93', 28)  # UI elements font
medium_font = pygame.font.SysFont('Bauhaus 93', 35) # Secondary elements font

# ============================================================================
#                              COLOR DEFINITIONS
# ============================================================================

# Primary colors
white = (255, 255, 255)
black = (0, 0, 0)


# UI Theme colors
purple = (147, 112, 219)
light_purple = (178, 132, 255)
teal = (0, 183, 193)
dark_purple = (75, 61, 96)

# Effect colors
neon_blue = (4, 217, 255)
neon_purple = (179, 0, 255)
red = (255, 100, 100)
blue = (100, 200, 255)

# ============================================================================
#                              GAME VARIABLES
# ============================================================================

# Movement and animation
ground_scroll = 0
scroll_speed = 3
flying = False

# Game states
game_over = False
game_started = False
game_paused = False

# Gameplay mechanics
pipe_gap = 160
pipe_frequency = 1800
last_pipe = pygame.time.get_ticks() - pipe_frequency

# Scoring system
score = 0
pass_pipe = False
fade_counter = 0
score_blink = 0

# ============================================================================
#                           HIGH SCORE MANAGEMENT
# ============================================================================

# Load high score from file
def load_high_score():
	try:
		with open('high_score.json', 'r') as f:
			data = json.load(f)
			return data.get('high_score', 0)
	except:
		return 0

# Save high score to file
def save_high_score(score):
	with open('high_score.json', 'w') as f:
		json.dump({'high_score': score}, f)

high_score = load_high_score()

# ============================================================================
#                              ASSET LOADING
# ============================================================================

# Load game images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')

# Create overlay for modal screens
overlay = pygame.Surface((screen_width, screen_height))
overlay.fill((0, 0, 0))
overlay.set_alpha(128)

# ============================================================================
#                              UI COMPONENTS
# ============================================================================

# Create pause button with better design
def create_pause_button():
	size = 40
	button = pygame.Surface((size, size), pygame.SRCALPHA)
	
	# Draw rounded rectangle background
	pygame.draw.rect(button, (*purple, 200), (0, 0, size, size), border_radius=10)
	
	# Draw pause bars with gradient
	for i in range(3):
		alpha = 255 - i * 20
		color = (*white, alpha)
		pygame.draw.rect(button, color, (10, 8, 8, 24))
		pygame.draw.rect(button, color, (22, 8, 8, 24))
	
	return button

pause_img = create_pause_button()

def draw_panel(x, y, width, height):
	pygame.draw.rect(screen, white, (x, y, width, height), border_radius=10)
	pygame.draw.rect(screen, (220, 220, 220), (x, y, width, height), 2, border_radius=10)

def draw_score():
	global score_blink
	score_blink = (score_blink + 1) % 60
	
	# Clean, modern score display
	score_text = font.render(str(score), True, white)
	score_rect = score_text.get_rect(center=(screen_width // 2, 40))
	
	# Simple glow effect - moved higher
	glow_intensity = abs(math.sin(pygame.time.get_ticks() / 800))
	glow_surface = pygame.Surface((80, 50), pygame.SRCALPHA)
	pygame.draw.circle(glow_surface, (*neon_blue, 40), (40, 20), 30 * glow_intensity)  # y changed from 25 to 20
	
	# Position and draw score
	screen_rect = glow_surface.get_rect(center=(screen_width // 2, 40))
	screen.blit(glow_surface, screen_rect)
	screen.blit(score_text, score_rect)
	
	# Always show high score during gameplay with white color
	high_text = small_font.render(f'Best: {high_score}', True, white)
	high_rect = high_text.get_rect(topright=(screen_width - 20, 15))
	screen.blit(high_text, high_rect)

def draw_pause_button():
	# Simplified pause button
	button_rect = pygame.Rect(20, 20, 40, 40)
	
	# Button background
	pygame.draw.rect(screen, dark_purple, button_rect, border_radius=10)
	pygame.draw.rect(screen, teal, button_rect, 2, border_radius=10)
	
	# Pause icon
	if not game_paused:
		pygame.draw.rect(screen, white, (30, 28, 6, 24))
		pygame.draw.rect(screen, white, (44, 28, 6, 24))
	else:
		# Play icon when paused
		pygame.draw.polygon(screen, white, [(32, 28), (32, 52), (52, 40)])
	
	if game_paused:
		# Clean, minimal pause overlay
		overlay = pygame.Surface((screen_width, screen_height))
		overlay.fill((0, 0, 0))
		overlay.set_alpha(120)
		screen.blit(overlay, (0, 0))
		
		# Simple pause menu
		menu_width = 300
		menu_height = 250  # Increased height significantly
		menu_x = (screen_width - menu_width) // 2
		menu_y = (screen_height - menu_height) // 2
		
		# Menu background
		pygame.draw.rect(screen, dark_purple, 
						(menu_x, menu_y, menu_width, menu_height),
						border_radius=15)
		pygame.draw.rect(screen, teal, 
						(menu_x, menu_y, menu_width, menu_height),
						2, border_radius=15)
		
		# Pause text - moved even lower
		draw_text('PAUSED', font, white, screen_width // 2, menu_y + 100)
		
		# Simple instruction - moved even lower
		instruction_alpha = abs(math.sin(pygame.time.get_ticks() / 500)) * 255
		instruction_text = small_font.render('Press SPACE to Resume', True, (200, 200, 200))
		instruction_text.set_alpha(int(instruction_alpha))
		instruction_rect = instruction_text.get_rect(center=(screen_width // 2, menu_y + 220))
		screen.blit(instruction_text, instruction_rect)

def draw_game_over_screen():
	global fade_counter
	
	# Simple dark overlay
	overlay.set_alpha(min(120, fade_counter * 4))
	screen.blit(overlay, (0,0))
	
	# Clean panel design
	panel_width = 300
	panel_height = 400  # Increased height significantly
	panel_x = (screen_width - panel_width) // 2
	panel_y = (screen_height - panel_height) // 2
	
	# Main panel
	pygame.draw.rect(screen, dark_purple, 
					(panel_x, panel_y, panel_width, panel_height),
					border_radius=15)
	pygame.draw.rect(screen, teal, 
					(panel_x, panel_y, panel_width, panel_height),
					2, border_radius=15)
	
	# Game Over text
	draw_text('GAME OVER', font, white, screen_width // 2, panel_y + 100)  # Moved much lower
	
	# Score display
	score_y = panel_y + 180  # Moved much lower
	draw_text('Score', small_font, (200, 200, 200), screen_width // 2, score_y)
	draw_text(str(score), font, white, screen_width // 2, score_y + 40)
	
	# High score with simple animation
	if fade_counter > 10:
		best_y = score_y + 100  # Increased spacing
		draw_text('Best Score', small_font, (255,255,255), screen_width // 2, best_y)
		draw_text(str(high_score), font, teal, screen_width // 2, best_y + 40)
	
	# Restart instruction - moved much lower
	if fade_counter > 30:
		instruction_alpha = abs(math.sin(pygame.time.get_ticks() / 500)) * 255
		instruction_text = small_font.render('Press SPACE to Restart', True, (200, 200, 200))
		instruction_text.set_alpha(int(instruction_alpha))
		instruction_rect = instruction_text.get_rect(center=(screen_width // 2, panel_y + 370))  # Moved much lower
		screen.blit(instruction_text, instruction_rect)
	
	fade_counter += 1

def draw_score_panel(title, value, x, y, width, height, color):
	# Panel background with gradient
	for i in range(height):
		alpha = 180 - (i / height * 60)
		s = pygame.Surface((width, 1))
		s.fill(dark_purple)
		s.set_alpha(int(alpha))
		screen.blit(s, (x, y + i))
	
	# Animated border
	border_glow = abs(math.sin(pygame.time.get_ticks() / 1000))
	border_color = (
		int(color[0] * border_glow + teal[0] * (1-border_glow)),
		int(color[1] * border_glow + teal[1] * (1-border_glow)),
		int(color[2] * border_glow + teal[2] * (1-border_glow))
	)
	pygame.draw.rect(screen, border_color, 
					(x, y, width, height), 
					2, border_radius=10)
	
	# Draw text with glow effect
	draw_text(title, small_font, white, x + width//2, y + 25)
	
	value_glow = abs(math.sin(pygame.time.get_ticks() / 800))
	for offset in range(3, 0, -1):
		alpha = int(value_glow * 60 * (4-offset))
		draw_text(str(value), font, (*color, alpha), 
				 x + width//2 + offset//2, y + 60 + offset//2)
	draw_text(str(value), font, color, x + width//2, y + 60)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	rect = img.get_rect()
	rect.center = (x, y)
	screen.blit(img, rect)

def reset_game():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score

def draw_start_screen():
	draw_text('FLAPPY BIRD', font, white, screen_width // 2, screen_height // 4)
	draw_text('Click or Press SPACE', small_font, white, screen_width // 2, screen_height // 2)
	draw_text('to Start', small_font, white, screen_width // 2, screen_height // 2 + 40)

# ============================================================================
#                              GAME CLASSES
# ============================================================================

class Bird(pygame.sprite.Sprite):
    """
    Bird class handling player character mechanics including:
    - Animation states
    - Physics (gravity and jumping)
    - Collision detection
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range (1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying == True:
            #apply gravity
            self.vel += 0.3  # Reduced from 0.4 for slower falling
            if self.vel > 5:  # Reduced from 6
                self.vel = 5
            if self.rect.bottom < screen_height - 168:
                self.rect.y += int(self.vel)

        if game_over == False:
            #jump
            keys = pygame.key.get_pressed()
            if (pygame.mouse.get_pressed()[0] == 1 or 
                keys[K_SPACE] or keys[K_UP]) and self.clicked == False:
                self.clicked = True
                self.vel = -7
            if (pygame.mouse.get_pressed()[0] == 0 and 
                not keys[K_SPACE] and not keys[K_UP]):
                self.clicked = False

            #handle the animation
            flap_cooldown = 5
            self.counter += 1
            
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            #point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    """
    Pipe class managing obstacle mechanics:
    - Positioning (top/bottom)
    - Movement
    - Cleanup when off-screen
    """
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        #position variable determines if the pipe is coming from the bottom or top
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    """
    Generic button class for UI interactions:
    - Click detection
    - Visual feedback
    - Action triggering
    """
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# ============================================================================
#                              GAME LOOP
# ============================================================================

# Initialize sprite groups
pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

# Create player character
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Main game loop
run = True
while run:
	clock.tick(fps)

	#draw background
	screen.blit(bg, (0,0))

	if game_started and not game_paused:
		pipe_group.draw(screen)
		bird_group.draw(screen)
		bird_group.update()
	elif not game_started:
		bird_group.draw(screen)
		draw_start_screen()

	#draw and scroll the ground
	screen.blit(ground_img, (ground_scroll, screen_height - 168))

	if game_started and not game_over:
		draw_score()
		draw_pause_button()

	#check the score
	if len(pipe_group) > 0 and not game_paused:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				pass_pipe = False
				if score > high_score:
					high_score = score
	
	if flying == True and game_over == False and not game_paused:
		#generate new pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-75, 75)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		pipe_group.update()

		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0
	
	# Check for collisions
	if game_started and not game_paused:
		# Check for pipe collision or hitting the top of the screen
		if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
			game_over = True
			game_started = False
			flying = False
		
		# Check for ground collision
		if flappy.rect.bottom >= screen_height - 168:
			game_over = True
			game_started = False
			flying = False

	#check for game over and reset
	if game_over == True:
		draw_game_over_screen()
		# Check for restart input
		keys = pygame.key.get_pressed()
		if fade_counter > 20 and (pygame.mouse.get_pressed()[0] or keys[K_SPACE] or keys[K_RETURN]):
			game_over = False
			game_started = True
			fade_counter = 0
			flying = False
			if score > high_score:
				high_score = score
				save_high_score(high_score)
			score = reset_game()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_pos = pygame.mouse.get_pos()
			if not game_over and game_started:
				# Check if pause button clicked
				if mouse_pos[0] < 60 and mouse_pos[1] < 60:
					game_paused = not game_paused
				elif not game_paused:
					flying = True
			elif not game_over and not game_started:
				flying = True
				game_started = True
		if event.type == pygame.KEYDOWN:
			if event.key in [pygame.K_SPACE, pygame.K_UP]:
				if game_paused:
					game_paused = False
				elif not flying and not game_over:
					flying = True
					game_started = True
			elif event.key == pygame.K_RETURN:  # Add Enter key for pause
				if game_started and not game_over:
					game_paused = not game_paused

	pygame.display.update()

pygame.quit()