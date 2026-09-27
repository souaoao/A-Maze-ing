import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Set, Tuple

from mazegen import MazeGenerator
from mazegen.maze_generate import EAST, NORTH, SOUTH, WEST, MazeApp
from output_maze.maze_model import MazeModel
from read_config_params import read_config_params
from read_config_params.read_config_params import parse_config_text
from read_config_params.validate_config_parameters import (
    validate_config_parameters,
)


Coordinate = Tuple[int, int]


def make_config(
        output_file: str,
        algorithm: str = "DFS",
        perfect: bool = True,
        seed: int = 42) -> Dict[str, Any]:
    return {
        "WIDTH": 19,
        "HEIGHT": 15,
        "ENTRY": (0, 0),
        "EXIT": (18, 14),
        "OUTPUT_FILE": output_file,
        "PERFECT": perfect,
        "SEED": seed,
        "ALGORITHM": algorithm,
    }


def count_open_edges(maze: MazeApp) -> int:
    edges = 0
    for y_coord, row in enumerate(maze.grid):
        for x_coord, cell in enumerate(row):
            if (x_coord, y_coord) in maze.forty_two:
                continue
            if x_coord + 1 < maze.width and not cell & EAST:
                edges += 1
            if y_coord + 1 < maze.height and not cell & SOUTH:
                edges += 1
    return edges


class ConfigTests(unittest.TestCase):
    def test_reads_and_normalizes_a_valid_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.txt"
            config_path.write_text(
                "WIDTH=11\n"
                "HEIGHT=9\n"
                "ENTRY=0,0\n"
                "EXIT=10,8\n"
                "OUTPUT_FILE=maze.txt\n"
                "PERFECT=True\n"
                "SEED=100\n"
                "ALGORITHM=BFS\n",
                encoding="utf-8",
            )

            config = read_config_params(str(config_path))

        self.assertEqual(config["WIDTH"], 11)
        self.assertEqual(config["ENTRY"], (0, 0))
        self.assertIs(config["PERFECT"], True)
        self.assertEqual(config["SEED"], 100)
        self.assertEqual(config["ALGORITHM"], "BFS")

    def test_rejects_duplicate_config_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate key"):
            parse_config_text("WIDTH=10\nWIDTH=11")

    def test_rejects_invalid_coordinates_and_algorithm(self) -> None:
        base = {
            "WIDTH": "5",
            "HEIGHT": "5",
            "ENTRY": "0,0",
            "EXIT": "4,4",
            "OUTPUT_FILE": "maze.txt",
            "PERFECT": "True",
        }
        with self.assertRaises(ValueError):
            validate_config_parameters({**base, "EXIT": "5,4"})
        with self.assertRaises(ValueError):
            validate_config_parameters({**base, "ALGORITHM": "A_STAR"})
        with self.assertRaises(ValueError):
            validate_config_parameters({
                **base,
                "OUTPUT_FILE": "maze.json",
            })


class GenerationTests(unittest.TestCase):
    def test_seed_reproduces_the_same_grid_and_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = MazeGenerator(make_config(
                str(Path(directory) / "first.txt"), seed=123,
            )).map
            second = MazeGenerator(make_config(
                str(Path(directory) / "second.txt"), seed=123,
            )).map

        self.assertEqual(first.grid, second.grid)
        self.assertEqual(first.shortest_path, second.shortest_path)

    def test_dfs_and_bfs_generate_valid_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for algorithm in ("DFS", "BFS"):
                with self.subTest(algorithm=algorithm):
                    maze = MazeGenerator(make_config(
                        str(Path(directory) / f"{algorithm}.txt"),
                        algorithm=algorithm,
                    )).map
                    self._assert_wall_consistency(maze)
                    self._assert_route_reaches_exit(maze)

    def test_perfect_maze_is_a_tree_over_traversable_cells(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            maze = MazeGenerator(make_config(
                str(Path(directory) / "perfect.txt"),
                perfect=True,
            )).map

        traversable_cells = maze.width * maze.height - len(maze.forty_two)
        self.assertEqual(count_open_edges(maze), traversable_cells - 1)

    def test_imperfect_maze_adds_connections_without_opening_a_3x3(
            self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            maze = MazeGenerator(make_config(
                str(Path(directory) / "imperfect.txt"),
                perfect=False,
            )).map

        traversable_cells = maze.width * maze.height - len(maze.forty_two)
        self.assertGreater(count_open_edges(maze), traversable_cells - 1)
        for y_coord in range(maze.height - 2):
            for x_coord in range(maze.width - 2):
                self.assertFalse(maze._is_three_by_three_fully_open(
                    x_coord, y_coord,
                ))

    def test_forty_two_cells_remain_fully_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            maze = MazeGenerator(make_config(
                str(Path(directory) / "forty-two.txt"),
            )).map

        self.assertEqual(len(maze.forty_two), 18)
        self.assertTrue(all(
            maze.grid[y_coord][x_coord] == 0b1111
            for x_coord, y_coord in maze.forty_two
        ))

    def test_output_file_contains_grid_coordinates_and_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "maze.txt"
            maze = MazeGenerator(make_config(str(output_path))).map
            lines = output_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(len(lines[:maze.height]), maze.height)
        self.assertTrue(all(len(row) == maze.width
                            for row in lines[:maze.height]))
        self.assertEqual(lines[maze.height], "")
        self.assertEqual(lines[maze.height + 1], "0,0")
        self.assertEqual(lines[maze.height + 2], "18,14")
        self.assertEqual(lines[maze.height + 3], "".join(
            maze.shortest_path,
        ))

    def _assert_wall_consistency(self, maze: MazeApp) -> None:
        for y_coord, row in enumerate(maze.grid):
            for x_coord, cell in enumerate(row):
                if y_coord == 0:
                    self.assertTrue(cell & NORTH)
                if y_coord == maze.height - 1:
                    self.assertTrue(cell & SOUTH)
                if x_coord == 0:
                    self.assertTrue(cell & WEST)
                if x_coord == maze.width - 1:
                    self.assertTrue(cell & EAST)
                if x_coord + 1 < maze.width:
                    east_is_closed = bool(cell & EAST)
                    west_is_closed = bool(
                        maze.grid[y_coord][x_coord + 1] & WEST
                    )
                    self.assertEqual(east_is_closed, west_is_closed)
                if y_coord + 1 < maze.height:
                    south_is_closed = bool(cell & SOUTH)
                    north_is_closed = bool(
                        maze.grid[y_coord + 1][x_coord] & NORTH
                    )
                    self.assertEqual(south_is_closed, north_is_closed)

    def _assert_route_reaches_exit(self, maze: MazeApp) -> None:
        directions: Dict[str, Tuple[int, int, int]] = {
            "N": (0, -1, NORTH),
            "E": (1, 0, EAST),
            "S": (0, 1, SOUTH),
            "W": (-1, 0, WEST),
        }
        current = maze.entry
        visited: Set[Coordinate] = {current}
        for move in maze.shortest_path:
            x_delta, y_delta, wall = directions[move]
            self.assertFalse(maze.grid[current[1]][current[0]] & wall)
            current = (current[0] + x_delta, current[1] + y_delta)
            self.assertTrue(0 <= current[0] < maze.width)
            self.assertTrue(0 <= current[1] < maze.height)
            visited.add(current)
        self.assertEqual(current, maze.exit)
        self.assertEqual(len(visited), len(maze.shortest_path) + 1)


class OutputModelTests(unittest.TestCase):
    def test_accepts_a_rectangular_grid_and_cardinal_route(self) -> None:
        model = MazeModel.model_validate({
            "grid": ["FF", "FF"],
            "entry_coord": "0,0",
            "exit_coord": "1,1",
            "route": "ES",
        })

        self.assertEqual(model.entry_coord, (0, 0))
        self.assertEqual(model.route, "ES")

    def test_rejects_uneven_rows_and_unknown_route_symbols(self) -> None:
        with self.assertRaises(ValueError):
            MazeModel.model_validate({
                "grid": ["FFF", "FF"],
                "entry_coord": "0,0",
                "exit_coord": "1,1",
                "route": "ES",
            })
        with self.assertRaises(ValueError):
            MazeModel.model_validate({
                "grid": ["FF", "FF"],
                "entry_coord": "0,0",
                "exit_coord": "1,1",
                "route": "EX",
            })


if __name__ == "__main__":
    unittest.main()
