import pgzrun
from plataformer import *
from plataformer import Sprite

# ============================
# CONSTANTES DO JOGO
# ============================

TILE_SIZE = 21
ROWS = 30
COLS = 20
WIDTH = TILE_SIZE * ROWS
HEIGHT = TILE_SIZE * COLS
TITLE = "UFO Jumper"

# ============================
# CONTROLE DE SOM
# ============================

sound_enabled = True

# ============================
# CRIAÇÃO DO PLAYER
# ============================

player = Actor('idle')
player.bottomleft = (0, HEIGHT - TILE_SIZE)
player.velocity_x = 3
player.velocity_y = 0
player.jumping = 2
player.alive = True
player.state = "idle"  # idle, walk_right
player.anim_timer = 0

# ============================
# FRAMES DE ANIMAÇÃO DO PLAYER
# ============================

idle_frames = ['idle', 'dance']
walk_right_frames = ['walk_right', 'walk_right1']

# ============================
# FUNÇÃO PARA CRIAR INIMIGO PATRULHA
# ============================

def create_enemy(x, y):
    enemy = Actor('bat')
    enemy.x = x
    enemy.y = y
    enemy.direction = 1
    enemy.velocity_x = 2
    enemy.anim_timer = 0
    enemy.frames_right = ['bat', 'bat1']
    return enemy

# ============================
# VARIÁVEIS DE ESTADO
# ============================

game_started = False
over = False
win = False

# ============================
# CRIAÇÃO DOS MAPAS
# ============================

platforms = build("map_floor.csv", TILE_SIZE)
spikes = build("map_spikes.csv", TILE_SIZE)
flags = build("map_winflag.csv", TILE_SIZE)

# ============================
# CRIAÇÃO DOS INIMIGOS
# ============================

