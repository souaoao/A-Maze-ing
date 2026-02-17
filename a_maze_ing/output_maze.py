from pydantic import BaseModel, Field, model_validator


class MazeModel(BaseModel):
    grid: list[str] = Field(...)
    entry_coord: tuple[int, int] = Field(...)
    exit_coord: tuple[int, int] = Field(...)
    route: str = Field(...)

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
    def __init__(self, output_file) -> None:
        self.grid: list[str] = []
        self.entry_coord: tuple[int, int] = ()
        self.exit_coord: tuple[int, int] = ()
        self.route: str

        try:
            with open(output_file, "r") as file:
                for line in file:
                    line = line.rstrip("\n")
                    if line == "":
                        break
                    self.grid.append(line)
                self.entry_coord = next(file).rstrip("\n").split(",")
                self.exit_coord = next(file).rstrip("\n").split(",")
                self.route = next(file).rstrip("\n")
        except FileNotFoundError as error:
            print(f"Error: {error}")

        self.maze_model = MazeModel(
            grid=self.grid,
            entry_coord=self.entry_coord,
            exit_coord=self.exit_coord,
            route=self.route
        )

    def output_maze(self):
        print(self.maze_model)
