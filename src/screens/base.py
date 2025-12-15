import pygame

class ScreenBase:
    def __init__(self, manager, screen_size):
        self.manager = manager
        self.screen_width, self.screen_height = screen_size

    def handle_event(self, event):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError