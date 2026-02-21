import sys
from typing import Any
from read_config_params import read_config_params
from maze_generate import MazeGenerator
from output_maze.output_maze import OutputMaze
from pydantic import ValidationError


def main() -> None:
    """
    main関数
    """
    if (len(sys.argv)) != 2:
        print("Invalid argv.")
        print("Run \"python3 a_maze_ing.py 'path of config.txt'\".")
        return
    try:
        config_params: dict[str, Any] = read_config_params(sys.argv[1])
    except (
        FileNotFoundError, ValueError, IndexError,
        ValidationError
    ) as error:
        print(f"Error: {error}")
        return
    try:
        MazeGenerator(config_params)
        output_maze: OutputMaze = OutputMaze(config_params)
        output_maze.output_maze()
    except (
        PermissionError, ValueError, IndexError,
        TypeError, OSError, RecursionError,
        RuntimeError
    ) as error:
        print(f"Error: {error}")
        return


if __name__ == "__main__":
    main()
