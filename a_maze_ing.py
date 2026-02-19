import sys
from read_config_params import read_config_params
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
        config_params = read_config_params(sys.argv[1])
    except (
        FileNotFoundError, ValueError, IndexError,
        ValidationError
    ) as error:
        print(f"Error: {error}")
        return
    print(config_params)
    print()
    output_maze = OutputMaze(config_params.output_file)
    output_maze.output_maze()


if __name__ == "__main__":
    main()
