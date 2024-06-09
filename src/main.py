import pygame
import sys
import time
from Background import Background
from Camera import Camera
from Serin import Serin
import spawn
import monster_squirrel
import monster_BamBoo  # 대나무 몬스터 모듈
import monster_Spirit  # 영혼 몬스터 모듈
from ui import Ui
from Inventory import Inventory
from AppleWeapon import AppleWeapon  # 사과무기
from DamageText import DamageText  # 데미지 표시
from Gem import Gem  # 경험치
from LevelUpUI import LevelUpUI

class Main:
    def __init__(self):
        pygame.init()
        self.screen_width = 980
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("밤의 수호자 세린")

        self.background = Background("./image/background.png")
        self.boundary_width = self.background.width
        self.boundary_height = self.background.height

        # 세린을 맵의 정 가운데에 배치
        serin_start_x = self.boundary_width // 2
        serin_start_y = self.boundary_height // 2
        self.serin = Serin(serin_start_x, serin_start_y, self.boundary_width, self.boundary_height)

        self.camera = Camera(self.screen_width, self.screen_height)
        self.running = True

        self.monsters = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        self.monster_spawner = spawn.MonsterSpawner(self.serin, self.all_sprites, self.monsters)
        self.monster_spawner.add_monster_class(monster_squirrel.SquirrelMonster)
        # 몬스터 클래스를 관리하는 리스트와 타이머 초기화
        self.monster_classes = [monster_BamBoo.BamBooMonster, monster_Spirit.SpiritMonster]
        self.next_monster_time = 60000  # 60초 간격으로 몬스터 클래스 추가
        self.last_monster_time = pygame.time.get_ticks()
        self.monster_index = 0

        # Serin을 전체 스프라이트 그룹에 추가
        self.all_sprites.add(self.serin)

        # 타이머 초기화
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.start_time = time.time()

        # 경험치 바 초기화
        self.exp = 0
        self.max_exp = 100
        self.level = 1
        # 몬스터 잡은 카운트
        self.monster_kills = 0
        self.kill_icon = pygame.image.load("./image/monster_kill_icon.png").convert_alpha()
        # 코인 개수
        self.coin_count = 0
        self.coin = pygame.image.load("./image/coin.png")
        self.inventory = Inventory()
        self.ui = Ui(self.inventory, self.screen)

        # 사과 무기 초기화
        self.apple_weapon = AppleWeapon(self.serin, 100, 5, "./image/apple.png")
        self.all_sprites.add(self.apple_weapon)

        self.damage_texts = pygame.sprite.Group()
        
        # 레벨업 UI초기화
        self.level_up_ui  = LevelUpUI(self.screen,"./image/LevelUpUI.png",self)
        
        # 게임 중단 초기화
        self.paused = False

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self._check_collisions()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.level_up_ui.active:
                self.level_up_ui.handle_event(event)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # ESC로 UI 비활성화 및 게임 재개
                self.level_up_ui.active = False
                self.paused = False

    def _update(self):
        if not self.paused:
            self.serin.update()
            self.camera.update(self.serin)
            self.monster_spawner.spawn_monster()
            self.all_sprites.update()
            self.damage_texts.update()
            self.gems.update()
            pygame.display.flip()
            self.clock.tick(60)

        # 일정 시간마다 몬스터 클래스 추가
        current_time = pygame.time.get_ticks()
        if current_time - self.last_monster_time > self.next_monster_time:
            if self.monster_index < len(self.monster_classes):
                self.monster_spawner.add_monster_class(self.monster_classes[self.monster_index])
                self.monster_index += 1
                self.last_monster_time = current_time
        #일정 시간마다 몬스터 스텟 업데이트
        if current_time%10000==0 and self.monster_index>1:
            for monster in self.monsters:
                monster.speed+=0.3
                monster.power+=0.2
                monster.health+=100

        if self.exp >= self.max_exp:  # 경험치가 최대치에 도달하면
            self.level += 1
            self.exp = 0  # 경험치 초기화
            if self.level % 1 == 0:
                self.level_up_ui.activate() 
                self.paused = True

    def _draw(self):
        self.background.draw(self.screen, self.camera.x, self.camera.y)
        if not self.paused:
            for sprite in self.all_sprites:
                sprite.draw(self.screen, self.camera.x, self.camera.y)
            for gem in self.gems:
                gem.draw(self.screen, self.camera.x, self.camera.y)
            for damage_text in self.damage_texts:
                self.screen.blit(damage_text.image, (damage_text.rect.x -
                                self.camera.x, damage_text.rect.y - self.camera.y))
               

        self._draw_clock()
        self._draw_exp_bar()
        self._draw_kill_count()
        self._draw_coin()
        self.ui.draw()
        self.level_up_ui.draw()
        
        if self.level_up_ui.active:
            self.level_up_ui.draw()

        pygame.display.flip()

    def _check_collisions(self):
        for monster in self.monsters:
            if self.serin.hitbox.colliderect(monster.hitbox):
                self.serin.health -= monster.power  # 몬스터의 공격력에 따라 체력 감소
                if self.serin.health <= 0:
                    self.serin.kill()
                    self.running = False

            if self.apple_weapon.rect.colliderect(monster.hitbox):
                damage = 10  # 사과 무기의 공격력
                monster.health -= damage
                self.damage_texts.add(DamageText(monster.rect.centerx, monster.rect.centery, damage))
                if monster.health <= 0:
                    monster.kill()
                    self.monster_kills += 1
                    self.coin_count += 1  # 몬스터 처치 시 코인 증가
                    gem = Gem(monster.rect.centerx, monster.rect.centery)
                    self.gems.add(gem)  # 몬스터가 죽은 위치에 보석 추가
                    self.all_sprites.add(gem)

        # Serin과 보석의 충돌 체크
        for gem in self.gems:
            if self.serin.hitbox.colliderect(gem.rect):
                self.exp += 10  # 보석 획득 시 경험치 증가
                gem.kill()  # 보석 제거

    def _draw_clock(self):
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = f"{minutes:02}:{seconds:02}"
        
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 80))

        self.screen.blit(text_surface, text_rect)

    def _draw_exp_bar(self):
        bar_length = 1300  # 경험치 바 길이
        bar_height = 35   # 경험치 바 높이
        fill = (self.exp / self.max_exp) * bar_length
        outline_rect = pygame.Rect((self.screen_width - bar_length) // 2, 10, bar_length, bar_height)
        fill_rect = pygame.Rect((self.screen_width - bar_length) // 2, 10, fill, bar_height)

        pygame.draw.rect(self.screen, (255, 255, 0),
                         fill_rect)  # 채우기 부분 노란색으로 그리기
        pygame.draw.rect(self.screen, (255, 255, 255),
                         outline_rect, 2)  # 경계선 흰색으로 그리기
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        text_rect = level_text.get_rect(midright=(self.screen_width - 10, 30))
        self.screen.blit(level_text, text_rect)  #레벨 표시

    def _draw_kill_count(self):
        kill_count_text = f"{self.monster_kills}"
        text_surface = self.font.render(kill_count_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(top=50, right=self.screen_width - 200)
        icon_rect = self.kill_icon.get_rect(top=45, left=text_rect.right + 10)

        self.screen.blit(self.kill_icon, icon_rect)
        self.screen.blit(text_surface, text_rect)  # 그 다음 텍스트 그리기

    def _draw_coin(self):
        coin_count_text = f"{self.coin_count}"
        text_surface = self.font.render(coin_count_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(top=50, right=self.screen_width - 100)

        icon_rect = self.coin.get_rect(top=29, left=text_rect.right-10)

        self.screen.blit(self.coin, icon_rect)
        self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    Main().run()
