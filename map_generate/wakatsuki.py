

from __future__ import annotations

import random
from collections import deque
from typing import List, Tuple, Dict, Optional


# 壁ビット
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

Direction = Tuple[int, int, int, int]

DIRECTIONS: List[Direction] = [
    (0, -1, NORTH, SOUTH),
    (1, 0, EAST, WEST),
    (0, 1, SOUTH, NORTH),
    (-1, 0, WEST, EAST),
]


class Maze:
    """
    迷路生成・最短経路計算クラス
    """

    def __init__(self, config: Dict) -> None:
        self.width: int = config["WIDTH"]
        self.height: int = config["HEIGHT"]
        self.entry: Tuple[int, int] = config["ENTRY"]
        self.exit: Tuple[int, int] = config["EXIT"]
        self.output_file: str = config["OUTPUT_FILE"]
        self.perfect: bool = config["PERFECT"]
        self.seed: Optional[int] = config["SEED"]

        if self.seed is not None:
            random.seed(self.seed)

        # 全壁あり状態で初期化
        self.grid: List[List[int]] = [
            [NORTH | EAST | SOUTH | WEST for _ in range(self.width)]
            for _ in range(self.height)
        ]

    # ==============================
    # 迷路生成（DFS）
    # ==============================
    def generate(self) -> None:
        visited: List[List[bool]] = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

        def dfs(x: int, y: int) -> None:
            visited[y][x] = True
            directions = DIRECTIONS.copy()
            random.shuffle(directions)

            for dx, dy, wall, opposite in directions:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not visited[ny][nx]:
                        # 壁を壊す
                        self.grid[y][x] &= ~wall
                        self.grid[ny][nx] &= ~opposite
                        dfs(nx, ny)

        dfs(self.entry[0], self.entry[1])

    # ==============================
    # 最短経路（BFS）
    # ==============================
    def shortest_path(self) -> List[str]:
        queue: deque[Tuple[int, int]] = deque([self.entry])
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            self.entry: None
        }

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.exit:
                break

            for dx, dy, wall, _ in DIRECTIONS:
                if not (self.grid[y][x] & wall):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in came_from:
                        came_from[(nx, ny)] = (x, y)
                        queue.append((nx, ny))

        path: List[str] = []
        current: Tuple[int, int] = self.exit

        while came_from[current] is not None:
            prev = came_from[current]
            if prev is None:
                break

            dx = current[0] - prev[0]
            dy = current[1] - prev[1]

            if dx == 1:
                path.append("E")
            elif dx == -1:
                path.append("W")
            elif dy == 1:
                path.append("S")
            elif dy == -1:
                path.append("N")

            current = prev

        path.reverse()
        return path

    # ==============================
    # ファイル出力
    # ==============================
    def write(self) -> None:
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for row in self.grid:
                    f.write("".join(f"{cell:X}" for cell in row) + "\n")

                f.write("\n")
                f.write(f"{self.entry[0]},{self.entry[1]}\n")
                f.write(f"{self.exit[0]},{self.exit[1]}\n")
                f.write("".join(self.shortest_path()) + "\n")

        except OSError as error:
            raise RuntimeError(f"File write error: {error}") from error

    # ==============================
    # ASCII表示
    # ==============================
    def display(self) -> None:
        for y in range(self.height):
            top = ""
            middle = ""

            for x in range(self.width):
                cell = self.grid[y][x]

                top += "+"
                top += "---" if cell & NORTH else "   "

                middle += "|" if cell & WEST else " "

                if (x, y) == self.entry:
                    middle += " E "
                elif (x, y) == self.exit:
                    middle += " X "
                else:
                    middle += "   "

            top += "+"
            middle += "|"

            print(top)
            print(middle)

        print("+" + "---+" * self.width)
