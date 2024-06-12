import pygame
import math
import random


class Leaf(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage):
        super().__init__()
        self.image = pygame.image.load("./image/leaf.png").convert_alpha()

        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 14
        self.damage = damage
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        # 2초가 지나면 삭제
        if pygame.time.get_ticks() - self.creation_time > 2000:
            self.kill()

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.rect.x -
                    camera_x, self.rect.y - camera_y))


class LeafWeapon:
    def __init__(self, serin, screen, all_sprite):
        self.serin = serin
        self.screen = screen
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = [0, 1000, 900, 900, 800, 700]
        self.angle = [0, 180, 180, 90, 90, 45]
        self.damage = [0, 10, 15, 15, 20, 25]
        self.level = 1
        self.maxLevel = 5
        self.all_sprite = all_sprite
        self.image = pygame.image.load("./image/leaf.png").convert_alpha()

    def attack(self):
        if self.level == 0:
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay[self.level]:
            self.last_shot = now
            for angle in range(0, 360, self.angle[self.level]):
                rad_angle = math.radians(angle)
                leaf = Leaf(self.serin.rect.centerx, self.serin.rect.centery,
                            rad_angle, self.damage[self.level])
                self.all_sprite.add(leaf)
