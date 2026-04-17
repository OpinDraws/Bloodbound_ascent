import arcade
import math
import time
import random
from pygame.math import Vector2
from entities.projectile import Projectile

class SkillManager:
    def __init__(self, player):
        self.player = player
        self.skills = {
            'flurry': SlashFlurry(player),
            'cloud': DaggerCloudSkill(player)
        }

    def on_key_press(self, key, enemy_list, projectile_list):
        """Обработка нажатий клавиш."""
        if key == arcade.key.E:
            self.skills['flurry'].activate(enemy_list)
        elif key == arcade.key.Q:
            self.skills['cloud'].activate(projectile_list, enemy_list)

    def update(self, dt):
        for skill in self.skills.values():
            skill.update(dt)

    def draw(self):
        # Вызываем отрисовку всех скиллов
        for skill in self.skills.values():
            skill.draw()

class SlashFlurry:
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0.5       # Быстрый откат
        self.damage = 50
        self.radius = 120         # Радиус атаки
        self.last_used_time = 0
        
        # Настройки визуала
        self.vfx_duration = 0.4   # Время жизни анимации (в секундах)
        self.active_vfx = []      # Список активных анимаций разреза

    def activate(self, enemy_list):
        now = time.time()
        if now - self.last_used_time < self.cooldown:
            return

        self.last_used_time = now
        print("Skill: Flurry Activated!")
        
        owner_pos = Vector2(self.owner.center_x, self.owner.center_y)
        
        # Добавляем эффект в список на отрисовку
        # Используем направление взгляда игрока (angle_view) как направление атаки
        self.active_vfx.append({
            'start_time': now,
            'pos': Vector2(owner_pos.x, owner_pos.y),
            'angle': getattr(self.owner, 'angle_view', 0)
        })
        
        hit_count = 0
        
        for enemy in enemy_list:
            enemy_pos = Vector2(enemy.center_x, enemy.center_y)
            dist = owner_pos.distance_to(enemy_pos)
            
            if dist <= self.radius:
                if dist > 0:
                    push_vector = (enemy_pos - owner_pos).normalize()
                else:
                    push_vector = Vector2(1, 0)
                
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(self.damage, push_vector)
                    hit_count += 1

        if hit_count > 0:
            print(f"Flurry hit {hit_count} enemies!")

    def update(self, dt):
        # Очищаем старые визуальные эффекты, которые уже отыграли
        now = time.time()
        self.active_vfx = [vfx for vfx in self.active_vfx if now - vfx['start_time'] < self.vfx_duration]

    def draw(self):
        # Отрисовка всех активных эффектов разреза
        now = time.time()
        print("Отрисовка")
        for vfx in self.active_vfx:
            progress = (now - vfx['start_time']) / self.vfx_duration
            if progress > 1.0:
                continue

            # Преобразуем угол и находим центр удара
            rad = math.radians(vfx['angle'])
            direction = Vector2(math.cos(rad), math.sin(rad))
            impact_center = vfx['pos'] + direction * (self.radius * 0.6)
            
            # Генератор случайных чисел для дерганного, но стабильного эффекта
            seed = int(progress * 20) 
            rng = random.Random(seed)
            
            # Цвета Arcade в формате RGBA (от белого к темно-красному)
            if progress < 0.2:
                color_core = (255, 255, 255)
                color_glow = (255, 100, 100)
            elif progress < 0.7:
                color_core = (255, 200, 200)
                color_glow = (200, 0, 0)
            else:
                color_core = (100, 0, 0)
                color_glow = (50, 0, 0)
                
            alpha = int(255 * (1 - progress))
            rgba_core = (*color_core, alpha)
            rgba_glow = (*color_glow, alpha)
            
            # Рисуем "Сферу ударов" - линии
            num_slashes = 8
            for _ in range(num_slashes):
                slash_angle = rng.uniform(0, math.pi)
                slash_dir = Vector2(math.cos(slash_angle), math.sin(slash_angle))
                
                offset = Vector2(rng.uniform(-20, 20), rng.uniform(-20, 20))
                slash_center = impact_center + offset
                
                length = rng.uniform(self.radius, self.radius * 1.5)
                p1 = slash_center - slash_dir * (length / 2)
                p2 = slash_center + slash_dir * (length / 2)
                
                width = max(1, int(4 * (1 - progress)))
                
                # В Arcade мы просто рисуем линии одна поверх другой
                if width > 1:
                    arcade.draw_line(p1.x, p1.y, p2.x, p2.y, rgba_glow, width + 4)
                arcade.draw_line(p1.x, p1.y, p2.x, p2.y, rgba_core, width)

            # Рисуем внешний круг ударной волны
            points = []
            for i in range(16):
                angle = (i / 16) * math.pi * 2
                r = self.radius * (0.5 + progress * 0.5) + rng.uniform(-5, 5)
                px = impact_center.x + math.cos(angle) * r
                py = impact_center.y + math.sin(angle) * r
                points.append((px, py))
            
            # Замыкаем круг, копируя первую точку в конец (особенность draw_line_strip)
            if len(points) > 2:
                points.append(points[0]) 
                arcade.draw_line_strip(points, rgba_glow, 2)
    def on_draw(self):
        self.clear()
        # Сначала рисуем карту/фон
        self.tile_map.draw()
        # Потом игрока и врагов
        self.player_list.draw()
        self.enemy_list.draw()
        # И только в конце — эффекты поверх всего!
        
        self.skill_manager.draw()


class DaggerCloudSkill:
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 1.0
        self.last_used_time = 0
        self.damage = 30

    def activate(self, projectile_list, enemy_list):
        now = time.time()
        if now - self.last_used_time < self.cooldown:
            return

        self.last_used_time = now
        print("Skill: Dagger Cloud!")

        target_pos = None
        min_dist = 1000
        owner_pos = Vector2(self.owner.center_x, self.owner.center_y)

        for enemy in enemy_list:
            enemy_pos = Vector2(enemy.center_x, enemy.center_y)
            dist = owner_pos.distance_to(enemy_pos)
            if dist < min_dist:
                min_dist = dist
                target_pos = enemy_pos

        base_angle = self.owner.angle_view
        if target_pos:
            diff = target_pos - owner_pos
            base_angle = math.degrees(math.atan2(diff.y, diff.x))

        angles = [-15, 0, 15]
        for offset in angles:
            proj = Projectile(self.owner.center_x, self.owner.center_y, base_angle + offset, speed=12)
            proj.damage = self.damage 
            projectile_list.append(proj)

    def update(self, dt):
        pass

    def draw(self):
        # Заглушка, чтобы менеджер мог безопасно вызывать draw() у всех скиллов
        pass