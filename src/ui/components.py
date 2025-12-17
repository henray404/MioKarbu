import pygame

class UIComponent:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 0, 0)
        self.is_visible = True

    def draw(self, surface):
        pass

class HoverButton(UIComponent):
    """
    Tombol dengan fitur Base Scale (ukuran asli) dan Hover Scale (efek zoom).
    """
    def __init__(self, x, y, image_path, base_scale=1.0, hover_scale=1.1):
        super().__init__(x, y)
        
        # 1. Load Gambar Original
        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print(f"ERROR: Gambar tidak ditemukan di {image_path}")
            raw_image = pygame.Surface((100, 50))
            raw_image.fill((255, 0, 0))

        # 2. Terapkan Base Scale (Resize ukuran asli tombol)
        w, h = raw_image.get_size()
        new_w = int(w * base_scale)
        new_h = int(h * base_scale)
        self.image = pygame.transform.smoothscale(raw_image, (new_w, new_h))
        
        # Set Rect berdasarkan ukuran baru, posisi CENTER di (x, y)
        self.rect = self.image.get_rect(center=(x, y))
        
        # 3. Generate Gambar Hover (Zoom dari ukuran base)
        hover_w = int(new_w * hover_scale)
        hover_h = int(new_h * hover_scale)
        self.hover_image = pygame.transform.smoothscale(self.image, (hover_w, hover_h))
        self.hover_rect = self.hover_image.get_rect(center=(x, y))
        
        self.is_hovered = False

    def draw(self, surface):
        if not self.is_visible: return
        
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered:
            surface.blit(self.hover_image, self.hover_rect)
        else:
            surface.blit(self.image, self.rect)

    def is_clicked(self, event):
        if self.is_visible and self.is_hovered:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return True
        return False


class SettingsPopup(UIComponent):
    # ... (Kode SettingsPopup SAMA PERSIS seperti sebelumnya, tidak perlu diubah) ...
    def __init__(self, screen_size, max_volume=0.4, curr_volume=0.2):
        sw, sh = screen_size
        panel_w, panel_h = 600, 400
        x = (sw - panel_w) // 2
        y = (sh - panel_h) // 2
        
        super().__init__(x, y)
        
        self.rect = pygame.Rect(x, y, panel_w, panel_h)
        self.max_vol = max_volume
        self.curr_vol = curr_volume
        self.is_dragging = False
        
        self.slider_track = pygame.Rect(0, 0, 400, 20)
        self.slider_track.center = (self.rect.centerx, self.rect.centery + 20)
        
        self.slider_knob = pygame.Rect(0, 0, 30, 40)
        self._sync_knob_position()
        
        self.btn_close = pygame.Rect(self.rect.right - 50, self.rect.top + 15, 35, 35)
        
        self.font_title = pygame.font.SysFont(None, 64, bold=True)
        self.font_ui = pygame.font.SysFont(None, 36)

    def _sync_knob_position(self):
        ratio = self.curr_vol / self.max_vol
        fill_width = int(self.slider_track.width * ratio)
        self.slider_knob.center = (self.slider_track.x + fill_width, self.slider_track.centery)

    def _update_volume_from_mouse(self, mouse_x):
        rel_x = mouse_x - self.slider_track.x
        ratio = max(0.0, min(1.0, rel_x / self.slider_track.width))
        self.curr_vol = ratio * self.max_vol
        pygame.mixer.music.set_volume(self.curr_vol)
        self._sync_knob_position()

    def handle_event(self, event):
        if not self.is_visible: return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_close.collidepoint(mouse_pos):
                return True
            
            if self.slider_track.collidepoint(mouse_pos) or self.slider_knob.collidepoint(mouse_pos):
                self.is_dragging = True
                self._update_volume_from_mouse(mouse_pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self._update_volume_from_mouse(mouse_pos[0])
            
        return False

    def draw(self, surface):
        if not self.is_visible: return

        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        bg_col, border_col = (149, 98, 53), (107, 65, 39)
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=20)
        pygame.draw.rect(surface, border_col, self.rect, 8, border_radius=20)

        shadow = self.font_title.render("MUSIC VOLUME", True, border_col)
        title = self.font_title.render("MUSIC VOLUME", True, (255, 240, 200))
        surface.blit(shadow, shadow.get_rect(center=(self.rect.centerx+3, self.rect.top+73)))
        surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top+70)))

        pygame.draw.rect(surface, (90, 50, 30), self.slider_track, border_radius=10)
        fill_w = int(self.slider_track.width * (self.curr_vol / self.max_vol))
        fill_rect = pygame.Rect(self.slider_track.x, self.slider_track.y, fill_w, self.slider_track.height)
        pygame.draw.rect(surface, (100, 220, 50), fill_rect, border_radius=10)

        pygame.draw.rect(surface, (240, 240, 240), self.slider_knob, border_radius=15)
        pygame.draw.rect(surface, border_col, self.slider_knob, 3, border_radius=15)

        # Hitung dulu (dikali 100), baru diformat jadi integer (.0f)
        txt = f"{(self.curr_vol / self.max_vol) * 100:.0f}%"
        txt_surf = self.font_ui.render(txt, True, (255, 255, 255))
        surface.blit(txt_surf, txt_surf.get_rect(center=(self.rect.centerx, self.slider_track.bottom + 40)))

        pygame.draw.rect(surface, (220, 60, 60), self.btn_close, border_radius=10)
        pygame.draw.rect(surface, (150, 30, 30), self.btn_close, 3, border_radius=10)
        x_surf = self.font_ui.render("X", True, (255, 255, 255))
        surface.blit(x_surf, x_surf.get_rect(center=self.btn_close.center))
    
