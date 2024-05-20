import random
import numpy as np
import turtle
import pygame
import threading as tr
import time
from pynput import keyboard
import math


class Pen2:
    def __init__(
        self,
        display_size=1200,
        square_length=10,
        circle_diameter=10,
        snake_color=(255, 0, 0),
        food_color=(255, 0, 255),
    ) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((display_size, display_size))
        self.screen.fill((20, 20, 20))
        self.sq_l = square_length
        self.c_d = circle_diameter
        self.snake_color = snake_color
        self.food_color = food_color

        # pygame.display.set_caption("Shape Drawer")

        # while running := True:
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             running = False
        #         elif event.type == pygame.KEYDOWN:
        #             if event.key == pygame.K_SPACE:
        #                 self.draw_square(600, 600)

        #     pygame.display.flip()
        #     self.clock.tick(60)

    def draw_square(self, x, y):
        half_side = self.sq_l // 2
        top_left = (x - half_side, y - half_side)
        rect = pygame.Rect(top_left, (self.sq_l, self.sq_l))
        pygame.draw.rect(self.screen, color=self.snake_color, rect=rect)

    def draw_sanke(self, array):
        for row in array:
            x, y = row
            self.draw_square(x, y)

    def draw_circle(self, center):
        pygame.draw.circle(
            self.screen, color=self.food_color, center=center, radius=self.c_d // 2
        )

    def draw_triangle(self, x, y, direction):
        match direction:
            case 0:
                angle_rad = math.radians(0)
            case 1:
                angle_rad = math.radians(-90)
            case 2:
                angle_rad = math.radians(180)
            case 3:
                angle_rad = math.radians(-270)

        x1 = x + self.sq_l / 1.8 * math.cos(angle_rad)
        y1 = y - self.sq_l / 1.8 * math.sin(angle_rad)
        x2 = x + self.sq_l / 1.8 * math.cos(angle_rad - (2 * math.pi / 3))
        y2 = y - self.sq_l / 1.8 * math.sin(angle_rad - (2 * math.pi / 3))
        x3 = x + self.sq_l / 1.8 * math.cos(angle_rad - (4 * math.pi / 3))
        y3 = y - self.sq_l / 1.8 * math.sin(angle_rad - (4 * math.pi / 3))
        pygame.draw.polygon(
            self.screen, self.snake_color, [(x1, y1), (x2, y2), (x3, y3)]
        )


class Pen(turtle.Turtle):
    def __init__(
        self, shape: str = "classic", undobuffersize: int = 1000, visible: bool = True
    ) -> None:
        super().__init__(shape, undobuffersize, visible)
        self.speed(0)
        self.hideturtle()

    def square(self, x, y):
        self.penup()
        self.goto(x, y)
        self.pendown()
        self.begin_fill()
        for _ in range(4):
            self.forward(length)
            self.right(90)
        self.end_fill()
        self.penup

    def draw_snake(self, array):
        for row in array:
            x, y = row
            self.square(x, y)


class SnakeGame:
    def __init__(self, visualization=True) -> None:
        self.dpl = 400
        self.sql = 20
        self.ts = 0.1

        self.visualization = visualization
        self.init_visulization()
        self.start_key_listener()

        self.continous_run()

    def continous_run(self):
        while True:
            self.bk = tr.Thread(target=self.restart_game)
            self.bk.daemon = False
            self.bk.start()
            self.bk.join()

    def restart_game(self):
        self.head_x, self.head_y = random.randint(0, self.dpl), random.randint(
            0, self.dpl
        )
        self.body_pos = np.array([self.head_x, self.head_y]).reshape(-1, 2)
        self.head_direction = random.randint(0, 3)

        self.put_food()
        self.speed = 1

        self.game_running = True

        while self.game_running:
            self.update_position()
            self.update_visulization()
            time.sleep(self.ts)

        return 0

    def init_visulization(self):
        if not self.visualization:
            return 0
        self.vis = Pen2(
            display_size=self.dpl, square_length=self.sql, circle_diameter=self.sql
        )

    def finish_visulization(self):
        if not self.visualization:
            return 0
        pygame.quit()

    def update_visulization(self):
        if not self.visualization:
            return 0

        self.vis.screen.fill((0, 0, 50))
        self.vis.draw_triangle(self.head_x, self.head_y, self.head_direction)
        self.vis.draw_sanke(self.body_pos[:-1, :])
        self.vis.draw_circle(self.food_pos)
        self.vis.clock.tick(60)

        pygame.display.flip()

    def update_position(self):
        match self.head_direction:
            case 0:
                self.head_x += self.sql + 1
            case 1:
                self.head_y += self.sql + 1
            case 2:
                self.head_x += -self.sql - 1
            case 3:
                self.head_y += -self.sql - 1

        self.body_pos = np.vstack([self.body_pos, [self.head_x, self.head_y]])

        if self.check_colision():
            self.game_running = False
            return False

        if self.food_grabbed():
            self.put_food()
        else:
            self.body_pos = np.delete(self.body_pos, 0, axis=0)

        return True

    def check_colision(self):
        if (
            self.head_x - self.sql < 0
            or self.head_x + self.sql > self.dpl
            or self.head_y - self.sql < 0
            or self.head_y + self.sql > self.dpl
        ):
            return True

        return False

    def food_grabbed(self):
        d = (
            (self.head_x - self.food_pos[0]) ** 2
            + (self.head_y - self.food_pos[1]) ** 2
        ) ** 0.5
        if d < self.sql:
            return True

        return False

    def put_food(self):
        l_limit = 2 * self.sql
        h_limit = self.dpl - l_limit

        x = random.randint(l_limit, h_limit)
        y = random.randint(l_limit, h_limit)

        self.food_pos = (x, y)

    def key_listener(self):
        def on_press(key):
            if key.char == "d":
                self.head_direction = (self.head_direction + 1) % 4
            elif key.char == "a":
                self.head_direction = (self.head_direction - 1) % 4
            # elif key.char == "q":
            #     self.game_running = False
            # elif key.char == "r":
            #     self.restart_game()

        listener = keyboard.Listener(on_press=on_press)

        while True:
            listener.start()
            listener.join()

    def start_key_listener(self):
        self.listener_thread = tr.Thread(target=self.key_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()


game = SnakeGame()
