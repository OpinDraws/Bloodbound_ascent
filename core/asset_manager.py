import arcade
import os
from core.config import ASSETS_DIR

class AssetManager:
    _instance = None

    def __new__(cls):
        """Паттерн Singleton."""
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        # В Arcade картинки — это Texture
        self.textures = {} 
        # Звуки — это Sound
        self.sounds = {} 
        
        # Для управления проигрываемой музыкой (чтобы можно было стопнуть)
        self.current_music_player = None 
        
        self.initialized = True

    def load_resources(self):
        """Загружает ресурсы в контекст OpenGL."""
        print("--- AssetManager (Arcade): Загрузка... ---")
        self._load_images()
        self._load_sounds()
        self._load_music()
        print("--- AssetManager: Готово ---")

    def _load_images(self):
        # Пример загрузки иконки босса
        icon_path = os.path.join(ASSETS_DIR, 'boss_icon.jpg')
        if os.path.exists(icon_path):
            try:
                # В Arcade мы грузим Texture. 
                # Она сразу попадает в видеопамять, поэтому рисуется супер-быстро.
                self.textures['boss_icon'] = arcade.load_texture(icon_path)
            except Exception as e:
                print(f"Ошибка загрузки текстуры {icon_path}: {e}")
        else:
            print(f"Файл не найден: {icon_path}")

    def _load_sounds(self):
        # Загружаем эффекты
        sound_files = [
            ('tentacle_lunge', 'tentacle_lunge.wav'),
            ('tentacle_strike', 'tentacle_strike.wav'),
            ('brain_spike', 'brain_spike.wav'),
            ('boss_spear', 'boss_spear.wav')
        ]

        for name, filename in sound_files:
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                # load_sound работает и с wav, и с mp3, и с ogg
                self.sounds[name] = arcade.load_sound(path)

    def _load_music(self):
        # Загружаем музыку (как Sound объекты)
        tracks = ['boss', 'dungeon']
        for name in tracks:
            # Arcade умен, он сам поймет формат
            for ext in ['.mp3', '.wav', '.ogg']:
                path = os.path.join(ASSETS_DIR, f"{name}_theme{ext}")
                if os.path.exists(path):
                    self.sounds[f"music_{name}"] = arcade.load_sound(path)
                    break

    def play_sound(self, name, volume=1.0):
        """Проиграть короткий звук (SFX)."""
        if name in self.sounds:
            # В Arcade просто вызываем play_sound
            arcade.play_sound(self.sounds[name], volume)

    def play_music(self, track_name, volume=0.5, loop=True):
        """
        Запускает музыку. 
        В Arcade для стриминга музыки мы используем play_sound с loop=True.
        """
        # Сначала остановим то, что играет сейчас
        self.stop_music()

        key = f"music_{track_name}"
        if key in self.sounds:
            music_sound = self.sounds[key]
            # Сохраняем плеер, чтобы потом можно было сделать stop()
            self.current_music_player = arcade.play_sound(music_sound, volume, looping=loop)
        else:
            print(f"Музыка '{track_name}' не найдена!")

    def stop_music(self):
        if self.current_music_player:
            arcade.stop_sound(self.current_music_player)
            self.current_music_player = None

    # --- Геттеры ---
    def get_texture(self, name):
        return self.textures.get(name)