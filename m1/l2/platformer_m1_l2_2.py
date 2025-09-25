import pygame as pg
import sys

pg.init()

# Установка размеров окна
screen_width = 800
screen_height = 600
screen = pg.display.set_mode((screen_width, screen_height))
bg = pg.transform.scale(pg.image.load("bg.jpg"), (screen_width, screen_height))

pg.display.set_caption("Платформер")

# Параметры игрока
y_speed = 0
gravity = 0.5
jump_strength = -10
player_speed = 5

on_ground = True

platforms = [
    (0, screen_height - 10, screen_width, 10),
    (200, 500, 100, 10),
    (400, 400, 150, 10),
    (220, 300, 70, 10),
    (370, 200, 100, 10),
    (490, 100, 100, 10),
]

player = pg.transform.scale(pg.image.load('cat.png'), (70, 70))
player_rect = player.get_rect()
player_rect.x = 100
player_rect.y = 150

pizza = pg.transform.scale(pg.image.load('pizza.png'), (70, 70))
pizza_rect = pizza.get_rect()
pizza_rect.x = 530
pizza_rect.y = 30

win_text = pg.font.SysFont('Arial', 50).render('ММММ, ПИЦЦА', True, (0, 255, 0))

running = True
finish = False
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    if not finish:
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pg.K_RIGHT]:
            player_rect.x += player_speed
        if keys[pg.K_SPACE] and on_ground:
            y_speed = jump_strength
            on_ground = False

        # Обновление вертикальной скорости
        y_speed += gravity
        player_rect.y += y_speed

        # Проверка столкновений с платформами
        on_ground = False
        for platform in platforms:
            platform_rect = pg.Rect(platform)
            # Вертикальные столкновения
            if (player_rect.colliderect(platform_rect) and y_speed > 0 and 
                player_rect.bottom > platform_rect.top):
                player_rect.bottom = platform_rect.top
                y_speed = 0
                on_ground = True

        # Проверка победы (исправлено на colliderect)
        if player_rect.colliderect(pizza_rect):
            finish = True

    # Отрисовка
    screen.blit(bg, (0, 0))
    # Сначала платформы, потом персонажей
    for platform in platforms:
        pg.draw.rect(screen, (0, 100, 200), platform)
    screen.blit(player, player_rect)
    screen.blit(pizza, pizza_rect)

    if finish:
        screen.blit(win_text, (300, 300))

    pg.display.flip()
    pg.time.delay(20)

pg.quit()
sys.exit()
