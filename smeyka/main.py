import pygame
import random
import sys
import os

# Настройка прозрачности для Windows
if os.name == 'nt':
    import win32api
    import win32con
    import win32gui

pygame.init()

# Получаем разрешение монитора
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

BLOCK_SIZE = 40  
FPS = 10         # Чуть увеличим скорость для плавности полета окон

# Настройка прозрачного полноэкранного окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

if os.name == 'nt':
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# Цвета
COLOR_CLEAR = (0, 0, 0)            
COLOR_WIN_BG = (240, 240, 240)      
COLOR_WIN_HEADER = (0, 120, 215)   
COLOR_SNAKE_HEADER = (230, 80, 0)  
COLOR_APPLE_HEADER = (200, 30, 30) 
COLOR_WALL_HEADER = (40, 40, 40)   
COLOR_TEXT = (255, 255, 255)       
COLOR_ERROR_BG = (255, 220, 220)   # Красный оттенок для окон ошибок

font = pygame.font.SysFont("semibold", 14)
score_font = pygame.font.SysFont("arial", 28)
error_font = pygame.font.SysFont("courier", 16, bold=True)

def draw_fake_window(x, y, w, h, header_color, title_text, is_glitch=False):
    """Рисует имитацию системного окна Windows."""
    bg = COLOR_ERROR_BG if is_glitch else COLOR_WIN_BG
    pygame.draw.rect(screen, bg, (x, y, w, h))
    pygame.draw.rect(screen, header_color, (x, y, w, 18))
    pygame.draw.rect(screen, (160, 160, 160), (x, y, w, h), 1)
    
    # Кнопки управления окном
    pygame.draw.rect(screen, (255, 255, 255), (x + w - 14, y + 4, 10, 2))
    pygame.draw.rect(screen, (255, 255, 255), (x + w - 28, y + 4, 8, 8), 1)
    text_close = font.render("X", True, COLOR_TEXT)
    screen.blit(text_close, (x + w - 14, y + 2))
    
    text_surface = font.render(title_text, True, COLOR_TEXT)
    screen.blit(text_surface, (x + 5, y + 1))

def draw_missing_texture_corner(start_x, start_y, width, height):
    """Рисует черно-фиолетовую шахматную сетку 'Нет текстуры'."""
    tile_size = 20
    for x in range(start_x, start_x + width, tile_size):
        for y in range(start_y, start_y + height, tile_size):
            color = (0, 0, 0) if ((x // tile_size) + (y // tile_size)) % 2 == 0 else (255, 0, 255)
            pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))

def spawn_one_food(snake_body, walls, current_foods):
    """Генерирует яблоко, избегая змейки и неподвижных стен."""
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE
    while True:
        x = random.randint(3, cols - 4) * BLOCK_SIZE
        y = random.randint(3, rows - 4) * BLOCK_SIZE
        pos = [x, y]
        if pos not in snake_body and pos not in walls and pos not in current_foods:
            return pos

def generate_walls(snake_body, count=6):
    """Генерирует твердые синие стены (при столкновении — смерть)."""
    walls = []
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE
    head = snake_body[0]
    while len(walls) < count:
        x = random.randint(3, cols - 4) * BLOCK_SIZE
        y = random.randint(3, rows - 4) * BLOCK_SIZE
        pos = [x, y]
        if pos not in snake_body and abs(pos[0] - head[0]) > BLOCK_SIZE * 3 and abs(pos[1] - head[1]) > BLOCK_SIZE * 3:
            walls.append(pos)
    return walls

def generate_glitches(count=2):
    """Генерирует структуру для летающих окон ошибок [x, y, w, h, speed_x, speed_y]."""
    glitches = []
    for _ in range(count):
        w = random.randint(180, 260)
        h = random.randint(110, 140)
        x = random.randint(200, SCREEN_WIDTH - 300)
        y = random.randint(200, SCREEN_HEIGHT - 200)
        # Случайное направление и скорость движения окон
        speed_x = random.choice([-8, -5, 5, 8])
        speed_y = random.choice([-8, -5, 5, 8])
        glitches.append([x, y, w, h, speed_x, speed_y])
    return glitches

def game_loop():
    clock = pygame.time.Clock()
    
    start_x = (SCREEN_WIDTH // (2 * BLOCK_SIZE)) * BLOCK_SIZE
    start_y = (SCREEN_HEIGHT // (2 * BLOCK_SIZE)) * BLOCK_SIZE
    snake_body = [[start_x, start_y], [start_x - BLOCK_SIZE, start_y], [start_x - BLOCK_SIZE * 2, start_y]]
    
    direction = 'RIGHT'
    change_to = direction

    walls = generate_walls(snake_body, count=5)
    glitches = generate_glitches(count=3)  # Начинаем с 3 летающих окон
    
    foods = []
    apples_eaten = 0
    score = 0
    
    foods.append(spawn_one_food(snake_body, walls, foods))
    corner_w, corner_h = 120, 120

    while True:
        required_food_count = 1 + (apples_eaten // 5)
        while len(foods) < required_food_count:
            foods.append(spawn_one_food(snake_body, walls, foods))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP: change_to = 'UP'
                elif event.key == pygame.K_DOWN: change_to = 'DOWN'
                elif event.key == pygame.K_LEFT: change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT: change_to = 'RIGHT'

        if change_to == 'UP' and direction != 'DOWN': direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP': direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT': direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT': direction = 'RIGHT'

        # Движение змейки
        head_x, head_y = snake_body[0]
        if direction == 'UP': head_y -= BLOCK_SIZE
        elif direction == 'DOWN': head_y += BLOCK_SIZE
        elif direction == 'LEFT': head_x -= BLOCK_SIZE
        elif direction == 'RIGHT': head_x += BLOCK_SIZE

        new_head = [head_x, head_y]

        # --- ОБНОВЛЕНИЕ ПОЗИЦИЙ ЛЕТАЮЩИХ ОКОН ---
        for glitch in glitches:
            glitch[0] += glitch[4]  # Движение по X
            glitch[1] += glitch[5]  # Движение по Y

            # Отскок от левой и правой границ экрана
            if glitch[0] <= 0 or glitch[0] + glitch[2] >= SCREEN_WIDTH:
                glitch[4] = -glitch[4]
            # Отскок от верхней и нижней границ экрана
            if glitch[1] <= 0 or glitch[1] + glitch[3] >= SCREEN_HEIGHT:
                glitch[5] = -glitch[5]

        # --- Проверка поражения ---
        collision = (head_x < 0 or head_x >= SCREEN_WIDTH or 
                     head_y < 0 or head_y >= SCREEN_HEIGHT or 
                     new_head in snake_body or 
                     new_head in walls)
        
        in_corner = (
            (head_x < corner_w and head_y < corner_h) or 
            (head_x >= SCREEN_WIDTH - corner_w and head_y < corner_h) or 
            (head_x < corner_w and head_y >= SCREEN_HEIGHT - corner_h) or 
            (head_x >= SCREEN_WIDTH - corner_w and head_y >= SCREEN_HEIGHT - corner_h)
        )

        # Условие врезания в окно ошибки ТЕПЕРЬ УБРАНО! Окна просто пролетают сквозь змейку.

        if collision or in_corner:
            break

        snake_body.insert(0, new_head)

        # --- Поедание яблока ---
        food_eaten_index = -1
        for i, food_pos in enumerate(foods):
            if head_x == food_pos[0] and head_y == food_pos[1]:
                food_eaten_index = i
                break

        if food_eaten_index != -1:
            score += 10
            apples_eaten += 1
            foods.pop(food_eaten_index)
            
            # Деспавн старых и спавн новых ТВЕРДЫХ стен
            walls = generate_walls(snake_body, count=5 + (apples_eaten // 4))
            
            # Рандомный переспавн ЛЕТАЮЩИХ окон ошибок + увеличение их количества
            glitches = generate_glitches(count=3 + (apples_eaten // 2))
        else:
            snake_body.pop()

        # --- ОТРИСОВКА ---
        screen.fill(COLOR_CLEAR) 

        # 1. Задний план: Углы «Нет текстуры»
        draw_missing_texture_corner(0, 0, corner_w, corner_h)
        draw_missing_texture_corner(SCREEN_WIDTH - corner_w, 0, corner_w, corner_h)
        draw_missing_texture_corner(0, SCREEN_HEIGHT - corner_h, corner_w, corner_h)
        draw_missing_texture_corner(SCREEN_WIDTH - corner_w, SCREEN_HEIGHT - corner_h, corner_w, corner_h)

        # 2. Неподвижные окна-стены (опасные)
        for wall in walls:
            draw_fake_window(wall[0], wall[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2, COLOR_WALL_HEADER, "Отказ")

        # 3. Окна-яблоки
        for food in foods:
            draw_fake_window(food[0], food[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2, COLOR_APPLE_HEADER, "Apple.exe")

        # 4. Змейка
        for index, block in enumerate(snake_body):
            if index == 0:
                draw_fake_window(block[0], block[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2, COLOR_SNAKE_HEADER, "cmd.exe")
            else:
                draw_fake_window(block[0], block[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2, COLOR_WIN_HEADER, "Folder")

        # 5. НАВЕРХУ ВСЕХ ИКОНОК: Отрисовываем летающие ошибки поверх змейки и яблок!
        for glitch in glitches:
            gx, gy, gw, gh, _, _ = glitch
            draw_fake_window(gx, gy, gw, gh, (220, 0, 0), "WARNING: SYSTEM INFECTED", is_glitch=True)
            err_txt = error_font.render("ERROR_OVERFLOW", True, (200, 0, 0))
            err_txt2 = font.render("Окно перекрывает интерфейс.", True, (0, 0, 0))
            screen.blit(err_txt, (gx + 15, gy + 40))
            screen.blit(err_txt2, (gx + 15, gy + 70))

        # Виджет счета (в самом низу)
        pygame.draw.rect(screen, (0, 0, 0), (20, SCREEN_HEIGHT - 60, 520, 40))
        # Виджет счета (в самом низу)
        pygame.draw.rect(screen, (0, 0, 0), (20, SCREEN_HEIGHT - 60, 520, 40))
        text_score = score_font.render(f"Яблоки: {apples_eaten} | Очки: {score} | Окон на экране: {len(glitches)}", True, (0, 255, 255))
        screen.blit(text_score, (30, SCREEN_HEIGHT - 58))

        pygame.display.flip()
        clock.tick(FPS)

    # Вызываем экран смерти после выхода из основного цикла
    show_game_over_screen(score)


def show_game_over_screen(score):
    """BSOD Экран смерти с правильными отступами."""
    while True:
        screen.fill((0, 90, 200)) 
        font_big = pygame.font.SysFont("arial", 40, bold=True)
        txt1 = font_big.render(":( Сбой ядра Glitch_Snake.sys", True, (255, 255, 255))
        txt2 = score_font.render(f"Поток уничтожен. Ваш результат: {score}.", True, (255, 255, 255))
        txt3 = font.render("Нажмите ПРОБЕЛ для перезагрузки или ESC для выхода.", True, (240, 240, 240))
        
        screen.blit(txt1, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3))
        screen.blit(txt2, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 60))
        screen.blit(txt3, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 120))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_loop()  # Перезапуск игры
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# Исправленная точка входа в программу
if __name__ == "__main__":
    game_loop()
