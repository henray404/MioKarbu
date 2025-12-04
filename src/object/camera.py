import pygame

camera = pygame.Rect(0, 0, 0, 0)
camera_target_x = 0
camera_target_y = 0

def create_screen(width, height, title="Mio-Mber"):
    pygame.display.set_caption(title)
    
    screen = pygame.display.set_mode((width, height))
    camera.width = width
    camera.height = height
    return screen

def update_camera(target_x, target_y, map_width, map_height):
    """Update posisi kamera untuk mengikuti target dengan smooth interpolation"""
    global camera_target_x, camera_target_y
    
    # Zoom factor - lebih kecil = lebih zoom in
    zoom_offset = 50  # Zoom lebih dekat ke motor (dari 150 jadi 50)
    
    # Target kamera dengan zoom adjustment
    camera_target_x = target_x - (camera.width // 2) + zoom_offset
    camera_target_y = target_y - (camera.height // 2) + zoom_offset
    
    # Smooth camera follow (lerp)
    smoothness = 0.15  # Sedikit lebih responsif (dari 0.1 jadi 0.15)
    camera.x += (camera_target_x - camera.x) * smoothness
    camera.y += (camera_target_y - camera.y) * smoothness
    
    # Batasi kamera agar tidak keluar dari map
    camera.x = max(0, min(camera.x, map_width - camera.width))
    camera.y = max(0, min(camera.y, map_height - camera.height))