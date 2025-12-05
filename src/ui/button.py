import pygame

class Button:
    def __init__(self, text, position, size, callback, font):
        self.text = text
        self.position = position
        self.size = size
        self.callback = callback
        self.font = font

        self.rect = pygame.Rect(position, size)
        self.color_idle = (70, 70, 70)
        self.color_hover = (100, 100, 100)
        self.color_active = (150, 150, 150)
        self.current_color = self.color_idle

        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.text_position = (text_rect.x, text_rect.y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.color_hover
            else:
                self.current_color = self.color_idle
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.current_color = self.color_active
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                self.current_color = self.color_hover

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        surface.blit(self.text_surf, self.text_position)