import pygame
import sys
import os
import random
import math


pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumpocalyps")


BLACK = (0, 0, 0)
SKY_COLOR = (25, 25, 40)
PLATFORM_COLOR = (0, 150, 255)
PLATFORM_BORDER = (0, 200, 255)
OBSTACLE_COLOR = (255, 50, 50)
PARTICLE_COLORS = [(100, 200, 255, 200)]
DEATH_PARTICLE_COLORS = [
    (255, 50, 50, 200),
    (255, 150, 50, 200),
    (255, 255, 50, 200)
]


TILE_SIZE = 50
LEVEL_WIDTH = 100  
LEVEL_HEIGHT = 12  
SCROLL_SPEED = 5


try:
    original_img = pygame.image.load("assets/character.png").convert_alpha()
    character_img = pygame.transform.scale(original_img, (TILE_SIZE, TILE_SIZE))
    player_width, player_height = TILE_SIZE, TILE_SIZE
except:
    print("Error pri nacitani obrazku charakteru")
    character_img = None
    player_width, player_height = TILE_SIZE, TILE_SIZE


particles = []
death_particles = []
PARTICLE_SPAWN_RATE = 0.4
PARTICLE_LIFETIME = 20
PARTICLE_SPEED = -2.5
on_ground = False


player_x = TILE_SIZE * 3
player_y = TILE_SIZE * 5
player_speed_x = SCROLL_SPEED
player_speed_y = 0
scroll_x = 0
rotation_angle = 0
target_angle = 0
rotation_speed = 5


is_dead = False
death_timer = 0
death_duration = 60
death_circle_radius = 0


GRAVITY = 0.8
JUMP_STRENGTH = -20
is_jumping = False
is_rotating = False


EMPTY = 0
PLATFORM = 1
TRIANGLE = 2         
WIDE_TRIANGLE = 3    
TRIANGLE_AREA = 4    
INVERTED_TRIANGLE = 5 
PLATFORM_BIG = 6
PORTAL = 7  
PORTAL_COLOR = (150, 50, 255)
PORTAL_GLOW_COLOR = (200, 100, 255, 100)
PORTAL_SIZE = TILE_SIZE * 1.5



PORTAL_COLOR = (150, 50, 255)  
PORTAL_GLOW_COLOR = (200, 100, 255, 50)  
PORTAL_BORDER_COLOR = (0, 0, 0)  
PORTAL_HIGHLIGHT_COLOR = (255, 255, 255)  
PORTAL_SIZE = TILE_SIZE * 1.5  
PORTAL_SPIN_SPEED = 3  

