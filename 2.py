import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survive")

background_menu = pygame.image.load("background_menu.png").convert()
player_images = [pygame.image.load(f"player{i}.png").convert_alpha() for i in range(1, 4)]
enemy_images = [pygame.image.load(f"enemy{i}.png").convert_alpha() for i in range(1, 4)]
bullet_image = pygame.image.load("bullet.png").convert()

heart_image = pygame.image.load("heart.png").convert_alpha()
boss_images = [pygame.image.load(f"boss{i}.png").convert_alpha() for i in range(1, 4)]  # Изображение босса

pygame.mixer.music.load("background_music.mp3")  # Фоновая музыка
damage_sound = pygame.mixer.Sound("damage.mp3")  # Звук получения урона
boss_sound = pygame.mixer.Sound("boss_spawn.mp3")  # Звук появления босса

pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

class Player:
    def __init__(self):
        self.images = player_images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 6
        self.hp = 7

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_alive(self):
        return self.hp > 0

# Класс врага
class Enemy:
    def __init__(self):
        self.images = enemy_images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50)))
        self.speed = random.randint(2, 4)
        self.hp = 2  # Здоровье врага

    def move_towards_player(self, player_rect):
        if self.rect.x < player_rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player_rect.x:
            self.rect.x -= self.speed

        if self.rect.y < player_rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player_rect.y:
            self.rect.y -= self.speed

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Класс босса
class Boss:
    def __init__(self):
        self.images = boss_images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50)))
        self.hp = 50  # Здоровье босса

    def move_towards_player(self, player_rect):
        if self.rect.x < player_rect.x:
            self.rect.x += 2  # Скорость босса
        elif self.rect.x > player_rect.x:
            self.rect.x -= 2

        if self.rect.y < player_rect.y:
            self.rect.y += 2
        elif self.rect.y > player_rect.y:
            self.rect.y -= 2

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Класс пули
class Bullet:
    def __init__(self, x, y, direction):
        self.image = bullet_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.direction = direction



    def move(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)




# меню
def menu():
    font = pygame.font.Font(None, 74)
    play_text = font.render("PLAY", True, (255, 255, 255))
    play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Проверяем нажатие кнопки мыши
                if play_rect.collidepoint(event.pos):
                    game()  # Запускаем игру при нажатии на кнопку PLAY

        # Отображение фона меню
        screen.blit(background_menu, (0, 0))
        screen.blit(play_text, play_rect)
        pygame.display.flip()



def game():
    player = Player()
    enemies = [Enemy() for _ in range(5)]  # Создание начальных врагов
    spawn_timer = 0  # Таймер для спавна врагов
    bullets = []
    killed_enemies = 0  # Счётчик убитых врагов
    start_time = pygame.time.get_ticks()  # Стартовое время игры
    clock = pygame.time.Clock()
    last_bullet_time = pygame.time.get_ticks()  # Время последней пули
    boss = None
    boss_spawned = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Таймер для спавна врагов
        spawn_timer += clock.get_time()
        if spawn_timer >= 10000:  # Каждые 10 секунд
            for _ in range(7):  # Спавн 5 врагов
                enemies.append(Enemy())
            spawn_timer = 0  # Сброс таймера

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]   # Движение  по гор
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]     # Движение по верт

        # цикл карты
        if player.rect.x < 0:
            player.rect.x = WIDTH
        elif player.rect.x > WIDTH:
            player.rect.x = 0
        if player.rect.y < 0:
            player.rect.y = HEIGHT
        elif player.rect.y > HEIGHT:
            player.rect.y = 0

        player.move(dx, dy)
        player.update()

        # Пули
        current_time = pygame.time.get_ticks()
        if current_time - last_bullet_time > 200:  # промежуток атаки
            direction = (1 if dx > 0 else (-1 if dx < 0 else 0), 1 if dy > 0 else (-1 if dy < 0 else 0))
            bullets.append(Bullet(player.rect.centerx, player.rect.centery, direction))
            last_bullet_time = current_time

        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.x < 0 or bullet.rect.x > WIDTH or bullet.rect.y < 0 or bullet.rect.y > HEIGHT:
                bullets.remove(bullet)

        # Обновление врагов и босса
        enemies_to_remove = []
        for enemy in enemies:
            enemy.move_towards_player(player.rect)
            if player.rect.colliderect(enemy.rect):
                player.hp -= 1
                damage_sound.play()
                enemies_to_remove.append(enemy)

            for bullet in bullets[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.hp -= 1
                    bullets.remove(bullet)
                    if enemy.hp <= 0:
                        enemies_to_remove.append(enemy)

        # Удаление врагов
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)
                killed_enemies += 1
                if killed_enemies % 5 == 0 and not boss_spawned:
                    boss = Boss()
                    boss_spawned = True
                    boss_sound.play()

        if boss_spawned:
            boss.move_towards_player(player.rect)
            if player.rect.colliderect(boss.rect):
                player.hp -= 1
                damage_sound.play()

            for bullet in bullets[:]:
                if bullet.rect.colliderect(boss.rect):
                    boss.hp -= 1
                    bullets.remove(bullet)
                    if boss.hp <= 0:
                        boss_spawned = False
                        player.hp += 1  # Игрок получает 1 hp


        # Проверка на окончание игры
        if not player.is_alive():
            pygame.quit()
            sys.exit()  # Закрытие окна, если здоровье кончилось




        screen.fill((255, 255, 255))
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        if boss_spawned:
            boss.draw(screen)

        # Отображение здоровья игрока
        for i in range(player.hp):
            screen.blit(heart_image, (WIDTH - 50 * (i + 1), HEIGHT - 50))

        # Отображение счётчика убитых врагов
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Killed: {killed_enemies}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Отображение таймера
        elapsed_time = (current_time - start_time) // 1000  # Время в секундах
        timer_text = font.render(f"Time: {elapsed_time}s", True, (0, 0, 0))
        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(timer_text, timer_rect)

        pygame.display.flip()
        clock.tick(60)


menu()



