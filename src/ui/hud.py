import pygame
import math

class GameHUD:
    def __init__(self, screen_size):
        self.width, self.height = screen_size
        
        # --- STYLE CONFIG ---
        self.colors = {
            "bg": (149, 98, 53),          # Coklat Panel
            "border": (107, 65, 39),      # Coklat Tua
            "text": (255, 240, 200),      # Cream
            "gold": (255, 215, 0),
            "silver": (192, 192, 192),
            "bronze": (205, 127, 50),
            "bar_bg": (70, 40, 20),       # Background bar (gelap)
            "bar_fill": (100, 255, 50)    # Warna bar (hijau neon)
        }
        
        self.font_big = pygame.font.SysFont(None, 48, bold=True)
        self.font_med = pygame.font.SysFont(None, 32, bold=True)
        self.font_small = pygame.font.SysFont(None, 24)

    def draw_panel(self, surface, rect, border_radius=15):
        """Helper untuk gambar panel coklat rounded"""
        pygame.draw.rect(surface, self.colors['bg'], rect, border_radius=border_radius)
        pygame.draw.rect(surface, self.colors['border'], rect, 4, border_radius=border_radius)

    def render_leaderboard(self, surface, cars):
        """Render Ranking berdasarkan jarak tempuh (Live Rank)."""
        sorted_cars = sorted(cars, key=lambda c: c.distance_traveled, reverse=True)
        
        panel_w, panel_h = 220, 180
        panel_x, panel_y = 20, 20
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        self.draw_panel(surface, rect)
        
        # Title
        title = self.font_med.render("LEADERBOARD", True, self.colors['text'])
        surface.blit(title, title.get_rect(center=(rect.centerx, rect.y + 25)))
        pygame.draw.line(surface, self.colors['border'], (rect.x+10, rect.y+45), (rect.right-10, rect.y+45), 2)
        
        # List
        start_y = rect.y + 60
        for i, car in enumerate(sorted_cars[:5]): # Top 5
            if car.color == "pink": name = "YOU"
            else: name = f"AI ({car.color.title()})"
            
            if i == 0: col = self.colors['gold']
            elif i == 1: col = self.colors['silver']
            elif i == 2: col = self.colors['bronze']
            else: col = self.colors['text']
            
            rank_txt = f"{i+1}."
            name_txt = name
            lap_txt = f"L{car.lap_count}"
            
            y_pos = start_y + (i * 25)
            
            r_surf = self.font_small.render(rank_txt, True, col)
            surface.blit(r_surf, (rect.x + 15, y_pos))
            
            n_surf = self.font_small.render(name_txt, True, (255,255,255) if name=="YOU" else self.colors['text'])
            surface.blit(n_surf, (rect.x + 45, y_pos))
            
            l_surf = self.font_small.render(lap_txt, True, self.colors['text'])
            surface.blit(l_surf, (rect.right - 40, y_pos))

    def render_lap_counter(self, surface, current, total):
        panel_w, panel_h = 150, 80
        rect = pygame.Rect((self.width - panel_w)//2, 20, panel_w, panel_h)
        
        self.draw_panel(surface, rect)
        
        display_lap = min(current, total)
        
        lbl = self.font_small.render("LAP", True, self.colors['text'])
        val = self.font_big.render(f"{display_lap} / {total}", True, self.colors['text'])
        
        surface.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.y + 20)))
        surface.blit(val, val.get_rect(center=(rect.centerx, rect.y + 50)))

    def render_speedometer(self, surface, speed_kmh):
        center_x = self.width - 100
        center_y = self.height - 100
        radius = 80
        
        # 1. Draw Circle Panel (Background)
        pygame.draw.circle(surface, self.colors['bg'], (center_x, center_y), radius)
        pygame.draw.circle(surface, self.colors['border'], (center_x, center_y), radius, 5)
        
        # 2. Text Speed
        spd_surf = self.font_big.render(str(int(abs(speed_kmh))), True, self.colors['text'])
        unit_surf = self.font_small.render("KM/H", True, self.colors['border'])
        
        surface.blit(spd_surf, spd_surf.get_rect(center=(center_x, center_y - 10)))
        surface.blit(unit_surf, unit_surf.get_rect(center=(center_x, center_y + 25)))
        
        # 3. ANIMATED ARC BAR
        # Buat kotak rect untuk arc
        arc_rect = pygame.Rect(center_x-radius+10, center_y-radius+10, (radius-10)*2, (radius-10)*2)
        
        # Hitung rasio kecepatan (Max visual 140 km/h)
        ratio = min(1.0, abs(speed_kmh) / 140)
        
        pygame.draw.arc(surface, self.colors['bar_bg'], arc_rect, 0, math.pi, 15)
        
        if ratio > 0.01:
            
            start_angle = math.pi * (1.0 - ratio)
            stop_angle = math.pi
            
            pygame.draw.arc(surface, self.colors['bar_fill'], arc_rect, start_angle, stop_angle, 15)

    def render_game_over(self, surface, winner_name):
        # 1. Draw Overlay Gelap
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # 2. Draw Panel
        panel_w, panel_h = 600, 300
        rect = pygame.Rect((self.width - panel_w)//2, (self.height - panel_h)//2, panel_w, panel_h)
        self.draw_panel(surface, rect)
        
        # 3. Setup Font & Text Besar
        font_huge = pygame.font.SysFont(None, 80, bold=True)
        
        t1 = font_huge.render("RACE FINISHED!", True, self.colors['text'])
        t2 = self.font_big.render(f"WINNER: {winner_name}", True, self.colors['gold'])
        
        # 4. Positioning (Centered)
        surface.blit(t1, t1.get_rect(center=(rect.centerx, rect.centery - 40)))
        surface.blit(t2, t2.get_rect(center=(rect.centerx, rect.centery + 50)))