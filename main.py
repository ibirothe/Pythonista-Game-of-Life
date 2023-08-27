from scene import *
import random

MAP_SIZE = (17, 29)

UPDATE_RATE = 4

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

class GameOfLife:
    """Class representing the Game of Life logic."""
    def __init__(self):
        self.living = False
        self.lifeframe = 0
        self.board_size = MAP_SIZE
        self.map = [[0 for _ in range(self.board_size[0])] for _ in range(self.board_size[1])]
        self.tiles = []

    def reset_board(self):
        self.map = [[0 for _ in range(self.board_size[0])] for _ in range(self.board_size[1])]

    def toggle_living(self):
        self.living = not self.living

    def touch_tile(self, x, y):
        self.map[y][x] = 0 if self.map[y][x] == 1 else 1

    def update_map(self):
        new_map = []
        for i, row in enumerate(self.map):
            new_row = []
            for j, cell in enumerate(row):
                neighbors = sum(self.map[(i + d[0]) % self.board_size[1]][(j + d[1]) % self.board_size[0]] == 1 for d in DIRECTIONS)
                new_row.append(1 if (cell == 1 and 1 < neighbors < 4) or (cell == 0 and neighbors == 3) else 0)
            new_map.append(new_row)
        self.map = new_map

class Button(ShapeNode):
    """Class representing a button."""
    def __init__(self, rect, fill_color, action, *args, **kwargs):
        super().__init__(rect, fill_color=fill_color, *args, **kwargs)
        self.anchor_point = (0.5, 0.5)
        self.action = action

class GameScene(Scene):
    """Class representing the scene."""
    def setup(self):
        self.game = GameOfLife()
        self.grey = self.get_gray_color()
        self.setup_buttons()
        self.setup_tiles()

    def setup_buttons(self):
        self.clear_buttons = Node(parent=self)
        self.play_buttons = Node(parent=self)
        self.step_buttons = Node(parent=self)
        self.labels = Node(parent=self)
        
        num_buttons = 4
        button_width = TILE_SIZE * 3
        total_button_width = button_width * num_buttons
        total_spacing = min(get_screen_size()) - total_button_width

        space_between_buttons = total_spacing / (num_buttons + 1)
    
        for i in range(num_buttons):
            x_pos = (button_width / 2) + (space_between_buttons * (i + 1)) + (button_width * i)
            if i == 0:
                self.add_button(self.play_buttons, "#c53636", x_pos, 35, self.toggle_play, "play")
            elif i == 1:
                self.add_button(self.clear_buttons, "#9faaa5", x_pos, 35, self.reset_board, "clear")
            elif i == 2:
                self.add_button(self.step_buttons, "#b6cb9a", x_pos, 35, self.update_map, "step")
            elif i == 3:
                self.add_button(self.step_buttons, "#cb8cc2", x_pos, 35, self.randomize_map, "rng")

    def add_button(self, parent, fill_color, x, y, action, text):
        button_rect = ui.Path.rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 2)
        button = Button(button_rect, fill_color, action)
        label = LabelNode(text, ("Helvetica", 20))
        label.anchor_point = (0.5, 0.5)
        label.position = (x, y)
        button.position = (x, y)
        parent.add_child(button)
        self.labels.add_child(label)

    def toggle_play(self):
        self.game.toggle_living()
        fill_color = "#649464" if self.game.living else "#c53636"
        for button in self.play_buttons.children:
            button.fill_color = fill_color

    def reset_board(self):
        self.game.reset_board()

    def update_map(self):
        self.game.update_map()

    def randomize_map(self):
        living_cells = self.count_living_tiles()
        dead_cells = MAP_SIZE[0] * MAP_SIZE[1] - living_cells
        for i in range(self.game.board_size[1]):
            for j in range(self.game.board_size[0]):
                self.game.map[i][j] = random.choices([0, 1], weights=[dead_cells, living_cells])[0]

    def setup_tiles(self):
        for y in range(self.game.board_size[1]):
            for x in range(self.game.board_size[0]):
                self.add_tile(x * TILE_SIZE, 70 + y * TILE_SIZE)

    def add_tile(self, x, y):
        tile = ShapeNode(ui.Path.rect(0, 0, TILE_SIZE, TILE_SIZE), fill_color="black", stroke_color="#191819")
        tile.anchor_point = (0, 0)
        tile.position = (x, y)
        self.game.tiles.append(tile)
        self.add_child(tile)

    def update(self):
        self.grey = self.get_gray_color()
        if self.game.living:
            self.game.lifeframe += 1
            if self.game.lifeframe == UPDATE_RATE:
                self.game.lifeframe = 0
                self.game.update_map()

        for y, row in enumerate(self.game.map):
            for x, cell in enumerate(row):
                tile_index = y * self.game.board_size[0] + x
                tile = self.game.tiles[tile_index]
                tile.fill_color = self.grey if cell == 1 else "black"

    def count_living_tiles(self):
        return sum(row.count(1) for row in self.game.map)

    def rgb_to_hex(self, rgb_tuple):
        hex_color = "#{:02X}{:02X}{:02X}".format(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        return hex_color

    def get_gray_color(self):
        living_tile_count = self.count_living_tiles()
        division_result = living_tile_count / (MAP_SIZE[0] * MAP_SIZE[1])
        gray_value = min(255, int(division_result * 500) + 30)
        color = (gray_value, gray_value, gray_value)
        hex_color = self.rgb_to_hex(color)
        return hex_color

    def touch_began(self, touch):
        for button in self.clear_buttons.children:
            if touch.location in button.bbox:
                button.action()

        for button in self.play_buttons.children:
            if touch.location in button.bbox:
                button.action()

        for button in self.step_buttons.children:
            if touch.location in button.bbox:
                button.action()

        self.check_tile_touch(touch)

    def touch_moved(self, touch):
        self.check_tile_touch(touch)

    def check_tile_touch(self, touch):
        for tile in self.game.tiles:
            if touch.location in tile.bbox:
                tile_index = self.game.tiles.index(tile)
                y = tile_index // self.game.board_size[0]
                x = tile_index % self.game.board_size[0]
                self.game.touch_tile(x, y)
                tile.fill_color = "black" if self.game.map[y][x] == 0 else "white"

if __name__ == '__main__':
    TILE_SIZE = min(get_screen_size()) // MAP_SIZE[0]
    run(GameScene(), PORTRAIT)
