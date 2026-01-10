import arcade
import math
import time
from PIL import Image
from pygame.math import Vector2
from rendering.vampire import draw_vampire_arcade
from entities.projectile import Projectile

# ИМПОРТИРУЕМ НОВЫЙ МЕНЕДЖЕР
from systems.skills import SkillManager

class Player(arcade.Sprite):
    def __init__(self, x, y):
        img = Image.new('RGBA', (30, 50), (0, 0, 0, 0))
        texture = arcade.Texture(img, name="player_hitbox")
        super().__init__(texture)
        
        self.center_x = x
        self.center_y = y

        # --- ЛОГИКА ---
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.speed = 5.0
        
        # --- DASH (РЫВОК) ---
        self.can_dash = True
        self.is_dashing = False
        self.dash_speed = 15.0      # Скорость рывка
        self.dash_duration = 0.2    # Длительность (сек)
        self.dash_cooldown = 1.0    # Откат (сек)
        self.dash_timer = 0         # Таймер длительности
        self.last_dash_time = 0     # Время последнего рывка
        self.dash_dir = Vector2(0, 0) # Направление рывка

        # Визуал
        self.angle_view = 0
        self.walk_cycle = 0
        
        # Плащ
        self.cape_len = 8
        self.cape_seg_dist = 10
        self.cape_points = [Vector2(x, y - i*10) for i in range(self.cape_len)]

        # Боевка
        self.hp = 100
        self.max_hp = 100
        self.last_shot_time = 0
        self.shoot_cooldown = 0.3 

        self.mouse_pos = Vector2(0, 0)
        
        # --- SKILLS ---
        self.skill_manager = SkillManager(self)

    def update(self):
        # (Оставляем update без аргументов для совместимости с arcade.SpriteList.update)
        # Но нам нужен dt для таймеров. Arcade обычно вызывает update() без dt.
        # Поэтому мы будем использовать time.time() или считать dt = 1/60 приблизительно.
        dt = 1/60 
        
        # 1. ЛОГИКА РЫВКА
        current_time = time.time()
        
        # Восстановление рывка
        if not self.can_dash and (current_time - self.last_dash_time > self.dash_cooldown):
            self.can_dash = True

        if self.is_dashing:
            # Пока идет рывок, игнорируем обычное управление (change_x/y)
            # и двигаем игрока принудительно
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.change_x = 0 # Стоп после рывка
                self.change_y = 0
            else:
                self.change_x = self.dash_dir.x * self.dash_speed
                self.change_y = self.dash_dir.y * self.dash_speed

        # 2. СИНХРОНИЗАЦИЯ
        self.pos.x = self.center_x
        self.pos.y = self.center_y
        self.vel.x = self.change_x
        self.vel.y = self.change_y

        # 3. Анимация и плащ
        speed = self.vel.length()
        if speed > 0.5: self.walk_cycle += 0.2
        else: self.walk_cycle = 0

        dx = self.mouse_pos.x - self.center_x
        dy = self.mouse_pos.y - self.center_y
        self.angle_view = math.degrees(math.atan2(dy, dx))

        self._update_cape()
        
        # Обновление кулдаунов скиллов
        self.skill_manager.update(dt)

    def _update_cape(self):
        # (Тот же код плаща, что и раньше)
        anchor = self.pos + Vector2(0, 15) 
        self.cape_points[0] = anchor
        wind = Vector2(-self.vel.x * 2, -self.vel.y * 2) 
        for i in range(1, self.cape_len):
            prev = self.cape_points[i-1]
            curr = self.cape_points[i]
            target = prev + Vector2(0, -self.cape_seg_dist)
            if self.vel.length() > 0.1: target += wind
            noise = math.sin(time.time() * 10 + i) * 2
            target.x += noise
            self.cape_points[i] = curr.lerp(target, 0.4)
        for _ in range(2):
            for i in range(self.cape_len - 1):
                p1, p2 = self.cape_points[i], self.cape_points[i+1]
                delta = p2 - p1
                if delta.length() > self.cape_seg_dist:
                    self.cape_points[i+1] = p1 + delta.normalize() * self.cape_seg_dist

    def start_dash(self, input_vector):
        """Запуск рывка."""
        if self.can_dash and not self.is_dashing:
            self.is_dashing = True
            self.can_dash = False
            self.last_dash_time = time.time()
            self.dash_timer = self.dash_duration
            
            # Если игрок стоит на месте, рывок вперед (по курсору) или вправо
            if input_vector.length() == 0:
                 rad = math.radians(self.angle_view)
                 self.dash_dir = Vector2(math.cos(rad), math.sin(rad))
            else:
                self.dash_dir = Vector2(input_vector.x, input_vector.y).normalize()

    def shoot(self):
        # (Тот же код стрельбы)
        now = time.time()
        if now - self.last_shot_time < self.shoot_cooldown: return None
        self.last_shot_time = now
        spawn_dist = 30
        spawn_x = self.center_x + math.cos(math.radians(self.angle_view)) * spawn_dist
        spawn_y = self.center_y + math.sin(math.radians(self.angle_view)) * spawn_dist
        return Projectile(spawn_x, spawn_y, self.angle_view)

    def draw_custom(self):
        draw_vampire_arcade(self.center_x, self.center_y, self.angle_view, 
                            self.walk_cycle, self.vel.length(), self.cape_points)