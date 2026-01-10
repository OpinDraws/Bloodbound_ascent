import arcade
import math
import time
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
        pass

class SlashFlurry:
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0.5       # Быстрый откат для теста (0.5 сек)
        self.damage = 50
        self.radius = 120         # Радиус атаки
        self.last_used_time = 0

    def activate(self, enemy_list):
        now = time.time()
        if now - self.last_used_time < self.cooldown:
            return

        self.last_used_time = now
        print("Skill: Flurry Activated!")
        
        # Позиция игрока
        owner_pos = Vector2(self.owner.center_x, self.owner.center_y)
        
        hit_count = 0
        
        # Перебираем врагов вручную (так как enemy_list это не SpriteList, а список объектов)
        for enemy in enemy_list:
            # Получаем координаты врага (через свойства @property center_x/y)
            enemy_pos = Vector2(enemy.center_x, enemy.center_y)
            
            # Считаем дистанцию
            dist = owner_pos.distance_to(enemy_pos)
            
            # Если враг в радиусе поражения
            if dist <= self.radius:
                # Вектор отталкивания (от игрока к врагу)
                if dist > 0:
                    push_vector = (enemy_pos - owner_pos).normalize()
                else:
                    push_vector = Vector2(1, 0) # Если стоят в одной точке, толкаем вправо
                
                # Наносим урон и передаем вектор для качания
                # Проверяем, есть ли у врага метод take_damage
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(self.damage, push_vector)
                    hit_count += 1

        if hit_count > 0:
            print(f"Flurry hit {hit_count} enemies!")

    def update(self, dt):
        pass

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

        # Ищем ближайшего врага для авто-прицеливания
        for enemy in enemy_list:
            enemy_pos = Vector2(enemy.center_x, enemy.center_y)
            dist = owner_pos.distance_to(enemy_pos)
            if dist < min_dist:
                min_dist = dist
                target_pos = enemy_pos

        # Угол стрельбы
        base_angle = self.owner.angle_view
        if target_pos:
            diff = target_pos - owner_pos
            base_angle = math.degrees(math.atan2(diff.y, diff.x))

        # Спавним снаряды
        angles = [-15, 0, 15]
        for offset in angles:
            proj = Projectile(self.owner.center_x, self.owner.center_y, base_angle + offset, speed=12)
            proj.damage = self.damage 
            projectile_list.append(proj)

    def update(self, dt):
        pass