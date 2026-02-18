from random import Random
from typing import List, Tuple, Dict, NamedTuple

# 壁ビット
NORTH: int = 0b0001
EAST: int = 0b0010
SOUTH: int = 0b0100
WEST: int = 0b1000


class Direction(NamedTuple):
    x: int
    y: int
    wall: int
    opposite: int


DIRECTIONS: Dict[str, Direction] = {
    "to_north": Direction(0, -1, NORTH, SOUTH),
    "to_east": Direction(1, 0, EAST, WEST),
    "to_south": Direction(0, 1, SOUTH, NORTH),
    "to_west": Direction(-1, 0, WEST, EAST)
}


class MazeGenerator:
    """
    迷路生成クラス（ボーナスのため、何種類か記載したいんご）
    """
    def __init__(self) -> None:
        self.width: int = 20
        self.height: int = 15
        self.entry: Tuple[int, int] = (0, 0)
        self.exit: Tuple[int, int] = (19, 14)
        self.perfect: bool = True
        self.rng: Random = Random(12431421)
        self.forty_two: set[Tuple[int, int]] = self._build_forty_two()
        self.grid: List[List[int]] = [[
            0b1111 for _ in range(self.width)] for _ in range(self.height)]

    # ==============================
    # 迷路生成（DFS）
    # ==============================
    def generate_dfs(self) -> List[List[int]]:
        self.grid: List[List[int]] = [[
            0b1111 for _ in range(self.width)] for _ in range(self.height)]
        visited: List[List[bool]] = [[
            False for _ in range(self.width)] for _ in range(self.height)]
        for (x, y) in self.forty_two:
            visited[y][x] = True

        def dfs(x: int, y: int) -> None:
            visited[y][x] = True
            directions: List[Direction] = list(DIRECTIONS.values())
            self.rng.shuffle(directions)
            d: Direction
            for d in directions:
                next_x: int = x + d.x
                next_y: int = y + d.y
                if 0 <= next_x < self.width and 0 <= next_y < self.height:
                    if not visited[next_y][next_x]:
                        mask_wall: int = (~d.wall) & 0b1111
                        mask_opposite: int = (~d.opposite) & 0b1111
                        self.grid[y][x] &= mask_wall
                        self.grid[next_y][next_x] &= mask_opposite
                        dfs(next_x, next_y)
        if (self.entry[0], self.entry[1]) in self.forty_two:
            raise ValueError
        if (self.exit[0], self.exit[1]) in self.forty_two:
            raise ValueError
        dfs(self.entry[0], self.entry[1])
        if not self.perfect:
            self._add_extra_connection()
        return self.grid

    # ==============================
    # 不完全迷路生成
    # ==============================
    def _add_extra_connection(self, probability: float = 0.05) -> None:
        for y in range(self.height):
            for x in range(self.width):
                for d in (DIRECTIONS["to_east"], DIRECTIONS["to_south"]):
                    next_x: int = x + d.x
                    next_y: int = y + d.y
                    if (x, y) in self.forty_two:
                        continue
                    if (next_x, next_y) in self.forty_two:
                        continue
                    if 0 <= next_x < self.width and 0 <= next_y < self.height:
                        have_wall: bool = self.grid[y][x] & d.wall
                        is_outer: bool = self._is_outer_wall(x, y, d)
                        should_break: bool = self.rng.random() < probability
                        if have_wall and not is_outer and should_break:
                            mask_wall: int = (~d.wall) & 0b1111
                            mask_opposite: int = (~d.opposite) & 0b1111
                            self.grid[y][x] &= mask_wall
                            self.grid[next_y][next_x] &= mask_opposite

    def _is_outer_wall(self, x: int, y: int, d: Direction) -> bool:
        if d.wall == NORTH and y == 0:
            return True
        if d.wall == SOUTH and y == self.height - 1:
            return True
        if d.wall == WEST and x == 0:
            return True
        if d.wall == EAST and x == self.width - 1:
            return True
        return False

    def _build_forty_two(self) -> set[Tuple[int, int]]:
        center_x: int = self.width // 2
        center_y: int = self.height // 2
        return {
            (center_x - 3, center_y - 2), (center_x - 3, center_y - 1),
            (center_x - 3, center_y), (center_x - 2, center_y),
            (center_x - 1, center_y), (center_x - 1, center_y + 1),
            (center_x - 1, center_y + 2), (center_x + 1, center_y - 2),
            (center_x + 2, center_y - 2), (center_x + 3, center_y - 2),
            (center_x + 3, center_y - 1), (center_x + 3, center_y),
            (center_x + 2, center_y), (center_x + 1, center_y),
            (center_x + 1, center_y + 1), (center_x + 1, center_y + 2),
            (center_x + 2, center_y + 2), (center_x + 3, center_y + 2),
        }
