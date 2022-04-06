import pygame
import time
import math
pygame.font.init()

def image_scale(img, multiply):
    size = round(img.get_width() * multiply), round(img.get_height() * multiply)
    return pygame.transform.scale(img, size)

def blit_rotate_canter(window, image, top_left, position):
    rotated_image = pygame.transform.rotate(image, position)
    new_rectangle = rotated_image.get_rect(center = image.get_rect(topleft = top_left).center)
    window.blit(rotated_image, new_rectangle.topleft)

def blit_text_center(window, font, text):
    render = font.render(text, 1, (26, 23, 23))
    window.blit(render, (window.get_width()/2 - render.get_width()/2, window.get_height()/2 - render.get_height()/2))

GRASS = image_scale(pygame.image.load("Images/grass.jpg"), 2.5)
TRACK = image_scale(pygame.image.load("Images/track.png"), 0.9)
TRACK_BORDER = image_scale(pygame.image.load("Images/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH_LINE = image_scale(pygame.image.load("Images/finish-line.png"), 0.8)
FINISH_LINE_POSITION = (700, 535)
FINISH_LINE_MASK = pygame.mask.from_surface(FINISH_LINE)

GRENN_CAR = image_scale(pygame.image.load("Images/green-car.png"), 0.4)
GREY_CAR = image_scale(pygame.image.load("Images/grey-car.png"), 0.4)
RED_CAR = image_scale(pygame.image.load("Images/red-car.png"), 0.4)

WITH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WITH, HEIGHT))
pygame.display.set_caption("Racing Car Game")

MAIN_FONT = pygame.font.Font("RobotoMono-SemiBold.ttf", 40)

FPS = 60

PATH = [(728, 377), (393, 345), (478, 255), (739, 222), (723, 83),
        (291, 75), (266, 417), (164, 328), (167, 96), (52, 100),
        (75, 501), (338, 744), (412, 631), (442, 469), (610, 556),
        (634, 734), (750, 678), (748, 543)]

class GameInfo:
    LEVELS = 5

    def __init__(self, level = 1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return self.level_start_time - time.time()

class AbstractCar:

    def __init__(self, max_speed, rotation_speed):
        self.img = self.IMG
        self.max_speed = max_speed
        self.rotation_speed = rotation_speed
        self.speed = 0
        self.position = 0
        self.x, self.y = self.START_POSITION
        self.speeding = 0.1

    def rotation(self, left = False, right = False):
        if left:
            self.position += self.rotation_speed
        elif right:
            self.position -= self.rotation_speed

    def draw(self, window):
        blit_rotate_canter(window, self.img, (self.x, self.y), self.position)

    def move_forward(self):
        self.speed = min(self.speed + self.speeding, self.max_speed)
        self.move()

    def move_backward(self):
        self.speed = max(self.speed - self.speeding, -self.max_speed)
        self.move()

    def move(self):
        radians = math.radians(self.position)
        vertical = math.cos(radians) * self.speed
        horizontal = math.sin(radians) * self.speed

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x = 0, y = 0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self,):
        self.x, self.y = self.START_POSITION
        self.speed = 0
        self.position = 0

class PlayerCar(AbstractCar):
    IMG = GREY_CAR
    START_POSITION = (755, 500)

    def reduce_speed_forward(self):
        self.speed = max(self.speed - self.speeding / 2, 0)
        self.move()

    def reduce_speed_backward(self):
        self.speed = min(self.speed + self.speeding / 2, 0)
        self.move()

    def bounce(self):
        self.speed = -self.speed/2
        self.move()

class ComputerCar(AbstractCar):
    IMG = RED_CAR
    START_POSITION = (715, 500)

    def __init__(self, max_speed, rotation_speed):
        super().__init__(max_speed, rotation_speed)
        self.current_point = 0

    def reduce_speed_forward(self):
        self.speed = max(self.speed - self.speeding / 2, 0)
        self.move()

    def reduce_speed_backward(self):
        self.speed = min(self.speed + self.speeding / 2, 0)
        self.move()

    def bounce(self):
        self.speed = -self.speed/2
        self.move()


run = True
clock = pygame.time.Clock()
player_car = PlayerCar(5, 5)
computer_car = ComputerCar(5, 5)
game_info = GameInfo()

while run:
    clock.tick(FPS)

    WIN.blit(GRASS, (0, 0))
    WIN.blit(TRACK, (0, 0))
    WIN.blit(FINISH_LINE, (FINISH_LINE_POSITION))
    WIN.blit(TRACK_BORDER, (0, 0))
    player_car.draw(WIN)
    computer_car.draw(WIN)

    pygame.display.update()

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()
            computer_car.path.append(position)

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_car.rotation(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotation(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()

    if not moved:
        if player_car.speed > 0:
            player_car.reduce_speed_forward()
        elif player_car.speed < 0:
            player_car.reduce_speed_backward()


    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    #second player
    if keys[pygame.K_a]:
        computer_car.rotation(left=True)
    if keys[pygame.K_d]:
        computer_car.rotation(right=True)
    if keys[pygame.K_w]:
        moved = True
        computer_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        computer_car.move_backward()

    if not moved:
        if computer_car.speed > 0:
            computer_car.reduce_speed_forward()
        elif computer_car.speed < 0:
            computer_car.reduce_speed_backward()

    if computer_car.collide(TRACK_BORDER_MASK) != None:
        computer_car.bounce()

    if player_car.collide(FINISH_LINE_MASK, *FINISH_LINE_POSITION) != None:
        if player_car.speed < 0:
            player_car.bounce()
        else:
            player_car.reset()
            computer_car.reset()

    if computer_car.collide(FINISH_LINE_MASK, *FINISH_LINE_POSITION) != None:
        player_car.reset()
        computer_car.reset()
        computer_car.path.clear()


pygame.quit()
