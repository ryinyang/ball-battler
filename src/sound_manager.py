import pygame
import random

class SoundManager:
    def __init__(self):
        self.initialized = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(64) # Prevent sounds from cutting out
            self.initialized = True
        except pygame.error as e:
            print(f"Warning: Could not initialize sound system. Running without sound. Error: {e}")
        
        self.sounds = {}
        if self.initialized:
            self._load_sounds()

    def _load_sounds(self):
        def load_sound_safe(path):
            try:
                return pygame.mixer.Sound(path)
            except (FileNotFoundError, pygame.error) as e:
                print(f"Warning: Could not load sound asset {path}: {e}")
                return None

        clash = load_sound_safe("assets/clash.mp3")
        if clash:
            self.sounds['clash'] = clash

        hit = load_sound_safe("assets/punch.mp3")
        if hit:
            self.sounds['hit'] = hit
            
        wall_hits = [load_sound_safe(f"assets/wall_hit_{i}.mp3") for i in range(1, 5)]
        wall_hits = [snd for snd in wall_hits if snd is not None]
        if wall_hits:
            self.sounds['wall_hit'] = wall_hits

    def play_sound(self, name):
        if self.initialized and name in self.sounds:
            sound = self.sounds[name]
            if isinstance(sound, list):
                random.choice(sound).play()
            else:
                sound.play()

    def play_clash(self):
        self.play_sound('clash')

    def play_hit(self):
        self.play_sound('hit')

    def play_ball_collision(self):
        # self.play_sound('wall_hit')
        pass

    def play_wall_collision(self):
        self.play_sound('wall_hit')