enemies = [
    create_enemy(WIDTH // 2, HEIGHT - TILE_SIZE * 3),
    create_enemy(WIDTH // 3, HEIGHT - TILE_SIZE * 5),
    create_enemy(WIDTH // 1.5, HEIGHT - TILE_SIZE * 7)
]

# ============================
# FUNÇÃO PARA TOCAR MÚSICA
# ============================

def play_music():
    if sound_enabled:
        music.play('music')  # type: ignore
        music.set_volume(0.5)  # type: ignore
    else:
        music.stop()  # type: ignore

play_music()

# ============================
# FUNÇÃO DRAW
# ============================

def draw():
    screen.clear()
    if not game_started:
        draw_menu()
    else:
        screen.fill('black')
        draw_game_elements()

def draw_menu():
    """Desenha o menu inicial."""
    screen.fill('black')
    screen.draw.text("UFO Jumper", center=(WIDTH/2, HEIGHT/3), fontsize=80, color="white")
    screen.draw.text("Pressione [ENTER] para Iniciar", center=(WIDTH/2, HEIGHT/2), fontsize=40, color="white")
    screen.draw.text("Pressione [M] para Mutar/Desmutar Som", center=(WIDTH/2, HEIGHT/2 + 60), fontsize=30, color="white")
    screen.draw.text("Pressione [ESC] para Sair", center=(WIDTH/2, HEIGHT/2 + 110), fontsize=30, color="white")
    screen.draw.text("Use as setas laterais para se mover, use o SPACE 2x para o pulo duplo, capture a bandeira", center=(WIDTH/2, HEIGHT/2 + 150), fontsize=20, color="white")

def draw_game_elements():
    """Desenha todos os elementos do jogo."""
    for platform in platforms:
        platform.draw()
    for spike in spikes:
        spike.draw()
    for flag in flags:
        flag.draw()
    for enemy in enemies:
        enemy.draw()
    if player.alive:
        player.draw()
    if over:
        screen.draw.text("Game Over!", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="white")
    if win:
        screen.draw.text("You Win!", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="white")

# ============================
# FUNÇÃO UPDATE
# ============================

def update():
    global over, win, game_started

    if not game_started:
        return

    animate_player()
    handle_player_movement()
    handle_player_jump()
    handle_enemy_patrol()
    handle_collisions()

# ============================
# ANIMAÇÃO DO PLAYER
# ============================

def animate_player():
    """Gerencia a animação do personagem."""
    player.anim_timer += 1
    if player.state == "idle":
        frame_index = (player.anim_timer // 10) % len(idle_frames)
        player.image = idle_frames[frame_index]
    elif player.state in ["walk_left", "walk_right"]:
        frame_index = (player.anim_timer // 6) % len(walk_right_frames)
        player.image = walk_right_frames[frame_index]

# ============================
# MOVIMENTO DO PLAYER
# ============================

def handle_player_movement():
    """Gerencia o movimento horizontal do personagem."""
    if keyboard.LEFT and player.left > 0:
        player.flip_x = True
        player.x -= player.velocity_x
        player.state = "walk_right"
        fix_collision_horizontal(-1)
    elif keyboard.RIGHT and player.right < WIDTH:
        player.flip_x = False
        player.x += player.velocity_x
        player.state = "walk_right"
        fix_collision_horizontal(1)
    else:
        player.state = "idle"

def fix_collision_horizontal(direction):
    """Corrige a colisão horizontal com plataformas."""
    index = player.collidelist(platforms)
    if index != -1:
        obj = platforms[index]
        if direction == -1:
            player.x = obj.x + (obj.width / 2 + player.width / 2)
        else:
            player.x = obj.x - (obj.width / 2 + player.width / 2)

# ============================
# PULO DO PLAYER
# ============================

def handle_player_jump():
    """Aplica gravidade e gerencia colisão vertical."""
    player.y += player.velocity_y
    player.velocity_y += 1

    index = player.collidelist(platforms)
    if index != -1:
        obj = platforms[index]
        if player.velocity_y >= 0:
            player.y = obj.y - (obj.height / 2 + player.height / 2)
            player.jumping = 2
        else:
            player.y = obj.y + (obj.height / 2 + player.height / 2)
        player.velocity_y = 0

# ============================
# PATRULHA DOS INIMIGOS
# ============================

def handle_enemy_patrol():
    """Controla a movimentação e animação dos inimigos."""
    for enemy in enemies:
        enemy.x += enemy.velocity_x * enemy.direction
        if enemy.left <= 0 or enemy.right >= WIDTH:
            enemy.direction *= -1

        enemy.anim_timer += 1
        frames = enemy.frames_right
        frame_index = (enemy.anim_timer // 8) % len(frames)
        enemy.image = frames[frame_index]

# ============================
# CHECAGEM DE COLISÕES
# ============================

def handle_collisions():
    """Verifica colisões e aplica as consequências."""
    global over, win

    # Colisão com inimigos
    for enemy in enemies:
        if player.colliderect(enemy):
            player_die()

    # Colisão com espinhos
    if player.collidelist(spikes) != -1:
        player_die()

    # Colisão com a bandeira (fim do nível)
    for flag in flags:
        if player.colliderect(flag):
            player_win(flag)

def player_die():
    """Mata o personagem e finaliza o jogo."""
    global over
    player.alive = False
    over = True
    music.stop()
    if sound_enabled:
        sounds.gameover.play()

def player_win(flag):
    """Vitória do jogador."""
    global win
    player.alive = False
    win = True
    music.stop()
    if sound_enabled:
        sounds.gamewin.play()
    flags.remove(flag)

# ============================
# ENTRADAS DE TECLADO
# ============================

def on_key_down(key):
    global game_started, sound_enabled

    if not game_started:
        if key == keys.RETURN:
            game_started = True
            play_music()
        elif key == keys.M:
            sound_enabled = not sound_enabled
            if sound_enabled:
                play_music()
            else:
                music.stop()
        elif key == keys.ESCAPE:
            exit()
    else:
        if key == keys.SPACE and player.jumping > 0:
            if sound_enabled:
                sounds.jump.play()
            player.velocity_y = -10
            player.jumping -= 1

# ============================
# EXECUTA O JOGO
# ============================

pgzrun.go()


# pula no SPACE, move-se nas setas <- ->