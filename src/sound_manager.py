import pygame

class SoundManager:
    def __init__(self):
        self.initialized = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.initialized = True
        except pygame.error as e:
            print(f"Warning: Could not initialize sound system. Running without sound. Error: {e}")
        
        self.sounds = {}
        if self.initialized:
            self._load_sounds()

    def _load_sounds(self):
        # TODO: Load actual sound assets here
        # self.sounds['clash'] = pygame.mixer.Sound("assets/sounds/clash.wav")
        # self.sounds['hit'] = pygame.mixer.Sound("assets/sounds/hit.wav")
        # self.sounds['ball_hit'] = pygame.mixer.Sound("assets/sounds/ball_hit.wav")
        # self.sounds['wall_hit'] = pygame.mixer.Sound("assets/sounds/wall_hit.wav")
        pass

    def play_sound(self, name):
        if self.initialized and name in self.sounds:
            self.sounds[name].play()

    def play_clash(self):
        self.play_sound('clash')

    def play_hit(self):
        self.play_sound('hit')

    def play_ball_collision(self):
        self.play_sound('ball_hit')

    def play_wall_collision(self):
        self.play_sound('wall_hit')
