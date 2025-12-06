"""
This module handles:
Fullscreen visual interface for TARS 
- The Matrix screen effect
- Displaying transcribed text from speech recognition & Live speech feedback while speaking

You can see an example of how the Matrix animation works here:
https://www.youtube.com/watch?v=L21_CCGxhaE

Usage Notes:
If you run this module separately, you will see the Matrix effect on screen.

Controls:
Press ESC to exit.
Requirements:
pip install pygame

Copyright (c) 2025 Yassine Labiade
Licensed under the MIT License.
"""
import pygame # Main graphics library pip install it
import random
import sys
import time
import textwrap



# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

pygame.init()
# Screen setup
#WIDTH, HEIGHT = 800, 600
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h  # Get screen size
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) #FULLSCREEN
pygame.display.set_caption("TARS Matrix Display")
clock = pygame.time.Clock()
font_size = int(HEIGHT * 0.03)  # responsive font sizing
font = pygame.font.SysFont("Consolas", font_size, bold=True)
# Matrix Rain Effect
# Matrix setup
columns = WIDTH // font_size
drops = [random.randint(-20, 0) for _ in range(columns)]

def draw_matrix():
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 15))
    screen.blit(surface, (0, 0))

    for i in range(columns):
        char = chr(random.randint(33, 126))
        text = font.render(char, True, GREEN)
        x = i * font_size
        y = drops[i] * font_size

        screen.blit(text, (x, y))
        drops[i] += 1
        if y > HEIGHT and random.random() > 0.975:
            drops[i] = 0

def render_multiline_text(text, x, y, color=WHITE, max_width=WIDTH - 100, line_spacing=5):
    lines = textwrap.wrap(text, width=int(max_width / (font_size * 0.6)))
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x, y + i * (font_size + line_spacing)))

def run_display(transcribed_text=None, duration=5):
    running = True
    showing_text = transcribed_text is not None
    start_time = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        if showing_text:
            screen.fill(BLACK)
            render_multiline_text(transcribed_text, 50, 50)
            pygame.display.flip()

            if pygame.time.get_ticks() - start_time > duration * 1000:
                running = False
        else:
            draw_matrix()
            pygame.display.flip()
            clock.tick(FPS)

def run_live_text_black_screen(get_live_text, final_text_container, is_listening_func):
    running = True
    clock = pygame.time.Clock()
    showing_final = False
    final_start_time = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)

        if is_listening_func():
            live_text = get_live_text()
            if live_text:
                render_multiline_text(live_text, 50, HEIGHT // 3)
        else:
            if not showing_final:
                final_start_time = pygame.time.get_ticks()
                showing_final = True

            final_text = final_text_container[0] if final_text_container else ""
            render_multiline_text(final_text, 50, 50)

            if pygame.time.get_ticks() - final_start_time > 2000:
                running = False

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_display()
