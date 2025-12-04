import sys
from typing import List, Protocol, Optional

import pygame


class UpdatableDrawable(Protocol):
    def update(self, *args, **kwargs) -> None: ...
    def draw(self, screen: pygame.Surface) -> None: ...


class GameManager:
    """
    Mengatur game loop utama.

    - Encapsulation: menyembunyikan detail loop
    - Composition: memiliki (has-a) list entity
    - Polymorphism: entity cukup punya update() & draw()
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Tabrak Bahlil",
        fps: int = 60,
        bg_color: tuple[int, int, int] = (0, 0, 0),
        show_fps: bool = True,
    ) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.fps_target: int = fps
        self.running: bool = False

        self.bg_color = bg_color
        self.show_fps = show_fps
        self.entities: List[UpdatableDrawable] = []
        self.static_drawables: List[UpdatableDrawable] = []  # e.g., walls wrapper if needed

        # Optional: preload font for FPS
        self._font: Optional[pygame.font.Font] = None
        if self.show_fps:
            try:
                self._font = pygame.font.SysFont("consolas", 16)
            except Exception:
                self._font = pygame.font.Font(None, 16)

    def add_entity(self, entity: UpdatableDrawable) -> None:
        self.entities.append(entity)

    def add_static(self, drawable: UpdatableDrawable) -> None:
        self.static_drawables.append(drawable)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self, *args, **kwargs) -> None:
        for ent in self.entities:
            # Entity bebas menggunakan *args seperti walls dsb.
            ent.update(*args, **kwargs)

    def draw(self) -> None:
        self.screen.fill(self.bg_color)
        for drawable in self.static_drawables:
            drawable.draw(self.screen)
        for ent in self.entities:
            ent.draw(self.screen)

        if self.show_fps and self._font:
            fps_text = self._font.render(f"FPS: {int(self.clock.get_fps())}", True, (0, 255, 0))
            self.screen.blit(fps_text, (8, 8))

        pygame.display.flip()

    def run(self, update_args: tuple = (), update_kwargs: dict | None = None) -> None:
        self.running = True
        update_kwargs = update_kwargs or {}

        while self.running:
            dt_ms = self.clock.tick(self.fps_target)
            self.handle_events()
            self.update(*update_args, **update_kwargs)
            self.draw()

        pygame.quit()
        # Exit gracefully if GameManager created its own window in a top-level run
        if __name__ == "__main__":
            sys.exit(0)
