from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from mlx import Mlx
from typing import Any
from ctypes import c_void_p


class WindowScale(int, Enum):
    line_length = 100


class MazeModel(BaseModel):
    """
    迷路のgrid,entry,exit,routeをバリデートして管理するクラス

    Args:
        BaseModel (_type_): BaseModel
    """
    grid: list[str] = Field(...)
    entry_coord: tuple[int, int] = Field(...)
    exit_coord: tuple[int, int] = Field(...)
    route: str = Field(...)

    @field_validator("entry_coord", "exit_coord", mode="before")
    def parse_coord(
        cls,
        coord_value: str
    ) -> tuple[int, int]:
        """
        入口座標、出口座標の文字列→タプル化

        Args:
            coord_value (str | list[str] | tuple[int, int]): _description_

        Raises:
            ValueError: _description_

        Returns:
            tuple[int, int]: _description_
        """
        parts = coord_value.split(",")
        if len(parts) != 2:
            raise ValueError("coord must be in 'x,y' format")
        return (int(parts[0]), int(parts[1]))

    @model_validator(mode="after")
    def check_model(self) -> "MazeModel":
        """
        モデルのバリデート

        Returns:
            MazeModel: バリデート済みモデル
        """
        if not self.grid:
            raise ValueError("grid must not be empty")
        if not self.grid[0]:
            raise ValueError("grid row must not be empty")

        y_size = len(self.grid)
        x_size = len(self.grid[0])
        for row in self.grid:
            if len(row) != x_size:
                raise ValueError("all grid rows must have the same length")

        entry_x, entry_y = self.entry_coord
        exit_x, exit_y = self.exit_coord
        if not (0 <= entry_x < x_size and 0 <= entry_y < y_size):
            raise ValueError("entry_coord is outside the grid")
        if not (0 <= exit_x < x_size and 0 <= exit_y < y_size):
            raise ValueError("exit_coord is outside the grid")

        if any(move not in {"N", "S", "E", "W"} for move in self.route):
            raise ValueError("route must contain only N,S,E,W")
        return self


class OutputMaze():
    def __init__(self, output_file: str) -> None:
        """
        output_fileの内容を行い、MazeModelクラスでバリデートを行う

        Args:
            output_file (_type_): 迷路の生成結果が記録されたファイル
        """
        grid: list[str] = []

        try:
            with open(output_file, "r") as file:
                for line in file:
                    line = line.rstrip("\n")
                    if line == "":
                        break
                    grid.append(line)
                entry_coord = next(file).rstrip("\n")
                exit_coord = next(file).rstrip("\n")
                route = next(file).rstrip("\n")
        except FileNotFoundError as error:
            raise FileNotFoundError(error) from error

        models: dict[str, Any] = {
            "grid": grid,
            "entry_coord": entry_coord,
            "exit_coord": exit_coord,
            "route": route
        }
        self.maze_model = MazeModel(**models)
        line_length = int(WindowScale.line_length)
        self.window_width = line_length * len(self.grid[0]) + 1
        self.window_height = line_length * len(self.grid) + 1
        self.color: int = int(0xFFFFFFFF)

    @property
    def grid(self) -> list[str]:
        """
        self.maze_model.gridを、self.gridに略すために必要なメソッド

        Returns:
            list[str]: grid
        """
        return self.maze_model.grid

    @property
    def entry_coord(self) -> tuple[int, int]:
        """
        同上

        Returns:
            tuple[int, int]: entry_coord
        """
        return self.maze_model.entry_coord

    @property
    def exit_coord(self) -> tuple[int, int]:
        """
        同上

        Returns:
            tuple[int, int]: exit_coord
        """
        return self.maze_model.exit_coord

    @property
    def route(self) -> str:
        """
        同上

        Returns:
            str: route
        """
        return self.maze_model.route

    @staticmethod
    def _on_key(keycode: int, mlx_apps: dict[str, Any]) -> None:
        if keycode == 65307:
            mlx_apps["mlx"].mlx_loop_exit(mlx_apps["mlx_ptr"])

    @staticmethod
    def _on_close(mlx_apps: dict[str, Any]) -> None:
        mlx_apps["mlx"].mlx_loop_exit(mlx_apps["mlx_ptr"])

    @staticmethod
    def _draw_straight_line(
        mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p,
        x1: int, y1: int, x2: int, y2: int, color: int
    ) -> None:
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            mlx.mlx_pixel_put(mlx_ptr, win_ptr, x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            err2 = 2 * err
            if err2 > -dy:
                err -= dy
                x1 += sx
            if err2 < dx:
                err += dx
                y1 += sy

    def _draw_maze_grid(
        self, mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p
    ) -> None:
        line = WindowScale.line_length

        y_coord = 0
        for row in self.grid:
            x_coord = 0
            for cell in row:
                cell_bits = int(cell, 16)

                north = cell_bits & 0b0001
                east = cell_bits & 0b0010
                south = cell_bits & 0b0100
                west = cell_bits & 0b1000

                x0, y0 = x_coord, y_coord
                x1, y1 = x_coord + line, y_coord + line

                if north:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x0, y0, x1, y0,
                        self.color
                    )
                if east:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x1, y0, x1, y1,
                        self.color
                    )
                if south:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x0, y1, x1, y1,
                        self.color
                    )
                if west:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x0, y0, x0, y1,
                        self.color
                    )

                x_coord += line
            y_coord += line

    def output_maze(self) -> None:
        print(self.route)

        mlx = Mlx()
        mlx_ptr = mlx.mlx_init()
        win_ptr = mlx.mlx_new_window(
            mlx_ptr,
            self.window_width, self.window_height,
            "A-Maze-ing"
        )
        mlx_apps = {"mlx": mlx, "mlx_ptr": mlx_ptr, "win_ptr": win_ptr}

        mlx.mlx_key_hook(win_ptr, self._on_key, mlx_apps)
        mlx.mlx_hook(win_ptr, 33, 0, self._on_close, mlx_apps)
        self._draw_maze_grid(mlx, mlx_ptr, win_ptr)
        mlx.mlx_loop(mlx_ptr)

        mlx.mlx_destroy_window(mlx_ptr, win_ptr)
        mlx.mlx_release(mlx_ptr)
