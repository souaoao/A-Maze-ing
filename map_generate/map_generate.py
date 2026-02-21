from random import Random
from typing import List, Tuple, Dict, NamedTuple, Optional, Any
from abc import ABC, abstractmethod
from collections import deque

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


class MazeGenerator(ABC):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.width: int = config["WIDTH"]
        self.height: int = config["HEIGHT"]
        self.entry: Tuple[int, int] = config["ENTRY"]
        self.exit: Tuple[int, int] = config["EXIT"]
        self.perfect: bool = config["PERFECT"]
        self.rng: Random = Random(config["SEED"])
        self.forty_two: set[Tuple[int, int]] = self._build_forty_two()
        if self.entry in self.forty_two:
            raise ValueError("Entry cannot be inside 42 area")
        if self.exit in self.forty_two:
            raise ValueError("Exit cannot be inside 42 area")
        self.grid: List[List[int]] = []
        self.shortest_path: List[str] = []

    @abstractmethod
    def generate(self) -> None:
        pass

    # ==============================
    # 壁壊していいか条件
    # ==============================
    def _can_break_wall(self, x: int, y: int, d: Direction) -> bool:
        next_x: int = x + d.x
        next_y: int = y + d.y
        # 範囲外
        if not (0 <= next_x < self.width and 0 <= next_y < self.height):
            return False
        # 外壁は壊さない
        if self._is_outer_wall(x, y, d):
            return False
        # 42エリアを壊さない
        if (x, y) in self.forty_two:
            return False
        if (next_x, next_y) in self.forty_two:
            return False
        # 既に開いているなら不要
        if not (self.grid[y][x] & d.wall):
            return False
        # 3×3 fully openを作るなら禁止
        if self._is_would_create_three_by_three_open_breaking(x, y, d):
            return False
        return True

    # ==============================
    # 不完全迷路生成
    # ==============================
    def _add_extra_connection(self, probability: float = 0.05) -> None:
        for y in range(self.height):
            for x in range(self.width):
                for d in (DIRECTIONS["to_east"], DIRECTIONS["to_south"]):
                    if self._can_break_wall(x, y, d):
                        if self.rng.random() < probability:
                            self._break_wall(x, y, d)

    # ==============================
    # 外壁かどうかチェック
    # ==============================
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

    # ==============================
    # 42マスかどうかチェック
    # ==============================
    def _build_forty_two(self) -> set[Tuple[int, int]]:
        if self.width < 9 or self.height < 7:
            return set()
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

    # ==============================
    # 左上を基点にして３×３になるかどうか
    # ==============================
    def _is_three_by_three_fully_open(self, x: int, y: int) -> bool:
        if x < 0 or y < 0:
            return False
        if x + 2 >= self.width or y + 2 >= self.height:
            return False
        for current_y in range(y, y + 3):
            for current_x in range(x, x + 3):
                if current_x < x + 2:
                    if self.grid[current_y][current_x] & EAST:
                        return False
                if current_y < y + 2:
                    if self.grid[current_y][current_x] & SOUTH:
                        return False
        return True

    # ==============================
    # ３×３になるかどうか
    # ==============================
    def _is_would_create_three_by_three_open_breaking(
            self, x: int, y: int, d: Direction) -> bool:
        next_x: int = x + d.x
        next_y: int = y + d.y

        backup_current: int = self.grid[y][x]
        backup_next: int = self.grid[next_y][next_x]
        self._break_wall(x, y, d)
        for check_y in range(y - 2, y + 1):
            for check_x in range(x - 2, x + 1):
                if self._is_three_by_three_fully_open(check_x, check_y):
                    self.grid[y][x] = backup_current
                    self.grid[next_y][next_x] = backup_next
                    return True
        self.grid[y][x] = backup_current
        self.grid[next_y][next_x] = backup_next

        return False

    # ==============================
    # 壁壊す
    # ==============================
    def _break_wall(self, x: int, y: int, d: Direction) -> None:
        next_x: int = x + d.x
        next_y: int = y + d.y
        mask_wall: int = (~d.wall) & 0b1111
        mask_opposite: int = (~d.opposite) & 0b1111
        self.grid[y][x] &= mask_wall
        self.grid[next_y][next_x] &= mask_opposite

    # ==============================
    # 最短経路（BFS）
    # ==============================
    def _search_shortest_path(self) -> None:
        queue: deque[Tuple[int, int]] = deque([self.entry])
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            self.entry: None}

        while queue:
            x: int
            y: int
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            d: Direction
            for d in DIRECTIONS.values():
                next_x: int = x + d.x
                next_y: int = y + d.y
                if not (self.grid[y][x] & d.wall):
                    if (next_x, next_y) not in came_from:
                        came_from[(next_x, next_y)] = (x, y)
                        queue.append((next_x, next_y))
        current: Tuple[int, int] = self.exit
        while came_from[current] is not None:
            prev: Tuple[int, int] = came_from[current]
            if prev is None:
                break
            dx: int = current[0] - prev[0]
            dy: int = current[1] - prev[1]
            if dx == 1:
                self.shortest_path.append("E")
            elif dx == -1:
                self.shortest_path.append("W")
            elif dy == 1:
                self.shortest_path.append("S")
            elif dy == -1:
                self.shortest_path.append("N")

            current = prev
        self.shortest_path.reverse()

    # ==============================
    # ファイル出力
    # ==============================
    def _write(self) -> None:
        with open("output_file", "w", encoding="utf-8") as f:
            row: List[int]
            for row in self.grid:
                cell: int
                for cell in row:
                    f.write(f"{cell:X}")
                f.write("\n")
            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
            direction: str
            for direction in self.shortest_path:
                f.write(direction)
            f.write("\n")


