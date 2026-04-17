import arcade
import math
from core.config import WIDTH, HEIGHT, COLOR_BG

class MenuView(arcade.View):
    """
    Главное меню игры.
    Наследуется от arcade.View, что позволяет легко переключаться между окнами.
    """
    def __init__(self):
        super().__init__()
        self.time = 0.0 
        self.blink_alpha = 255

    def on_show_view(self):
        """Вызывается один раз при переключении на эту сцену."""
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, dt):
        """Логика обновления (анимации)."""
        self.time += dt
        # Эффект "дыхания" для текста (изменяем прозрачность)
        self.blink_alpha = int(128 + 127 * math.sin(self.time * 3))

    def on_draw(self):
        """Отрисовка кадра."""
        self.clear()

        # 1. Заголовок
        arcade.draw_text(
            "Bloodbound Ascent",
            WIDTH / 2,
            HEIGHT / 2 + 50,
            arcade.color.CRIMSON, # Кроваво-красный, под стать вампиру
            font_size=50,
            anchor_x="center",
            font_name=("Times New Roman", "serif") # Попытка использовать шрифт с засечками
        )

        # 2. Подзаголовок
        arcade.draw_text(
            "Refactored Edition",
            WIDTH / 2,
            HEIGHT / 2,
            arcade.color.GRAY,
            font_size=20,
            anchor_x="center",
            italic=True
        )

        # 3. Мигающая надпись "Start"
        # В Arcade цвет задается (R, G, B, A), где A - прозрачность
        text_color = (255, 255, 255, self.blink_alpha)
        
        arcade.draw_text(
            "Press ENTER to Start",
            WIDTH / 2,
            HEIGHT / 2 - 100,
            text_color,
            font_size=24,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            # Импортируем GameView здесь, чтобы избежать круговых зависимостей
            from scenes.game_scene import GameView
            
            game_view = GameView()
            
            # --- ВАЖНО: ОБЯЗАТЕЛЬНО ВЫЗЫВАЕМ SETUP ---
            game_view.setup() 
            # -----------------------------------------
            
            self.window.show_view(game_view)
            
        elif key == arcade.key.ESCAPE:
            arcade.close_window()