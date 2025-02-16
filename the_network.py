import random
import math
import pygame
from person import Person
from constants import *
from utility import handle_color_gene, handle_complex_gene, compute_likelihood
from hover_manager import HoverManager


class TheNetwork:
    def __init__(self, screen):
        self.current = None
        self.path_stack = None
        self.visited_nodes = None
        self.search_initialized = None
        self.screen = screen
        self.phase = "growth"
        self.all_people = {}
        self.can_grow_people = []
        self.scored_nodes = []
        self.hover_manager = HoverManager(screen)
        self.current_top_right_text = None

        # Spatial hash grid
        self.agent_size = 5
        self.cell_size = self.agent_size * 2
        self.max_growth_len = self.agent_size * 2
        self.min_growth_len = self.agent_size * 6

        self.grid_width = WINDOW_WIDTH // self.cell_size
        self.grid_height = WINDOW_HEIGHT // self.cell_size
        self.spatial_grid = {}  # Dictionary for occupied cells
        self.operations = 0
        self.max_people = 300

        # Create Adam
        adam = Person(pos_x=WINDOW_WIDTH // 2, pos_y=WINDOW_HEIGHT // 2, color=RED, id=0, linked_to=None,
                      size=15)

        adam.bias_flags = [random.choice([True, False]) for _ in range(10)]

        self.all_people[0] = adam
        self.can_grow_people.append(adam)

        # Mark Adam's cell as occupied
        cell_x = int(adam.pos_x // self.cell_size)
        cell_y = int(adam.pos_y // self.cell_size)
        self.spatial_grid[(cell_x, cell_y)] = True

        self.growth_timer = 0
        self.find_timer = 0
        self.finding_route = False
        self.current_route = []

    def update(self):
        if self.phase == "growth":
            self.growth_timer += 1
            if self.growth_timer >= 1:
                self.growth_timer = 0
                self.new_person()

            if len(self.all_people) >= self.max_people:
                self.phase = "communication"
            if len(self.can_grow_people) <= 0:
                self.phase = "communication"
        if self.phase == "communication":
            self.draw_top_right_text()
            self.find_timer += 1
            self.communication()

        self.hover_manager.update(self.all_people)

        self.draw_people()
        self.draw_operations()

        self.hover_manager.draw()

    def new_person(self):
        if not self.can_grow_people:
            self.phase = "communication"
            return

        parent = random.choice(self.can_grow_people)
        self.can_grow_people.remove(parent)
        parent.can_grow = False

        num_children = random.randint(1, 10)

        for _ in range(num_children):
            self.operations += 1
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.min_growth_len, self.max_growth_len)

            new_x = parent.pos_x + math.cos(angle) * distance
            new_y = parent.pos_y + math.sin(angle) * distance

            # Check boundaries
            if not (0 <= new_x <= WINDOW_WIDTH and 0 <= new_y <= WINDOW_HEIGHT):
                continue

            if self.is_position_free(new_x, new_y):
                self.operations += 1
                new_id = len(self.all_people)

                new_genes, bias_flags, new_family, new_family_anchor = handle_complex_gene(parent)
                r, g, b = handle_color_gene(new_genes, bias_flags)

                new_person = Person(
                    pos_x=new_x,
                    pos_y=new_y,
                    color=(r, g, b),
                    parent_id=parent.id,
                    id=new_id,
                    linked_to=parent.id,
                    size=self.agent_size,
                    gene_vector=new_genes,
                    bias_flags=bias_flags,
                    family=new_family,
                    family_anchor=new_family_anchor
                )

                parent.linked_to.add(new_id)
                self.all_people[new_id] = new_person
                self.can_grow_people.append(new_person)

                # Mark the new position in the spatial grid
                cell_x = int(new_x // self.cell_size)
                cell_y = int(new_y // self.cell_size)
                self.spatial_grid[(cell_x, cell_y)] = True

    def is_position_free(self, x, y):
        self.operations += 1  # Grid lookup is an operation
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (cell_x + dx, cell_y + dy) in self.spatial_grid:
                    return False
        return True

    def communication(self):

        if not hasattr(self, 'current_start') or not hasattr(self, 'current_target'):
            print("Starting new communication phase")
            # Initialize new search
            # self.current_start = random.choice(list(self.all_people.values()))
            self.current_start = self.all_people[0]
            self.current_target = random.choice(list(self.all_people.values()))

            # Make sure start and target are different
            while self.current_target.id == self.current_start.id:
                self.current_target = random.choice(list(self.all_people.values()))

            print(f"Selected start: {self.current_start.id}, target: {self.current_target.id}")

            # Reset search state
            if hasattr(self, 'search_initialized'):
                delattr(self, 'search_initialized')

            self.current_start.color = WHITE
            self.current_start.size = 15
            self.current_target.color = WHITE
            self.current_target.size = 15

        # Continue existing search
        self.genetic_search(self.current_start, self.current_target)

        # Check if search is complete
        if not self.finding_route:
            print("Search complete!")
            self.phase = "none"
            delattr(self, 'current_start')
            delattr(self, 'current_target')
            if hasattr(self, 'search_initialized'):
                delattr(self, 'search_initialized')
            return

    def genetic_search(self, start, target):
        # Initialize search
        if not hasattr(self, 'search_initialized'):
            self.finding_route = True
            self.current_route = [(start.pos_x, start.pos_y)]
            self.current = start
            self.path_stack = [start]
            self.visited_nodes = {start.id}
            self.search_initialized = True

        if self.find_timer < 45:
            return

        self.find_timer = 0

        linked_nodes_ids = self.current.linked_to - {self.current.parent_id}
        self.visited_nodes.add(self.current.id)
        nodes_to_evaluate = []
        score = 0
        next_node = None

        # Only break into evaluation if the node even has children, otherwise go pack to the parent.
        # Also, if we are backtracking we don't want to break back into evaluation.
        if self.current.linked_to:
            linked_nodes_ids = linked_nodes_ids - self.visited_nodes
            if linked_nodes_ids:
                for node_id in linked_nodes_ids:
                    node = self.all_people[node_id]
                    family_difference, drift_p, vector_difference, downstream = compute_likelihood(node, target)

                    score += vector_difference
                    score += family_difference * 4000

                    nodes_to_evaluate.append((node_id, score, drift_p))

            if nodes_to_evaluate:
                best_node = min(nodes_to_evaluate, key=lambda x: x[1])
                if best_node[2] >= 4 or best_node[1] > 32000:
                    next_node = self.all_people[self.current.parent_id]
                    self.current_route.remove((self.current.pos_x, self.current.pos_y))
                else:
                    next_node = self.all_people[best_node[0]]  # <-- Pick the best node
            else:
                next_node = self.all_people[self.current.parent_id]
                self.current_route.remove((self.current.pos_x, self.current.pos_y))
        else:
            next_node = self.all_people[self.current.parent_id]
            self.current_route.remove((self.current.pos_x, self.current.pos_y))

        self.current = next_node
        self.current_route.append((self.current.pos_x, self.current.pos_y))

    def draw_people(self):
        # Draw links first
        for person in self.all_people.values():
            for linked_id in person.linked_to:
                linked_person = self.all_people[linked_id]
                pygame.draw.line(
                    self.screen,
                    (128, 128, 128),
                    (int(person.pos_x), int(person.pos_y)),
                    (int(linked_person.pos_x), int(linked_person.pos_y)),
                    1
                )

        # Draw current exploration route
        if hasattr(self, 'current_route') and self.current_route:
            for i in range(len(self.current_route) - 1):
                pygame.draw.line(
                    self.screen,
                    YELLOW,
                    self.current_route[i],
                    self.current_route[i + 1],
                    3
                )

        # Draw people
        for person in self.all_people.values():
            pygame.draw.circle(
                self.screen,
                person.color,
                (int(person.pos_x), int(person.pos_y)),
                person.size
            )

    def draw_operations(self):
        font = pygame.font.SysFont('arial', 24)
        text = font.render(f'Operations: {self.operations}, phase: {self.phase}, total agents:{len(self.all_people)}',
                           True, RED)
        self.screen.blit(text, (10, 10))

    def draw_top_right_text(self):
        font = pygame.font.SysFont('arial', 24)
        text_surface = font.render(self.current_top_right_text, True, (255, 255, 255))  # White text

        # Position in top right with some padding
        padding = 10
        text_x = WINDOW_WIDTH - text_surface.get_width() - padding
        text_y = padding

        # Draw background box
        padding_box = 5
        bg_rect = (
            text_x - padding_box,
            text_y - padding_box,
            text_surface.get_width() + (2 * padding_box),
            text_surface.get_height() + (2 * padding_box)
        )

        # Semi-transparent black background
        s = pygame.Surface((bg_rect[2], bg_rect[3]))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, (bg_rect[0], bg_rect[1]))

        # Draw text
        self.screen.blit(text_surface, (text_x, text_y))
