import arcade
from PIL import Image
from core.config import WIDTH, HEIGHT
from core.asset_manager import AssetManager
from entities.player import Player
from pygame.math import Vector2
from entities.base_enemy import DummyEnemy

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.asset_manager = AssetManager()
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList() # Список для снарядов

        self.player = None
        self.physics_engine = None 
        self.background_color = arcade.color.BLACK_OLIVE
        self.mouse_world_x = 0
        self.mouse_world_y = 0

    def setup(self):
        # 1. Игрок
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.player_list.append(self.player)

        # 2. Стены
        img_wall = Image.new('RGBA', (40, 40), arcade.color.GRAY)
        wall_texture = arcade.Texture(img_wall, name="wall_solid")
        for i in range(0, 1000, 50):
            wall = arcade.Sprite(wall_texture)
            wall.center_x = i
            wall.center_y = 200
            self.wall_list.append(wall)
            
        # 3. Враги (Добавим пару манекенов для теста скиллов)
        self.enemies = [] # Используем обычный список
        for i in range(3):
            # Передаем asset_manager (хотя пока он не используется внутри, на будущее)
            enemy = DummyEnemy(300 + i * 100, 400, self.asset_manager)
            self.enemies.append(enemy)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.wall_list)

    def on_draw(self):
        self.clear()
        self.camera.use()
        
        self.wall_list.draw()
        
        # --- РИСУЕМ ВРАГОВ ---
        for enemy in self.enemies:
            enemy.draw() # Вызываем метод draw() составного объекта
            
        self.projectile_list.draw()
        
        if self.player:
            self.player.draw_custom()

        self.gui_camera.use()
        arcade.draw_text(f"HP: {self.player.hp}", -WIDTH/2 + 20, HEIGHT/2 - 40, arcade.color.RED, 16)
        
        # Индикаторы (для дебага)
        dash_status = "READY" if self.player.can_dash else "CD"
        arcade.draw_text(f"Dash: {dash_status}", -WIDTH/2 + 20, HEIGHT/2 - 60, arcade.color.WHITE, 12)

    def on_update(self, dt):
        # ВАЖНО: Если игрок в дэше, process_input не должен перебивать его скорость
        if not self.player.is_dashing:
            self.process_input()
            
        self.physics_engine.update()
        self.projectile_list.update(dt) # Передаем dt!
        
        # Обновляем логику игрока
        if self.player:
            self.player.mouse_pos = Vector2(self.mouse_world_x, self.mouse_world_y)
            self.player.update()

        # --- ОБНОВЛЯЕМ ВРАГОВ ---
        for enemy in self.enemies:
            enemy.update(dt)

        # --- ОБНОВЛЕННАЯ ЛОГИКА ПОПАДАНИЙ СНАРЯДОВ ---
        # Теперь нужно проверять коллизию снаряда с ХИТБОКСОМ врага.
        # Для манекена хитбоксом будет body_sprite.
        
        for proj in self.projectile_list:
            # Проверка со стенами
            if arcade.check_for_collision_with_list(proj, self.wall_list):
                proj.remove_from_sprite_lists()
                continue

            # Проверка с врагами (вручную перебираем список)
            hit_enemy = False
            for enemy in self.enemies:
                # Проверяем пересечение снаряда с ТЕЛОМ манекена
                if arcade.check_for_collision(proj, enemy.body_sprite):
                    # Вычисляем вектор удара (от снаряда к врагу)
                    push_vec = Vector2(proj.change_x, proj.change_y).normalize()
                    enemy.take_damage(proj.damage, push_vec)
                    hit_enemy = True
                    break # Снаряд попал в одного и исчезает
            
            if hit_enemy:
                proj.remove_from_sprite_lists()

        self.scroll_to_player()

    def on_mouse_motion(self, x, y, dx, dy):
        cam_x, cam_y = self.camera.position
        self.mouse_world_x = x + (cam_x - self.window.width / 2)
        self.mouse_world_y = y + (cam_y - self.window.height / 2)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.player:
            projectile = self.player.shoot()
            if projectile:
                self.projectile_list.append(projectile)

    def on_key_press(self, key, modifiers):
        if not hasattr(self.window, "key_pressed"): self.window.key_pressed = {}
        self.window.key_pressed[key] = True

        # --- ОБРАБОТКА СКИЛЛОВ ---
        if self.player:
            # 1. DASH (ПРОБЕЛ)
            if key == arcade.key.SPACE:
                # Определяем направление ввода
                input_vec = Vector2(0, 0)
                if self.window.key_pressed.get(arcade.key.W): input_vec.y = 1
                elif self.window.key_pressed.get(arcade.key.S): input_vec.y = -1
                if self.window.key_pressed.get(arcade.key.A): input_vec.x = -1
                elif self.window.key_pressed.get(arcade.key.D): input_vec.x = 1
                
                self.player.start_dash(input_vec)

            # 2. АТАКИ (Q / E)
            # Передаем списки, чтобы скиллы знали, кого бить и куда спавнить снаряды
            self.player.skill_manager.on_key_press(key, self.enemies, self.projectile_list)

        if key == arcade.key.ESCAPE:
            from scenes.menu_scene import MenuView
            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if hasattr(self.window, "key_pressed"): self.window.key_pressed[key] = False
        
    def process_input(self):
        # Обычное движение
        self.player.change_x = 0
        self.player.change_y = 0
        if not hasattr(self.window, "key_pressed"): return
        speed = self.player.speed
        if self.window.key_pressed.get(arcade.key.W): self.player.change_y = speed
        elif self.window.key_pressed.get(arcade.key.S): self.player.change_y = -speed
        if self.window.key_pressed.get(arcade.key.A): self.player.change_x = -speed
        elif self.window.key_pressed.get(arcade.key.D): self.player.change_x = speed

    def scroll_to_player(self):
        # (Без изменений)
        target_x = self.player.center_x
        target_y = self.player.center_y
        curr_x = self.camera.position.x
        curr_y = self.camera.position.y
        lerp_speed = 0.1
        new_x = curr_x + (target_x - curr_x) * lerp_speed
        new_y = curr_y + (target_y - curr_y) * lerp_speed
        self.camera.position = (new_x, new_y)