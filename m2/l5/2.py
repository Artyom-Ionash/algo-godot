import pygame
import sys
from random import randint

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))


def start_screen():
    start = pygame.transform.scale(pygame.image.load("start.png"), (200, 70))
    start_rect = start.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(start, start_rect)

    stop = pygame.transform.scale(pygame.image.load("stop.png"), (200, 70))
    stop_rect = stop.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
    screen.blit(stop, stop_rect)

    return start_rect, stop_rect


start_rect, stop_rect = start_screen()


class GameSprite(pygame.sprite.Sprite):
    def __init__(self, picture: str, x: int, y: int):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(picture), (100, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class Player(GameSprite):
    def __init__(self, picture: str, x: int, y: int, speed: int):
        super().__init__(picture, x, y)
        self.speed = speed
        self.pick_ind = 0
        self.rotation = 0  # 0 - смотрим вправо, 1 - смотрим влево, 2 - бежим вправо, 3 - бежим влево
        self.animation_lose = False

        # Анимации
        self.stay_right = [
            pygame.transform.scale(
                pygame.image.load(f"Images/Warrior/{i}.png"), (100, 120)
            ).convert_alpha()
            for i in range(1, 11)
        ]
        self.stay_left = [
            pygame.transform.flip(img, True, False) for img in self.stay_right
        ]
        self.move_right = [
            pygame.transform.scale(
                pygame.image.load(f"Images/Warrior/{i}.png"), (100, 120)
            ).convert_alpha()
            for i in range(11, 19)
        ]
        self.move_left = [
            pygame.transform.flip(img, True, False) for img in self.move_right
        ]

        self.atk = [
            pygame.transform.scale(
                pygame.image.load(f"Images/Warrior/{i}.png"), (100, 120)
            ).convert_alpha()
            for i in range(41, 48)
        ]
        self.death = [
            pygame.transform.scale(
                pygame.image.load(f"Images/Warrior/{i}.png"), (100, 120)
            ).convert_alpha()
            for i in range(61, 68)
        ]

    def animate(self):
        if self.rotation == 0:
            self.image = self.stay_right[self.pick_ind // 6]
        elif self.rotation == 1:
            self.image = self.stay_left[self.pick_ind // 6]
        elif self.rotation == 2:
            self.image = self.move_right[self.pick_ind // 7]
            self.rect.x += self.speed
        elif self.rotation == 3:
            self.image = self.move_left[self.pick_ind // 7]
            self.rect.x -= self.speed
        elif self.rotation == 4:
            self.image = self.atk[self.pick_ind // 4]
        elif self.rotation == 5:
            self.image = self.death[self.pick_ind // 6]

        if self.rect.x > bg_width - 100:
            self.rotation = 0
        if self.rect.x < 0:
            self.rotation = 1

        if self.rotation == 4:
            self.pick_ind = (self.pick_ind + 1) % 25
        else:
            self.pick_ind = (self.pick_ind + 1) % 55

        if self.rotation == 5 and self.pick_ind == 36:
            self.animation_lose = True

    def update_rotation(self, new_rotation: int):
        if new_rotation != self.rotation:
            self.rotation = new_rotation
            self.pick_ind = 0


class Enemy(GameSprite):
    def update(self):
        if self.rect.x < 7500:
            self.rect.x += 5

    def fire(self):
        bullet = Bullet(
            "Images/Enemy/bullet.png",
            self.rect.left,
            self.rect.centery,
            randint(4, 7),
            40,
            20,
        )
        bullets.add(bullet)


class Bullet(GameSprite):
    def __init__(
        self, picture: str, x: int, y: int, speed: int, width: int, height: int
    ):
        super().__init__(picture, x, y)
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load(picture), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if hero.rotation == 2:
            self.rect.x -= self.speed + hero.speed
        else:
            self.rect.x -= self.speed


# Загрузка ресурсов
bg_menu = pygame.transform.scale(
    pygame.image.load("bg_menu.jpg"), (screen_width, screen_height)
)
bg = pygame.transform.scale(pygame.image.load("bg.jpg"), (8000, screen_height))
bg_width, bg_height = bg.get_size()

# Музыка
menu_music = pygame.mixer.Sound("menu_music.mp3")
menu_music.play(-1)
game_music = pygame.mixer.Sound("game_music.mp3")

hero = Player("Images/Warrior/1.png", 300, 380, 3)
enemy = Enemy("Images/Enemy/enemy.png", 600, 390)
bullets = pygame.sprite.Group()

win = pygame.font.SysFont("Arial", 70).render("ПОБЕДА", True, (0, 255, 0))

camera = pygame.Rect(0, 0, screen_width, screen_height)

pygame.time.set_timer(pygame.USEREVENT, 3000)

# Игровые переменные
main_menu = True
running = True
finish = False
game_start = False

# Главный игровой цикл
while running:
    if not finish:
        if main_menu:
            screen.blit(bg_menu, (0, 0))
            start_rect, stop_rect = start_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if start_rect.collidepoint(x, y):
                        game_start = True
                        main_menu = False
                        menu_music.stop()
                        game_music.play(-1)
                    if stop_rect.collidepoint(x, y):
                        pygame.quit()
                        sys.exit()

        elif game_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    enemy.fire()
                if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                    hero.update_rotation(0)
                elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                    hero.update_rotation(1)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    hero.update_rotation(2)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    hero.update_rotation(3)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    hero.update_rotation(4)

            # Обновление камеры
            camera.x = hero.rect.x - screen_width // 2
            camera.y = hero.rect.y - screen_height // 2
            camera.x = max(0, min(camera.x, bg_width - screen_width))
            camera.y = max(0, min(camera.y, bg_height - screen_height))

            # Отрисовка
            screen.blit(bg, (-camera.x, -camera.y))

            for bullet in bullets:
                screen.blit(
                    bullet.image, (bullet.rect.x - camera.x, bullet.rect.y - camera.y)
                )

            hero.draw()
            hero.animate()
            enemy.draw()
            enemy.update()
            bullets.update()

            if hero.rotation == 4:
                pygame.sprite.spritecollide(hero, bullets, True)
                if pygame.sprite.collide_rect(hero, enemy):
                    screen.blit(win, (400, 300))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    game_start = False
                    main_menu = True
                    hero.animation_lose = False
                    for b in bullets:
                        b.kill()
                    hero.rotation = 0
                    hero.rect.x = 300
                    hero.rect.y = 380
                    enemy.rect.x = 600
                    enemy.rect.y = 390
                    menu_music.play(-1)
                    game_music.stop()

            else:
                if pygame.sprite.spritecollide(hero, bullets, False):
                    hero.update_rotation(5)

            if hero.animation_lose:
                game_start = False
                main_menu = True
                hero.animation_lose = False
                for b in bullets:
                    b.kill()
                hero.rotation = 0
                hero.rect.x = 300
                hero.rect.y = 380
                enemy.rect.x = 600
                enemy.rect.y = 390
                menu_music.play(-1)
                game_music.stop()

    pygame.display.flip()
    pygame.time.delay(20)

pygame.quit()
sys.exit()
