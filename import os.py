import os
import random
import pygame

# ---------- 1. INITIALIZATION ----------
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge & Collect")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 210, 0)
RED = (220, 40, 40)
BACKGROUND = (25, 130, 60)

# ---------- 2. LOAD SPRITE SHEET ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_CANDIDATES = [
    os.path.join(BASE_DIR, "guy.png"),
    os.path.join(BASE_DIR, "assets", "guy.png"),
    os.path.join(BASE_DIR, "Deco_skeleto_sitdown.PNG"),
    os.path.join(BASE_DIR, "assets", "Deco_skeleto_sitdown.PNG"),
]

SPRITESHEET = None
for path in SPRITE_CANDIDATES:
    if os.path.exists(path):
        SPRITESHEET = pygame.image.load(path).convert_alpha()
        break

FRAME_W, FRAME_H = 16, 24
SCALE = 3
DISPLAY_W, DISPLAY_H = FRAME_W * SCALE, FRAME_H * SCALE

DIRECTION_ROWS = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3,
}
FRAMES_PER_ROW = 4

def get_frame(direction, frame_index):
    """Cut out one frame from the spritesheet and scale it up."""
    row = DIRECTION_ROWS[direction]
    col = frame_index % FRAMES_PER_ROW
    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
    frame = SPRITESHEET.subsurface(rect).copy()
    frame = pygame.transform.scale(frame, (DISPLAY_W, DISPLAY_H))
    return frame

if SPRITESHEET is not None:
    ANIMATIONS = {
        direction: [get_frame(direction, i) for i in range(FRAMES_PER_ROW)]
        for direction in DIRECTION_ROWS
    }
else:
    ANIMATIONS = {
        "down": [pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA) for _ in range(FRAMES_PER_ROW)],
        "left": [pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA) for _ in range(FRAMES_PER_ROW)],
        "right": [pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA) for _ in range(FRAMES_PER_ROW)],
        "up": [pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA) for _ in range(FRAMES_PER_ROW)],
    }
    for direction in ANIMATIONS:
        for i in range(FRAMES_PER_ROW):
            surface = ANIMATIONS[direction][i]
            pygame.draw.rect(surface, (0, 200, 120), (0, 0, DISPLAY_W, DISPLAY_H))
            pygame.draw.rect(surface, (20, 40, 80), (DISPLAY_W // 4, DISPLAY_H // 4, DISPLAY_W // 2, DISPLAY_H // 2))
            pygame.draw.circle(surface, (255, 255, 255), (DISPLAY_W // 2, DISPLAY_H // 4), DISPLAY_W // 6)

# ---------- 3. LOAD MUSIC ----------
MUSIC_CANDIDATES = [
    os.path.join(BASE_DIR, "Juhani Junkala [Retro Game Music Pack] Level 2.wav"),
    os.path.join(BASE_DIR, "assets", "Juhani Junkala [Retro Game Music Pack] Level 2.wav"),
    os.path.join(BASE_DIR, "battleThemeA.mp3"),
    os.path.join(BASE_DIR, "assets", "battleThemeA.mp3"),
]

MUSIC_PATH = next((path for path in MUSIC_CANDIDATES if os.path.exists(path)), None)
if MUSIC_PATH:
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# ---------- 4. PLAYER STATE ----------
player_x = WIDTH // 2 - DISPLAY_W // 2
player_y = HEIGHT // 2 - DISPLAY_H // 2
player_speed = 4

facing = "down"
anim_frame = 0
anim_timer = 0
ANIM_SPEED = 8

# ---------- 5. FALLING OBJECTS ----------
OBJECT_SIZE = 26
fall_speed = 4

def make_object():
    """Randomly create either a gem (collect) or a spike (dodge)."""
    kind = random.choice(["gem", "gem", "spike"])
    x = random.randint(0, WIDTH - OBJECT_SIZE)
    return {"kind": kind, "x": x, "y": -OBJECT_SIZE}

falling_objects = [make_object()]
spawn_timer = 0
SPAWN_INTERVAL = 45

score = 0
game_over = False

def draw_text(text, font_size, color, pos):
    font = pygame.font.SysFont(None, font_size)
    render = font.render(text, True, color)
    rect = render.get_rect(center=pos)
    screen.blit(render, rect)

def reset_game():
    global player_x, player_y, falling_objects, score, game_over, fall_speed, spawn_timer
    player_x = WIDTH // 2 - DISPLAY_W // 2
    player_y = HEIGHT // 2 - DISPLAY_H // 2
    falling_objects = [make_object()]
    score = 0
    fall_speed = 4
    spawn_timer = 0
    game_over = False

# ---------- 6. GAME LOOP ----------
running = True
while running:
    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    if not game_over:
        # --- Movement & direction/animation ---
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT]:
            player_x -= player_speed
            facing = "left"
            moving = True
        elif keys[pygame.K_RIGHT]:
            player_x += player_speed
            facing = "right"
            moving = True
        elif keys[pygame.K_UP]:
            player_y -= player_speed
            facing = "up"
            moving = True
        elif keys[pygame.K_DOWN]:
            player_y += player_speed
            facing = "down"
            moving = True

        # keep player inside the screen
        player_x = max(0, min(WIDTH - DISPLAY_W, player_x))
        player_y = max(0, min(HEIGHT - DISPLAY_H, player_y))

        # advance walking animation only while moving
        if moving:
            anim_timer += 1
            if anim_timer >= ANIM_SPEED:
                anim_timer = 0
                anim_frame = (anim_frame + 1) % FRAMES_PER_ROW
        else:
            anim_frame = 0
            anim_timer = 0

        # --- Spawn new falling objects over time ---
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            falling_objects.append(make_object())

        # --- Update falling objects ---
        player_rect = pygame.Rect(player_x, player_y, DISPLAY_W, DISPLAY_H)

        for obj in falling_objects[:]:
            obj["y"] += fall_speed
            obj_rect = pygame.Rect(obj["x"], obj["y"], OBJECT_SIZE, OBJECT_SIZE)

            if player_rect.colliderect(obj_rect):
                if obj["kind"] == "gem":
                    score += 1
                    fall_speed = min(12, 4 + score // 5)
                    falling_objects.remove(obj)
                else:
                    game_over = True
            elif obj["y"] > HEIGHT:
                falling_objects.remove(obj)

    # ---------- 7. DRAW ----------
    screen.fill(BACKGROUND)

    if not game_over:
        # Draw falling objects
        for obj in falling_objects:
            if obj["kind"] == "gem":
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (obj["x"] + OBJECT_SIZE // 2, obj["y"] + OBJECT_SIZE // 2),
                    OBJECT_SIZE // 2,
                )
            else:
                pygame.draw.polygon(
                    screen,
                    RED,
                    [
                        (obj["x"] + OBJECT_SIZE // 2, obj["y"]),
                        (obj["x"], obj["y"] + OBJECT_SIZE),
                        (obj["x"] + OBJECT_SIZE, obj["y"] + OBJECT_SIZE),
                    ],
                )

        # Draw player using the correct direction + animation frame
        current_sprite = ANIMATIONS[facing][anim_frame]
        screen.blit(current_sprite, (player_x, player_y))

        draw_text(f"Score: {score}", 36, WHITE, (90, 30))
    else:
        draw_text("GAME OVER", 64, RED, (WIDTH // 2, HEIGHT // 2 - 40))
        draw_text(f"Final score: {score}", 40, WHITE, (WIDTH // 2, HEIGHT // 2 + 20))
        draw_text("Press R to play again", 28, WHITE, (WIDTH // 2, HEIGHT // 2 + 70))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()