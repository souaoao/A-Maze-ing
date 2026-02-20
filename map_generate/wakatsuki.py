

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


def _is_3x3_fully_open(self, x0: int, y0: int) -> bool:
    """左上(x0,y0)の3x3が、内部の隣接が全部開通してたら True（=禁止状態）"""
    if x0 < 0 or y0 < 0 or x0 + 2 >= self.width or y0 + 2 >= self.height:
        return False

    # 横方向（east）: 2本 × 3行 = 6本
    for yy in range(y0, y0 + 3):
        for xx in range(x0, x0 + 2):
            if (self.grid[yy][xx] & EAST) != 0:  # east壁がある=閉じてる
                return False

    # 縦方向（south）: 2本 × 3列 = 6本
    for xx in range(x0, x0 + 3):
        for yy in range(y0, y0 + 2):
            if (self.grid[yy][xx] & SOUTH) != 0:  # south壁がある=閉じてる
                return False

    return True


def _would_create_3x3_open_by_breaking(
    self, x: int, y: int, d: Direction, next_x: int, next_y: int
) -> bool:
    """
    いまから (x,y)->(next_x,next_y) の壁を壊すとき、
    どこかの3x3が完全開放になるなら True（=この手は禁止）
    """
    # 仮に壊す
    before_a = self.grid[y][x]
    before_b = self.grid[next_y][next_x]

    mask_wall: int = (~d.wall) & 0b1111
    mask_opp: int = (~d.opposite) & 0b1111
    self.grid[y][x] &= mask_wall
    self.grid[next_y][next_x] &= mask_opp

    # 影響するのは周辺だけ：変更した2セル周りの3x3左上候補を検査
    min_x0 = min(x, next_x) - 2
    max_x0 = max(x, next_x)
    min_y0 = min(y, next_y) - 2
    max_y0 = max(y, next_y)

    bad = False
    for y0 in range(min_y0, max_y0 + 1):
        for x0 in range(min_x0, max_x0 + 1):
            if self._is_3x3_fully_open(x0, y0):
                bad = True
                break
        if bad:
            break

    # 戻す
    self.grid[y][x] = before_a
    self.grid[next_y][next_x] = before_b

    return bad
