import arcade
import math
import random
from PIL import Image

class DummyEnemy:
    """
    Манекен для битья (v4: Настройка высоты посадки).
    """
    def __init__(self, x, y, asset_manager):
        self.x = x
        self.y = y
        self.hp = 100
        
        # --- МАСШТАБ ---
        self.scale = 0.08 
        
        # --- ФИЗИКА (Жесткая) ---
        self.angle = 0
        self.angular_vel = 0
        
        # Damping: Меньше число = быстрее остановка (0.8 очень быстро гасит скорость)
        self.damping = 0.80     
        
        # Stiffness: Больше число = жестче пружина (быстрее возврат в центр)
        self.stiffness = 0.15   
        
        # Максимальный угол отклонения (совсем чуть-чуть)
        self.max_angle = 50

        self.sprites = arcade.SpriteList()

        # 1. ПАЛКА
        try:
            tex_stick = arcade.load_texture("assets/dummy_stick.png")
            self.stick_sprite = arcade.Sprite(tex_stick, scale=self.scale)
        except Exception:
             img = Image.new('RGBA', (10, 60), (100, 50, 20, 255))
             tex_stick = arcade.Texture(img, name="stick_stub")
             self.stick_sprite = arcade.Sprite(tex_stick, scale=self.scale)

        self.stick_sprite.center_x = x
        self.stick_sprite.center_y = y
        self.sprites.append(self.stick_sprite)

        # 2. ТЕЛО
        try:
            tex_body = arcade.load_texture("assets/dummy_body.png")
            self.body_sprite = arcade.Sprite(tex_body, scale=self.scale)
        except Exception:
             img = Image.new('RGBA', (50, 80), (200, 180, 150, 255))
             tex_body = arcade.Texture(img, name="body_stub")
             self.body_sprite = arcade.Sprite(tex_body, scale=self.scale)

        self.pivot_offset = self.body_sprite.height / 2 
        
        self.update_body_position()
        self.sprites.append(self.body_sprite)

    def update(self, dt):
        force = -self.stiffness * self.angle
        self.angular_vel += force
        self.angular_vel *= self.damping
        self.angle += self.angular_vel
        self.angle = max(-self.max_angle, min(self.max_angle, self.angle))
        
        self.body_sprite.angle = self.angle
        self.update_body_position()

    def update_body_position(self):
        rad = math.radians(self.angle)
        
        # --- НАСТРОЙКА ВЫСОТЫ ---
        # overlap: Насколько глубоко тело "насаживается" на палку (в пикселях)
        # Увеличьте это число, если щель все еще видна!
        overlap = 80
        
        # Точка опоры = Верхушка палки МИНУС нахлест
        pivot_x = self.stick_sprite.center_x
        pivot_y = self.stick_sprite.top - overlap
        
        # Смещаем центр тела
        self.body_sprite.center_x = pivot_x + math.sin(rad) * self.pivot_offset
        self.body_sprite.center_y = pivot_y + math.cos(rad) * self.pivot_offset

    def draw(self):
        self.sprites.draw()

    def take_damage(self, amount, push_vector=None):
        self.hp -= amount
        
        impulse = amount * 0.1 
        if push_vector:
            if push_vector.x > 0:
                self.angular_vel -= impulse 
            else:
                self.angular_vel += impulse
        else:
            self.angular_vel += random.choice([-5, 5])
            
        self.angular_vel = max(-10, min(10, self.angular_vel))

    @property
    def center_x(self): return self.x
    @property
    def center_y(self): return self.y