class PausePopup(UIComponent):
    """
    Popup Menu saat tombol ESC ditekan
    """
    def __init__(self, screen_size):
        sw, sh = screen_size
        panel_w, panel_h = 400, 450
        x = (sw - panel_w) // 2
        y = (sh - panel_h) // 2
        super().__init__(x, y)
        
        self.rect = pygame.Rect(x, y, panel_w, panel_h)
        self.action = None  # "RESUME", "RETRY", "EXIT"
        
        # Font
        self.font_title = pygame.font.SysFont(None, 64, bold=True)
        self.font_btn = pygame.font.SysFont(None, 48, bold=True)
        
        # Layout Tombol
        btn_w, btn_h = 250, 60
        cx = self.rect.centerx - (btn_w // 2)
        start_y = self.rect.y + 130
        
        self.btn_resume = pygame.Rect(cx, start_y, btn_w, btn_h)
        self.btn_retry = pygame.Rect(cx, start_y + 90, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx, start_y + 180, btn_w, btn_h)

    def handle_event(self, event):
        if not self.is_visible: return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mp = pygame.mouse.get_pos()
            if self.btn_resume.collidepoint(mp):
                self.action = "RESUME"
                return True
            elif self.btn_retry.collidepoint(mp):
                self.action = "RETRY"
                return True
            elif self.btn_exit.collidepoint(mp):
                self.action = "EXIT"
                return True
        return False

    def draw(self, surface):
        if not self.is_visible: return

        # 1. Overlay Gelap
        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # 2. Background Panel (Style Kayu)
        pygame.draw.rect(surface, (149, 98, 53), self.rect, border_radius=20)
        pygame.draw.rect(surface, (107, 65, 39), self.rect, 8, border_radius=20)

        # 3. Judul
        title = self.font_title.render("PAUSED", True, (255, 240, 200))
        surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.y + 60)))

        # 4. Helper Gambar Tombol
        def draw_btn(rect, text, color):
            mp = pygame.mouse.get_pos()
            col = color if not rect.collidepoint(mp) else (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30))
            pygame.draw.rect(surface, col, rect, border_radius=15)
            pygame.draw.rect(surface, (107, 65, 39), rect, 4, border_radius=15)
            txt = self.font_btn.render(text, True, (255, 255, 255))
            surface.blit(txt, txt.get_rect(center=rect.center))

        draw_btn(self.btn_resume, "RESUME", (100, 220, 50))
        draw_btn(self.btn_retry, "RETRY", (220, 160, 40))
        draw_btn(self.btn_exit, "EXIT", (200, 50, 50))