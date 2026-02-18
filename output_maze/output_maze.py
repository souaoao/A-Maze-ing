from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any


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

    def output_maze(self) -> None:
        print(self.maze_model)
