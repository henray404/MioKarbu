import pygame
import os
from .base import ScreenBase
from ui.components import HoverButton

class PickMapScreen(ScreenBase):
    def __init__(self, manager, screen_size, asset_root):
        super().__init__(manager, screen_size)
        self.asset_root = asset_root
        self.selected_map = None  # Akan berisi string nama map (misal: 'track-1')
        self.finished = False
        
        # --- STYLE CONFIG (Wood/Brown Theme) ---
        self.colors = {
            "bg_panel": (149, 98, 53),
            "border": (107, 65, 39),
            "text_light": (255, 240, 200),
            "text_shadow": (107, 65, 39),
            "highlight": (100, 220, 50)
        }
        
        # --- FONTS ---
        self.font_title = pygame.font.SysFont(None, 64, bold=True)
        self.font_label = pygame.font.SysFont(None, 36, bold=True)

        # --- BACKGROUND ---
        # Kita pakai background lobby yang digelapkan sedikit
        bg_path = os.path.join(asset_root, "ui", "lobby-2.png")
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, screen_size)
        self.overlay = pygame.Surface(screen_size)
        self.overlay.set_alpha(150)
        self.overlay.fill((0, 0, 0))

        # --- MAP CARDS CONFIG ---
        sw, sh = screen_size
        card_w, card_h = 400, 300
        gap = 50
        
        # Posisi Card
        start_x = (sw - (card_w * 2 + gap)) // 2
        card_y = (sh - card_h) // 2
        
        # Map 1 Data
        self.rect_map1 = pygame.Rect(start_x, card_y, card_w, card_h)
        self.img_map1 = self._load_map_thumb("map-2.png", (card_w - 20, card_h - 60))
        
        # Map 2 Data
        self.rect_map2 = pygame.Rect(start_x + card_w + gap, card_y, card_w, card_h)
        self.img_map2 = self._load_map_thumb("new-4.png", (card_w - 20, card_h - 60))

        # Button Start
        self.btn_start = HoverButton(
            sw // 2, card_y + card_h + 80,
            os.path.join(asset_root, "ui", "btn-play.png"),
            base_scale=1.0
        )
        self.btn_start.is_visible = False # Sembunyikan sampai map dipilih

        self.current_selection = None # 'map1' atau 'map2'

    def _load_map_thumb(self, filename, size):
        path = os.path.join(self.asset_root, "tracks", filename) # Asumsi folder tracks
        try:
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, size)
        except:
            # Fallback jika gambar map belum ada
            surf = pygame.Surface(size)
            surf.fill((50, 50, 50))
            return surf

    def handle_event(self, event):
        if self.btn_start.is_clicked(event):
            if self.current_selection:
                self.selected_map = self.current_selection
                self.finished = True
        
        # Handle Map Selection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect_map1.collidepoint(mouse_pos):
                self.current_selection = "map-2" # Value yg dikirim ke main
                self.btn_start.is_visible = True
            elif self.rect_map2.collidepoint(mouse_pos):
                self.current_selection = "new-4" # Value yg dikirim ke main
                self.btn_start.is_visible = True

    def update(self, dt):
        pass

    def draw(self, surface):
        # 1. Background
        surface.blit(self.bg, (0, 0))
        surface.blit(self.overlay, (0, 0))
        
        # 2. Title
        title_surf = self.font_title.render("SELECT TRACK", True, self.colors['text_light'])
        shadow_surf = self.font_title.render("SELECT TRACK", True, self.colors['text_shadow'])
        title_rect = title_surf.get_rect(center=(surface.get_width() // 2, self.rect_map1.top - 80))
        surface.blit(shadow_surf, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title_surf, title_rect)

        # 3. Draw Cards
        self._draw_card(surface, self.rect_map1, self.img_map1, "CIRCUIT 1", self.current_selection == "map-2")
        self._draw_card(surface, self.rect_map2, self.img_map2, "CIRCUIT 2", self.current_selection == "new-4")

        # 4. Start Button
        if self.btn_start.is_visible:
            self.btn_start.draw(surface)

    def _draw_card(self, surface, rect, image, label_text, is_selected):
        # Config warna
        bg_col = self.colors['bg_panel']
        border_col = self.colors['highlight'] if is_selected else self.colors['border']
        border_width = 8 if is_selected else 4
        
        # Panel Background
        pygame.draw.rect(surface, bg_col, rect, border_radius=15)
        
        # Image
        img_rect = image.get_rect(center=(rect.centerx, rect.centery - 15))
        surface.blit(image, img_rect)
        pygame.draw.rect(surface, (0,0,0), img_rect, 2) # Border tipis gambar
        
        # Label
        txt_surf = self.font_label.render(label_text, True, self.colors['text_light'])
        surface.blit(txt_surf, txt_surf.get_rect(center=(rect.centerx, rect.bottom - 25)))
        
        # Main Border
        pygame.draw.rect(surface, border_col, rect, border_width, border_radius=15)