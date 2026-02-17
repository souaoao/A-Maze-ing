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


class MazeGenerater:
    """
    迷路生成クラス（ボーナスのため、何種類か記載したいんご）
    """
    def __init__(self) -> None:
        self.width: int = 20
        self.height: int = 15
        self.entry: Tuple[int, int] = (0, 0)
        self.exit: Tuple[int, int] = (19, 14)
        self.rng: Random = Random(12431421)
        self.grid: List[List[int]] = [[0b1111 for _ in range(self.width)] for _ in range(self.height)]

    # ==============================
    # 迷路生成（DFS）
    # ==============================
    def generate_dfs(self) -> List[List[int]]:
        visited: List[List[bool]] = [[False for _ in range(self.width)] for _ in range(self.height)]

        def dfs(x: int, y: int) -> None:
            if x == self.exit[0] and y == self.exit[1]:
                return
            visited[y][x] = True
            direction: List[Direction] = list(DIRECTIONS.values())
            self.rng.shuffle(direction)
            d: Direction
            for d in direction:
                next_x: int = x + d.x
                next_y: int = y + d.y
                if 0 <= next_x < self.width and 0 <= next_y < self.height:
                    if not visited[next_y][next_x]:
                        mask_wall: int = ~d.wall
                        mask_opposite: int = ~d.opposite
                        self.grid[y][x] &= mask_wall
                        self.grid[next_y][next_x] &= mask_opposite
                        dfs(next_x, next_y)

        dfs(self.entry[0], self.entry[1])
        return self.grid
