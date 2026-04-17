import arcade
import math
import random
from PIL import Image

class Projectile(arcade.Sprite):
    def __init__(self, x, y, angle_degrees, speed=10):
        # --- ВИЗУАЛ (Временный светящийся шар) ---
        size = 16
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Внешний красный круг
        draw.ellipse((0, 0, size-1, size-1), fill=(200, 0, 0, 150))
        # Внутреннее желтое ядро
        draw.ellipse((4, 4, size-5, size-5), fill=(255, 255, 100, 255))
        
        # Уникальное имя текстуры, чтобы не было конфликтов
        texture = arcade.Texture(img, name=f"proj_bolt_{random.randint(0, 100000)}")

        # В Arcade 3.0 передаем текстуру первым аргументом
        super().__init__(texture)

        self.center_x = x
        self.center_y = y
        self.angle = angle_degrees 

        # Вычисляем вектор движения
        angle_rad = math.radians(angle_degrees)
        self.change_x = math.cos(angle_rad) * speed
        self.change_y = math.sin(angle_rad) * speed
        
        self.damage = 25
        self.lifetime = 2.0 # Время жизни в секундах

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Добавляем delta_time=1/60, чтобы метод принимал аргумент, если его передадут
    def update(self, delta_time: float = 1/60):
        """Движение и удаление снаряда."""
        
        # Движение (Arcade сам использует change_x/y, но можно и вручную)
        self.center_x += self.change_x
        self.center_y += self.change_y
        
        # Таймер жизни теперь зависит от реального времени
        # Если delta_time не передан (равен 1/60), будет работать как раньше
        self.lifetime -= delta_time
        
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()