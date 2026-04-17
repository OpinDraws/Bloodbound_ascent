import arcade
import math
from PIL import Image
from core.config import WIDTH, HEIGHT
from core.asset_manager import AssetManager

# Наши новые сущности
from entities.player import Player
from entities.base_enemy import DummyEnemy

# Для передачи координат мыши
from pygame.math import Vector2 

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        
        # --- МЕНЕДЖЕРЫ ---
        self.asset_manager = AssetManager()
        
        # --- КАМЕРЫ ---
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # --- СПИСКИ СПРАЙТОВ ---
        self.wall_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        
        # Враги теперь хранятся в обычном списке (т.к. DummyEnemy - это составной объект)
        self.enemies = [] 

        self.player = None
        self.physics_engine = None 
        
        self.background_color = arcade.color.BLACK_OLIVE
        
        # Координаты мыши в мире
        self.mouse_world_x = 0
        self.mouse_world_y = 0

    def setup(self):
        print("--- GameView: Чистый старт (Arcade Refactor) ---")
        
        # 1. СОЗДАНИЕ ИГРОКА
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        
        # 2. СОЗДАНИЕ СТЕН (ВРЕМЕННЫЙ ПОЛ/СТЕНЫ)
        # Потом заменим на TileMap
        try:
            # Если есть текстура стены
            tex_wall = arcade.load_texture("assets/wall.png")
            wall_sprite = arcade.Sprite(tex_wall)
        except:
             # Заглушка
            img_wall = Image.new('RGBA', (40, 40), arcade.color.GRAY)
            wall_texture = arcade.Texture(img_wall, name="wall_solid")
        
        # Генерируем "коробку" стен
        for x in range(0, 2000, 40):
            self.create_wall(x, 0, wall_texture if 'wall_texture' in locals() else None)
            self.create_wall(x, 1000, wall_texture if 'wall_texture' in locals() else None)
        
        for y in range(0, 1000, 40):
            self.create_wall(0, y, wall_texture if 'wall_texture' in locals() else None)
            self.create_wall(2000, y, wall_texture if 'wall_texture' in locals() else None)
            
        # 3. ВРАГИ (МАНЕКЕНЫ)
        for i in range(3):
            enemy = DummyEnemy(400 + i * 150, 400, self.asset_manager)
            self.enemies.append(enemy)

        # 4. ФИЗИКА
        # Игрок сталкивается со стенами
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.wall_list)

    def create_wall(self, x, y, texture):
        if texture:
            wall = arcade.Sprite(texture)
        else:
             # Если текстуры нет, создаем на лету (заглушка)
             img = Image.new('RGBA', (40, 40), arcade.color.GRAY)
             tex = arcade.Texture(img, name=f"wall_{x}_{y}")
             wall = arcade.Sprite(tex)
             
        wall.center_x = x
        wall.center_y = y
        self.wall_list.append(wall)

    def on_draw(self):
        self.clear()
        
        # 1. МИР
        self.camera.use()
        self.wall_list.draw()
        
        # Рисуем врагов
        for enemy in self.enemies:
            enemy.draw()
            
        # Рисуем снаряды
        self.projectile_list.draw()
        
        # Рисуем игрока (наш кастомный метод)
        if self.player:
            self.player.draw_custom()

        # 2. UI (Интерфейс)
        self.gui_camera.use()
        
        # Здоровье
        arcade.draw_text(f"HP: {self.player.hp}", -WIDTH/2 + 20, HEIGHT/2 - 40, arcade.color.RED, 16)
        
        # Подсказки
        arcade.draw_text("WASD: Move | SPACE: Dash | Q/E: Skills | Click: Shoot", 
                         -WIDTH/2 + 20, -HEIGHT/2 + 20, arcade.color.WHITE, 12)
        
        # Таймеры скиллов (простая отладка)
        flurry_cd = self.player.skill_manager.skills['flurry'].cooldown
        last_flurry = self.player.skill_manager.skills['flurry'].last_used_time
        import time
        if time.time() - last_flurry < flurry_cd:
            arcade.draw_text("E: COOLDOWN", -WIDTH/2 + 20, HEIGHT/2 - 60, arcade.color.GRAY, 12)
        else:
            arcade.draw_text("E: READY", -WIDTH/2 + 20, HEIGHT/2 - 60, arcade.color.GREEN, 12)

    def on_update(self, dt):
        # 1. Ввод и Физика игрока
        if not self.player.is_dashing:
            self.process_input()
        
        self.physics_engine.update()
        
        # 2. Обновление игрока (анимация, плащ, кулдауны)
        if self.player:
            self.player.mouse_pos = Vector2(self.mouse_world_x, self.mouse_world_y)
            self.player.update()

        # 3. Обновление врагов
        for enemy in self.enemies:
            enemy.update(dt)

        # 4. Обновление снарядов и коллизии
        self.projectile_list.update(dt)
        self.check_collisions()
        
        # 5. Камера
        self.scroll_to_player()

    def check_collisions(self):
        """Обработка попаданий."""
        for proj in self.projectile_list:
            # Стены
            if arcade.check_for_collision_with_list(proj, self.wall_list):
                proj.remove_from_sprite_lists()
                continue
            
            # Враги
            hit_enemy = False
            for enemy in self.enemies:
                # Проверяем хитбокс тела манекена
                if arcade.check_for_collision(proj, enemy.body_sprite):
                    push_vec = Vector2(proj.change_x, proj.change_y).normalize()
                    enemy.take_damage(proj.damage, push_vec)
                    hit_enemy = True
                    break 
            
            if hit_enemy:
                proj.remove_from_sprite_lists()

    def process_input(self):
        """Управление движением (WASD)."""
        self.player.change_x = 0
        self.player.change_y = 0
        if not hasattr(self.window, "key_pressed"): return

        speed = self.player.speed
        if self.window.key_pressed.get(arcade.key.W): self.player.change_y = speed
        elif self.window.key_pressed.get(arcade.key.S): self.player.change_y = -speed
        if self.window.key_pressed.get(arcade.key.A): self.player.change_x = -speed
        elif self.window.key_pressed.get(arcade.key.D): self.player.change_x = speed

    def on_mouse_motion(self, x, y, dx, dy):
        """Слежение за мышью."""
        cam_x, cam_y = self.camera.position
        self.mouse_world_x = x + (cam_x - self.window.width / 2)
        self.mouse_world_y = y + (cam_y - self.window.height / 2)

    def on_mouse_press(self, x, y, button, modifiers):
        """Стрельба."""
        if button == arcade.MOUSE_BUTTON_LEFT and self.player:
            projectile = self.player.shoot()
            if projectile:
                self.projectile_list.append(projectile)

    def on_key_press(self, key, modifiers):
        """Кнопки действий."""
        if not hasattr(self.window, "key_pressed"): self.window.key_pressed = {}
        self.window.key_pressed[key] = True

        if self.player:
            # DASH
            if key == arcade.key.SPACE:
                input_vec = Vector2(0, 0)
                if self.window.key_pressed.get(arcade.key.W): input_vec.y = 1
                elif self.window.key_pressed.get(arcade.key.S): input_vec.y = -1
                if self.window.key_pressed.get(arcade.key.A): input_vec.x = -1
                elif self.window.key_pressed.get(arcade.key.D): input_vec.x = 1
                self.player.start_dash(input_vec)

            # SKILLS (передаем список врагов и снарядов)
            self.player.skill_manager.on_key_press(key, self.enemies, self.projectile_list)

        if key == arcade.key.ESCAPE:
            from scenes.menu_scene import MenuView
            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if hasattr(self.window, "key_pressed"): self.window.key_pressed[key] = False

    def scroll_to_player(self):
        """Камера."""
        target_x = self.player.center_x
        target_y = self.player.center_y
        curr_x = self.camera.position.x
        curr_y = self.camera.position.y
        lerp_speed = 0.1
        new_x = curr_x + (target_x - curr_x) * lerp_speed
        new_y = curr_y + (target_y - curr_y) * lerp_speed
        self.camera.position = (new_x, new_y)