class DfsMazeGenerator(MazeGenerator):
    def __init__(self, config: Dict):
        super().__init__(config)

    # ==============================
    # 迷路生成（DFS）深さ優先探索
    # ==============================
    def generate(self) -> None:
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
                if self._can_break_wall(x, y, d):
                    if not visited[next_y][next_x]:
                        self._break_wall(x, y, d)
                        dfs(next_x, next_y)

        dfs(self.entry[0], self.entry[1])
        if not self.perfect:
            self._add_extra_connection()


class BfsMazeGenerator(MazeGenerator):
    def __init__(self, config: Dict) -> None:
        super().__init__(config)

    # ==============================
    # 迷路生成（BFS）幅優先探索
    # ==============================
    def generate(self) -> None:
        self.grid: List[List[int]] = [[
            0b1111 for _ in range(self.width)] for _ in range(self.height)]
        visited: List[List[bool]] = [[
            False for _ in range(self.width)] for _ in range(self.height)]
        for (x, y) in self.forty_two:
            visited[y][x] = True

        queue: deque[Tuple[int, int]] = deque()
        visited[self.entry[1]][self.entry[0]] = True
        queue.append(self.entry)
        while queue:
            x: int
            y: int
            x, y = queue.popleft()
            directions: List[Direction] = list(DIRECTIONS.values())
            self.rng.shuffle(directions)
            d: Direction
            for d in directions:
                next_x: int = x + d.x
                next_y: int = y + d.y
                if self._can_break_wall(x, y, d):
                    if not visited[next_y][next_x]:
                        self._break_wall(x, y, d)
                        visited[next_y][next_x] = True
                        queue.append((next_x, next_y))
        if not self.perfect:
            self._add_extra_connection()


class Maze:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.algorithm: Optional[str] = config["ALGORITHM"]
        if self.algorithm == "DFS":
            self.map: MazeGenerator = DfsMazeGenerator(config)
        else:
            self.map: MazeGenerator = BfsMazeGenerator(config)
        self.map.generate()
        self.map._search_shortest_path()
        self.map._write()
