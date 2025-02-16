# hover_manager.py
import pygame
import math
from constants import *


class HoverManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('arial', 16)
        self.hovered_person = None

    def is_mouse_over_person(self, mouse_pos, person):
        """Check if mouse is hovering over a person node"""
        dx = mouse_pos[0] - person.pos_x
        dy = mouse_pos[1] - person.pos_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= person.size

    def update(self, people):
        """Update hovered person based on mouse position"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_person = None

        for person in people.values():
            if self.is_mouse_over_person(mouse_pos, person):
                self.hovered_person = person
                break

    def draw(self):
        """Draw RGB values if hovering over a person"""
        if self.hovered_person:
            # Create text with vector values and ID
            vector = self.hovered_person.gene_vector
            flags = ['t' if flag else 'f' for flag in self.hovered_person.bias_flags]
            family = self.hovered_person.family

            vector_text = f"Genes({vector})"
            flags_text = f"Flags({flags})"
            family_text = f"Family({family})"

            vector_surface = self.font.render(vector_text, True, WHITE)
            flags_surface = self.font.render(flags_text, True, WHITE)
            family_text_Surface = self.font.render(family_text, True, WHITE)

            # Position text above the node
            text_x = int(self.hovered_person.pos_x - vector_surface.get_width() // 2)
            text_y = int(self.hovered_person.pos_y - self.hovered_person.size - 40)  # Moved up more for two lines

            # Calculate background rectangle to fit both lines
            padding = 5
            bg_width = max(vector_surface.get_width(), flags_surface.get_width()) + (2 * padding)
            bg_height = vector_surface.get_height() + flags_surface.get_height() + (2 * padding)

            bg_rect = (
                text_x - padding,
                text_y - padding,
                bg_width,
                bg_height
            )

            # Draw background with semi-transparency
            s = pygame.Surface((bg_rect[2], bg_rect[3]))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, (bg_rect[0], bg_rect[1]))

            # Draw both lines of text
            self.screen.blit(vector_surface, (text_x, text_y))
            self.screen.blit(flags_surface, (text_x, text_y + vector_surface.get_height()))
            self.screen.blit(family_text_Surface, (text_x, text_y + (vector_surface.get_height() * 3)))