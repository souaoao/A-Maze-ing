import sys
from read_config_params import read_config_params, MazeParameters
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
        config_params: MazeParameters = read_config_params(sys.argv[1])
    except (
        FileNotFoundError, ValueError, IndexError,
        ValidationError
    ) as error:
        print(f"Error: {error}")
        return
    try:
        MazeGenerator(config_params)
    except (
        PermissionError, ValueError, IndexError,
        TypeError, OSError
    ) as error:
        print(f"Error: {error}")
        return
    output_maze: OutputMaze = OutputMaze(config_params.output_file)
    output_maze.output_maze()


if __name__ == "__main__":
    main()
