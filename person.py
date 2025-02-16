import pygame
import random
import math


class Person:
    def __init__(self, pos_x, pos_y, color, id, linked_to, size,
                 gene_vector=None, bias_flags=None, family=0, family_anchor=None,parent_id=None):
        # Existing attributes
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size = size
        self.color = color
        self.id = id
        self.linked_to = set()
        self.parent_id = parent_id
        self.can_grow = True
        self.family = family
        self.gene_vector = gene_vector or [0] * 10
        self.bias_flags = bias_flags or [True] * 10
        self.family_anchor = family_anchor or self.gene_vector.copy()

        if gene_vector is None:
            self.gene_vector = [0 for _ in range(10)]
        else:
            self.gene_vector = gene_vector

        if bias_flags is None:
            self.bias_flags = [random.choice([True, False]) for _ in range(10)]
        else:
            self.bias_flags = bias_flags

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.pos_x, self.pos_y), self.size)
