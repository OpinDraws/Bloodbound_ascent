import arcade
from core.config import WIDTH, HEIGHT
from core.asset_manager import AssetManager
from scenes.menu_scene import MenuView  # <-- Теперь импортируем наше новое меню

class GameWindow(arcade.Window):
    def __init__(self):
        # Инициализация окна
        super().__init__(WIDTH, HEIGHT, "Bloodbound Ascent - Arcade Edition", antialiasing=True)
        
        # --- ЗАГРУЗКА РЕСУРСОВ ---
        # Мы вызываем это здесь, чтобы при старте игры все картинки и звуки
        # загрузились в память (Singleton сработает как надо)
        self.asset_manager = AssetManager()
        self.asset_manager.load_resources()

    def setup(self):
        """Настройка начального состояния."""
        # Создаем и показываем сцену Меню
        start_view = MenuView()
        self.show_view(start_view)

def main():
    window = GameWindow()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()