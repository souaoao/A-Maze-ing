import sys
from read_config_file.read_config_file import read_config_file


def main() -> None:
    """
    main関数
    """
    if (len(sys.argv)) != 2:
        print("Invalid argv.")
        print("Run \"python3 a_maze_ing.py 'path of config.txt'\".")
        return
    try:
        config_params = read_config_file(sys.argv[1])
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return
    print(config_params)


if __name__ == "__main__":
    main()