def draw_portal(x, y, size, rotation):
    
    center_x = x - scroll_x
    center_y = y
    
   
    portal_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    
    
    for i in range(3, 0, -1):
        glow_size = size + i * 5
        alpha = 50 - i * 15
        pygame.draw.circle(
            portal_surface, 
            (*PORTAL_GLOW_COLOR[:3], alpha), 
            (size, size), 
            glow_size
        )
    
    
    for i in range(int(size//2), int(size//4), -2):
        alpha = 200 - (i * 100 // (size//2))
        color = (*PORTAL_COLOR, alpha)
        pygame.draw.circle(portal_surface, color, (size, size), i)
    
    
    pygame.draw.circle(portal_surface, PORTAL_BORDER_COLOR, (size, size), size//2, 3)
    
     
    inner_size = size//2 - 5
    
    
    for i in range(4):
        angle = rotation + (math.pi/2 * i)
        start_pos = (
            size + inner_size * 0.3 * math.cos(angle),
            size + inner_size * 0.3 * math.sin(angle)
        )
        end_pos = (
            size + inner_size * 0.9 * math.cos(angle),
            size + inner_size * 0.9 * math.sin(angle)
        )
        pygame.draw.line(
            portal_surface, 
            PORTAL_HIGHLIGHT_COLOR, 
            start_pos, 
            end_pos, 
            3
        )
    
    
    pygame.draw.circle(portal_surface, PORTAL_HIGHLIGHT_COLOR, (size, size), inner_size//2, 2)
    
    
    pygame.draw.circle(portal_surface, PORTAL_HIGHLIGHT_COLOR, (size, size), 3)
    
    
    screen.blit(portal_surface, (center_x - size, center_y - size))
    
    
    line_length = size * 1.2
    line_y = center_y + size//2 + 5
    pygame.draw.line(
        screen, 
        PORTAL_HIGHLIGHT_COLOR, 
        (center_x - line_length//2, line_y), 
        (center_x + line_length//2, line_y), 
        3
    )

def load_level(filename):
    
    platforms = []
    obstacles = []
    portals = [] 
    
    
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
            for y, line in enumerate(lines):
                
                cleaned = ''.join(c for c in line if c in '0123456789')
                
                for x, char in enumerate(cleaned):
                    code = int(char)
                    pos_x = x * TILE_SIZE
                    pos_y = y * TILE_SIZE
                    
                    if code == PLATFORM:
                        platforms.append({
                            "x": pos_x,
                            "y": pos_y + TILE_SIZE - TILE_SIZE//2,  
                            "width": TILE_SIZE,
                            "height": TILE_SIZE//2
                        })
                    elif code == TRIANGLE:
                        obstacles.append({
                            "x": pos_x + TILE_SIZE//2,
                            "y": pos_y ,  
                            "width": TILE_SIZE,
                            "height": TILE_SIZE,
                            "direction": "up"
                        })
                    elif code == WIDE_TRIANGLE:
                        obstacles.append({
                            "x": pos_x + TILE_SIZE//2,
                            "y": pos_y +  TILE_SIZE//2,  
                            "width": TILE_SIZE * 1.5,
                            "height": TILE_SIZE//2,
                            "direction": "up"
                        })
                    elif code == TRIANGLE_AREA:
                        
                        for i in range(3):
                            offset = i * TILE_SIZE//2
                            obstacles.append({
                                "x": pos_x + TILE_SIZE//2,
                                "y": pos_y ,
                                "width": TILE_SIZE,
                                "height": TILE_SIZE,
                                "direction": "up"
                            })
                    elif code == INVERTED_TRIANGLE:
                        obstacles.append({
                            "x": pos_x + TILE_SIZE//2,
                            "y": pos_y,  
                            "width": TILE_SIZE,
                            "height": TILE_SIZE,
                            "direction": "down"
                        })

                    elif code == PLATFORM_BIG:
                        platforms.append({
                            "x": pos_x,
                            "y": pos_y + TILE_SIZE - TILE_SIZE,  
                            "width": TILE_SIZE,
                            "height": TILE_SIZE
                        })

                    elif code == PORTAL:
                        portals.append({
                            "x": pos_x + TILE_SIZE//2,
                            "y": pos_y + TILE_SIZE//2,
                            "size": PORTAL_SIZE,
                            "rotation": 0
                        })
        
        return platforms, obstacles, portals  
    
    except FileNotFoundError:
        print(f"Error: slozks levelu '{filename}' nebyla nalezena. pouziva se takladni level.")
        return create_default_level()

def create_default_level():
    
    platforms = [
        {"x": 0, "y": 500, "width": 600, "height": 20},
        {"x": 700, "y": 450, "width": 300, "height": 20},
        {"x": 1100, "y": 400, "width": 300, "height": 20},
    ]
    
    obstacles = [
        
        {"x": 650, "y": 430, "width": 40, "height": 40, "direction": "up"},
        
        {"x": 1200, "y": 380, "width": 80, "height": 30, "direction": "up"},
        
        {"x": 900, "y": 350, "width": 40, "height": 40, "direction": "down"},
        
        {"x": 1500, "y": 380, "width": 40, "height": 40, "direction": "up"},
        {"x": 1550, "y": 380, "width": 40, "height": 40, "direction": "up"},
        {"x": 1600, "y": 380, "width": 40, "height": 40, "direction": "up"},
    ]
    
    return platforms, obstacles



def generate_obstacle_area(area_config):
    
    area_obstacles = []
    platform = platforms[area_config["platform_idx"]]
    
    for i in range(area_config["count"]):
        x = area_config["start_x"] + i * area_config["spacing"]
        width = random.randint(30, 60)
        height = random.randint(
            area_config["min_height"],
            area_config["max_height"]
        )
        
        
        if area_config["direction"] == "up":
            y = platform["y"] - height + area_config["y_offset"]
        else:  
            y = platform["y"] - platform["height"] + area_config["y_offset"]
        
        area_obstacles.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "platform_idx": area_config["platform_idx"],
            "direction": area_config["direction"]
        })
    
    return area_obstacles



stars = []
for _ in range(100):
    stars.append({
        "x": random.randint(0, LEVEL_WIDTH * TILE_SIZE),
        "y": random.randint(0, SCREEN_HEIGHT),
        "size": random.randint(1, 3),
        "speed": random.uniform(0.1, 0.5),
        "brightness": random.randint(100, 255)
    })
def draw_crystal(x, y, width, height):
    
    
    pygame.draw.rect(screen, 'red', (x, y, width, height))
    
    
    for i in range(5):
        cx = x + random.randint(0, width)
        cy = y + random.randint(0, height)
        size = random.randint(5, 10)
        points = []
        for j in range(6):  
            angle = math.pi * 2 * j / 6
            points.append((
                cx + size * math.cos(angle),
                cy + size * math.sin(angle)
            ))
        pygame.draw.polygon(screen, (200, 255, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 1)

def create_death_particles(x, y):
    particles = []
    for _ in range(30):
        size = random.randint(3, 8)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        particles.append({
            "x": x,
            "y": y,
            "size": size,
            "color": random.choice(DEATH_PARTICLE_COLORS),
            "life": random.randint(30, 45),
            "speed_x": math.cos(angle) * speed,
            "speed_y": math.sin(angle) * speed
        })
    return particles

def update_death_particles():
    global death_particles
    for particle in death_particles[:]:
        particle["x"] += particle["speed_x"]
        particle["y"] += particle["speed_y"]
        particle["life"] -= 1
        if particle["life"] <= 0:
            death_particles.remove(particle)

def draw_death_particles():
    for particle in death_particles:
        alpha = min(255, particle["life"] * 6)
        color = (*particle["color"][:3], alpha)
        surf = pygame.Surface((particle["size"]*2, particle["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (particle["size"], particle["size"]), particle["size"])
        screen.blit(surf, (particle["x"], particle["y"]))

def draw_background():
    
    screen.fill(SKY_COLOR)
    for star in stars:
        adjusted_x = (star["x"] - scroll_x * star["speed"]) % (LEVEL_WIDTH * TILE_SIZE)
        brightness = star["brightness"]
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(adjusted_x), star["y"]), star["size"])

def draw_platform(x, y, width, height):
    
    pygame.draw.rect(screen, PLATFORM_COLOR, (x, y, width, height))
    pygame.draw.rect(screen, PLATFORM_BORDER, (x, y, width, 3))
    pygame.draw.rect(screen, PLATFORM_BORDER, (x, y + height - 1, width, 1))
    pygame.draw.rect(screen, PLATFORM_BORDER, (x, y, 2, height))
    pygame.draw.rect(screen, PLATFORM_BORDER, (x + width - 2, y, 2, height))

def draw_obstacle(x, y, width, height, direction="up"):
    
    if direction == "up":
        points = [
            (x, y),
            (x - width//2, y + height),
            (x + width//2, y + height)
        ]
    else:  
        points = [
            (x - width//2, y),
            (x + width//2, y),
            (x, y + height)
        ]
    
    pygame.draw.polygon(screen, OBSTACLE_COLOR, points)
    pygame.draw.polygon(screen, (255, 100, 100), points, 2)


def create_particle(x, y):
    size = random.randint(2, 5)
    return {
        "x": x - random.randint(0, 15),
        "y": y + player_height - 5,
        "size": size,
        "color": random.choice(PARTICLE_COLORS),
        "life": PARTICLE_LIFETIME,
        "speed_x": PARTICLE_SPEED * random.uniform(0.7, 1.3),
        "speed_y": random.uniform(-0.5, 0.5),
    }

def update_particles():
    global particles
    if on_ground and player_speed_x > 0 and random.random() < PARTICLE_SPAWN_RATE:
        particles.append(create_particle(player_x - scroll_x, player_y))
    
    for particle in particles[:]:
        particle["x"] += particle["speed_x"]
        particle["y"] += particle["speed_y"]
        particle["life"] -= 1
        if particle["life"] <= 0 or particle["x"] < -50:
            particles.remove(particle)

def draw_particles():
    for particle in particles:
        alpha = min(255, particle["life"] * 12)
        color = (*particle["color"][:3], alpha)
        surf = pygame.Surface((particle["size"]*2, particle["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (particle["size"], particle["size"]), particle["size"])
        screen.blit(surf, (particle["x"], particle["y"]))

def get_player_rect(x, y):
    return pygame.Rect(x - scroll_x, y, player_width, player_height)

def get_obstacle_rect(x, y, width, height, obstacle_type):
    if obstacle_type == "spike":
        return pygame.Rect(x - width//2, y, width, height)
    else:  
        return pygame.Rect(x, y, width, height)




def draw_death_effect():
    if death_timer > 0:
        progress = 1 - (death_timer / death_duration)
        current_radius = death_circle_radius * (1 - progress)
        alpha = int(200 * (1 - progress))
        
        circle_surf = pygame.Surface((int(current_radius*2), int(current_radius*2)), pygame.SRCALPHA)
        pygame.draw.circle(
            circle_surf, 
            (255, 255, 255, alpha), 
            (int(current_radius), int(current_radius)), 
            int(current_radius)
        )
        
        screen.blit(
            circle_surf,
            (player_x - scroll_x + player_width//2 - current_radius,
             player_y + player_height//2 - current_radius)
        )


player_speed_y = 0


initial_platforms = []
initial_obstacles = []
is_restarting = False
restart_timer = 0
restart_duration = 60  




platforms, obstacles,portals = load_level("easy-level.txt")
initial_platforms = platforms.copy()
initial_obstacles = obstacles.copy()
initial_portals = portals.copy()  

def reset_game():
    
    global player_x, player_y, player_speed_x, player_speed_y, scroll_x
    global rotation_angle, target_angle, is_jumping, is_rotating, on_ground
    global is_dead, death_timer, death_particles, particles, death_circle_radius
    global platforms, obstacles
    global portals
    portals = initial_portals.copy()
    difficulty = selected_level.upper()
    
    music_file = f"assets/{difficulty}.mp3"
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(1)  
        
    except pygame.error as e:
        print(f"Error pri nacitani muziky: {e}")
    
   
    player_x = TILE_SIZE * 3
    player_y = TILE_SIZE * 5
    player_speed_x = SCROLL_SPEED
    player_speed_y = 0
    scroll_x = 0
    rotation_angle = 0
    target_angle = 0
    is_jumping = False
    is_rotating = False
    on_ground = False
    
    
    is_dead = False
    death_timer = 0
    death_particles = []
    particles = []
    
    
    platforms = initial_platforms.copy()
    obstacles = initial_obstacles.copy()

def check_collisions(player_rect):
    
    global on_ground, is_dead, death_particles, death_timer, death_circle_radius,player_speed_y
    
    on_ground = False
    new_x, new_y = player_rect.x, player_rect.y
    was_on_ground = on_ground
   
    
    
    for platform in platforms:
        platform_rect = pygame.Rect(
            platform["x"] - scroll_x,
            platform["y"],
            platform["width"],
            platform["height"]
        )
        
        if player_rect.colliderect(platform_rect) and not in_menu:
            
            overlap_left = player_rect.right - platform_rect.left
            overlap_right = platform_rect.right - player_rect.left
            overlap_top = player_rect.bottom - platform_rect.top
            overlap_bottom = platform_rect.bottom - player_rect.top
            
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            
            if min_overlap == overlap_top and player_speed_y >= 0:
                on_ground = True
                new_y = platform_rect.top - player_height
                player_speed_y = 0
            
            
            elif min_overlap == overlap_bottom and player_speed_y < 0:
                new_y = platform_rect.bottom
                player_speed_y = 0  
                
                
                if was_on_ground:
                    new_y = player_rect.y  
            
            
            elif min_overlap == overlap_left:
                new_x = platform_rect.left - player_width
                player_speed_x = 0
            
            
            elif min_overlap == overlap_right:
                new_x = platform_rect.right
                player_speed_x = 0
    
   
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(
            obstacle["x"] - obstacle["width"]//2 - scroll_x,
            obstacle["y"],
            obstacle["width"],
            obstacle["height"]
        )
        
        if player_rect.colliderect(obstacle_rect) and not is_dead and not in_menu:
            is_dead = True
            death_particles = create_death_particles(
                player_x - scroll_x + player_width//2,
                player_y + player_height//2
            )
            death_timer = death_duration
            death_circle_radius = max(player_width, player_height) // 2
    
    return new_x, new_y


MENU_COLORS = {
    'background': (25, 25, 40),
    'button': (0, 150, 255),
    'button_hover': (0, 200, 255),
    'text': (255, 255, 255),
    'title': (0, 200, 255),
    'slider': (100, 200, 255),
    'slider_knob': (255, 255, 255),
    'easy': (50, 200, 50),
    'medium': (200, 200, 50),
    'hard': (200, 50, 50)
}


in_menu = True
current_menu = "main"  
volume = 0.8
is_muted = False
dragging_volume = False
selected_level = None

class Button:
    def __init__(self, x, y, width, height, text, action, btn_type="normal", color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.type = btn_type
        self.color = color if color else MENU_COLORS['button']
        self.hover_color = self._get_hover_color()
        
        if self.type == "slider":
            self.knob_pos = x + int(width * volume)
            self.knob_rect = pygame.Rect(self.knob_pos - 10, y - 5, 20, height + 10)
    
    def _get_hover_color(self):
        if self.action == "easy":
            return (100, 255, 100)
        elif self.action == "medium":
            return (255, 255, 100)
        elif self.action == "hard":
            return (255, 100, 100)
        return MENU_COLORS['button_hover']
    
    def draw(self, surface):
        if self.type == "normal":
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=10)
            pygame.draw.rect(surface, MENU_COLORS['text'], self.rect, 2, border_radius=10)
            
            font = pygame.font.SysFont('Arial', 30)
            text_surf = font.render(self.text, True, MENU_COLORS['text'])
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        
        elif self.type == "slider":
            pygame.draw.rect(surface, MENU_COLORS['slider'], 
                           (self.rect.x, self.rect.y + self.rect.height//2 - 2, 
                            self.rect.width, 4))
            self.knob_rect = pygame.Rect(self.knob_pos - 10, self.rect.y - 5, 20, self.rect.height + 10)
            pygame.draw.rect(surface, MENU_COLORS['slider_knob'], self.knob_rect, border_radius=5)
            
            font = pygame.font.SysFont('Arial', 25)
            vol_text = "MUTED" if is_muted else f"VOLUME: {int(volume*100)}%"
            text_surf = font.render(vol_text, True, MENU_COLORS['text'])
            surface.blit(text_surf, (self.rect.x, self.rect.y - 30))
    
    def check_hover(self, pos):
        if self.type == "slider":
            self.is_hovered = self.knob_rect.collidepoint(pos)
        else:
            self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def handle_event(self, event):
        global volume, is_muted, dragging_volume, selected_level
        
        if self.type == "slider":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                dragging_volume = True
                return "volume_drag_start"
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_volume:
                dragging_volume = False
                return "volume_drag_end"
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                if self.action == "mute":
                    is_muted = not is_muted
                    if is_muted:
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(volume)
                return self.action
        return None


menu_buttons = [
    Button(SCREEN_WIDTH//2 - 100, 200, 200, 50, "START", "level_select"),
    Button(SCREEN_WIDTH//2 - 100, 270, 200, 50, "SETTINGS", "settings"),
    Button(SCREEN_WIDTH//2 - 100, 340, 200, 50, "QUIT", "quit")
]

settings_buttons = [
    Button(SCREEN_WIDTH//2 - 100, 150, 200, 50, "MUTE", "mute"),
    Button(SCREEN_WIDTH//2 - 100, 230, 200, 10, "", "volume", "slider"),
    Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "BACK", "back")
]

level_select_buttons = [
    Button(SCREEN_WIDTH//2 - 100, 180, 200, 50, "EASY", "easy", "normal", MENU_COLORS['easy']),
    Button(SCREEN_WIDTH//2 - 100, 250, 200, 50, "MEDIUM", "medium", "normal", MENU_COLORS['medium']),
    Button(SCREEN_WIDTH//2 - 100, 320, 200, 50, "HARD", "hard", "normal", MENU_COLORS['hard']),
    Button(SCREEN_WIDTH//2 - 100, 400, 200, 50, "BACK", "back")
]

def update_volume_slider(pos):
    global volume
    for button in settings_buttons:
        if button.type == "slider":
            relative_x = pos[0] - button.rect.x
            volume = max(0, min(1, relative_x / button.rect.width))
            button.knob_pos = button.rect.x + int(button.rect.width * volume)
            
            if not is_muted:
                pygame.mixer.music.set_volume(volume)
            break

def draw_menu():
    
    draw_background()
    
    titles = {
        "main": "Jumpocalyps",
        "settings": "SETTINGS",
        "level_select": "SELECT LEVEL"
    }
    
    title_font = pygame.font.SysFont('Arial', 50, bold=True)
    title_text = title_font.render(titles[current_menu], True, MENU_COLORS['title'])
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 80))
    
    buttons = []
    if current_menu == "main":
        buttons = menu_buttons
    elif current_menu == "settings":
        buttons = settings_buttons
    elif current_menu == "level_select":
        buttons = level_select_buttons
    
    for button in buttons:
        button.draw(screen)
    
    

def handle_menu_events(event):
    
    buttons = []
    if current_menu == "main":
        buttons = menu_buttons
    elif current_menu == "settings":
        buttons = settings_buttons
    elif current_menu == "level_select":
        buttons = level_select_buttons
    
    for button in buttons:
        button.check_hover(pygame.mouse.get_pos())
        action = button.handle_event(event)
        if action:
            return action
    return None

def start_game(difficulty):
    
    global in_menu, selected_level, initial_platforms, initial_portals, initial_obstacles
    selected_level = difficulty
    in_menu = False

    
    music_file = f"assets/{difficulty}.mp3"
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(1)  
        
    except pygame.error as e:
        print(f"Error pri nacitani muziky: {e}")

    
    platforms, obstacles, portals = load_level(f"{difficulty}-level.txt")
    initial_platforms = platforms.copy()
    initial_obstacles = obstacles.copy()
    initial_portals = portals.copy()
    reset_game()


def draw_completion_message():
    
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    
    font_large = pygame.font.SysFont('Arial', 72, bold=True)
    text = font_large.render("LEVEL COMPLETED!", True, (0, 255, 0))
    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    
    
    if selected_level:
        font_small = pygame.font.SysFont('Arial', 36)
        level_text = font_small.render(f"Difficulty: {selected_level.upper()}", True, (255, 255, 255))
        screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2 + 30))



clock = pygame.time.Clock()
running = True


level_completed = False
completion_timer = 0
COMPLETION_DISPLAY_TIME = 180  

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if in_menu:
            if dragging_volume and event.type == pygame.MOUSEMOTION:
                update_volume_slider(event.pos)
            
            action = handle_menu_events(event)
            if action == "level_select":
                current_menu = "level_select"
            elif action == "settings":
                current_menu = "settings"
            elif action in ["easy", "medium", "hard"]:
                start_game(action)
            elif action == "back":
                current_menu = "main"
            elif action == "quit":
                running = False
        else:
           
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_menu = True  
                elif event.key == pygame.K_SPACE and not is_jumping and not is_dead:
                    player_speed_y = JUMP_STRENGTH
                    is_jumping = True
                    is_rotating = True
                    target_angle += 90
    if level_completed:
        completion_timer -= 1
        if completion_timer <= 0:
            level_completed = False
            in_menu = True
            current_menu = "main"
    
    if in_menu:
        draw_menu()
    else:
        draw_background()

    if level_completed:
            draw_completion_message()
    if is_restarting:
        restart_timer -= 1
        if restart_timer <= 0:
            is_restarting = False
            reset_game()
    
    if not is_dead and not is_restarting :
        
        player_x += player_speed_x
        player_speed_y += GRAVITY
        player_y += player_speed_y
        
        
        player_rect = pygame.Rect(
            player_x - scroll_x,
            player_y,
            player_width,
            player_height
        )
        
       
        new_x, new_y = check_collisions(player_rect)
        player_x = new_x + scroll_x
        player_y = new_y
        
      
        
       
        if is_rotating:
            angle_diff = (target_angle - rotation_angle) % 360
            if angle_diff > 180:
                angle_diff -= 360
            if abs(angle_diff) > 0.5:
                rotation_step = min(rotation_speed, abs(angle_diff))
                rotation_angle += rotation_step * (1 if angle_diff > 0 else -1)
            else:
                rotation_angle = target_angle
                is_rotating = False
        
        
        
        if on_ground:
            player_y = new_y
            player_speed_y = 0
            is_jumping = False
            rotation_angle = round(rotation_angle / 90) * 90
        
        
        scroll_x = player_x - SCREEN_WIDTH // 3
        
        
        if player_y > SCREEN_HEIGHT - player_height:
            player_y = SCREEN_HEIGHT - player_height
            player_speed_y = 0
            is_jumping = False
            rotation_angle = round(rotation_angle / 90) * 90
            on_ground = True
        
        
        if on_ground and player_speed_x > 0 and random.random() < PARTICLE_SPAWN_RATE:
            particles.append({
                "x": player_x - scroll_x - random.randint(0, 15),
                "y": player_y + player_height - 5,
                "size": random.randint(2, 5),
                "color": random.choice(PARTICLE_COLORS),
                "life": PARTICLE_LIFETIME,
                "speed_x": PARTICLE_SPEED * random.uniform(0.7, 1.3),
                "speed_y": random.uniform(-0.5, 0.5),
            })
        
        
        for particle in particles[:]:
            particle["x"] += particle["speed_x"]
            particle["y"] += particle["speed_y"]
            particle["life"] -= 1
            if particle["life"] <= 0 or particle["x"] < -50:
                particles.remove(particle)
    else:
        
        death_timer -= 1
        for particle in death_particles[:]:
            particle["x"] += particle["speed_x"]
            particle["y"] += particle["speed_y"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                death_particles.remove(particle)
        
        
        if death_timer <= 0 and not is_restarting:
            is_restarting = True
            restart_timer = restart_duration
    
    

    player_rect = get_player_rect(player_x, player_y)
    if not in_menu:
       
        for platform in platforms:
            draw_platform(
                platform["x"] - scroll_x,
                platform["y"],
                platform["width"],
                platform["height"]
            )

        
        for portal in portals[:]:
            portal_rect = pygame.Rect(
                portal["x"] - portal["size"]//2 - scroll_x,
                portal["y"] - portal["size"]//2,
                portal["size"],
                portal["size"]
            )

            if player_rect.colliderect(portal_rect) and not is_dead and not level_completed:
                level_completed = True
                completion_timer = COMPLETION_DISPLAY_TIME
        
        
        for obstacle in obstacles:
            draw_obstacle(
                obstacle["x"] - scroll_x,
                obstacle["y"],
                obstacle["width"],
                obstacle["height"],
                obstacle.get("direction", "up")
            )
        for portal in portals:
            portal["rotation"] += 0.05  
            draw_portal(portal["x"], portal["y"], portal["size"], portal["rotation"])
       
        for particle in particles:
            alpha = min(255, particle["life"] * 12)
            color = (*particle["color"][:3], alpha)
            surf = pygame.Surface((particle["size"]*2, particle["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (particle["size"], particle["size"]), particle["size"])
            screen.blit(surf, (particle["x"], particle["y"]))
        
   
    if not is_dead and not in_menu:
        if character_img:
            rotated_img = pygame.transform.rotate(character_img, rotation_angle)
            rotated_rect = rotated_img.get_rect(center=(player_x - scroll_x + player_width//2, 
                                           player_y + player_height//2))
            screen.blit(rotated_img, rotated_rect.topleft)
        else:
            pygame.draw.rect(screen, (255, 0, 0), (player_x - scroll_x, player_y, player_width, player_height))
    else:
        
        for particle in death_particles:
            alpha = min(255, particle["life"] * 6)
            color = (*particle["color"][:3], alpha)
            surf = pygame.Surface((particle["size"]*2, particle["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (particle["size"], particle["size"]), particle["size"])
            screen.blit(surf, (particle["x"], particle["y"]))
        
       
        if death_timer > 0:
            progress = 1 - (death_timer / death_duration)
            current_radius = death_circle_radius * (1 - progress)
            alpha = int(200 * (1 - progress))
            
            circle_surf = pygame.Surface((int(current_radius*2), int(current_radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(
                circle_surf, 
                (255, 255, 255, alpha), 
                (int(current_radius), int(current_radius)), 
                int(current_radius)
            )
            
            screen.blit(
                circle_surf,
                (player_x - scroll_x + player_width//2 - current_radius,
                 player_y + player_height//2 - current_radius)
            )
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()