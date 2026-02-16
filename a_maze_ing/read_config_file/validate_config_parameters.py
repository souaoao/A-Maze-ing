from enum import Enum
from maze_parameter import MazeParameters


class RequiredKeys(str, Enum):
    """
    必須キーのEnum

    Args:
        Enum (_type_): Enum
    """
    width = "WIDTH"
    height = "HEIGHT"
    entry_coord = "ENTRY"
    exit_coord = "EXIT"
    output_file = "OUTPUT_FILE"
    perfect = "PERFECT"


class OptionalKeys(str, Enum):
    """
    任意キーのEnum

    Args:
        Enum (_type_): Enum
    """
    seed = "SEED"
    algorithm = "ALGORITHM"


def validate_config_parameters(
    config_parameters: dict[str, str]
) -> MazeParameters:
    """
    dictをインスタンスに変換する

    Args:
        config_parameters (dict[str, str]): 迷路のパラメータが格納されたdict

    Returns:
        MazeParameters: MazeParametersインスタンス
    """
    normalized_parameters = {
        "width": config_parameters[RequiredKeys.width],
        "height": config_parameters[RequiredKeys.height],
        "entry_coord": config_parameters[RequiredKeys.entry_coord],
        "exit_coord": config_parameters[RequiredKeys.exit_coord],
        "output_file": config_parameters[RequiredKeys.output_file],
        "perfect": config_parameters[RequiredKeys.perfect],
    }

    seed_value = config_parameters.get(OptionalKeys.seed)
    if seed_value is not None:
        normalized_parameters["seed"] = seed_value
    maze_parameter = MazeParameters(**normalized_parameters)
    return maze_parameter
