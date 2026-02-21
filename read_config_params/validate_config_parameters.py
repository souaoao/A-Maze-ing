from enum import Enum
from .maze_parameter import MazeParameters
from typing import Any
from dataclasses import asdict


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
) -> dict[str, Any]:
    """
    dictをインスタンスに変換する

    Args:
        config_parameters (dict[str, str]): 迷路のパラメータが格納されたdict

    Returns:
        MazeParameters: MazeParametersインスタンス
    """
    normalized_parameters: dict[str, Any] = {
        "width": config_parameters[RequiredKeys.width],
        "height": config_parameters[RequiredKeys.height],
        "entry_coord": config_parameters[RequiredKeys.entry_coord],
        "exit_coord": config_parameters[RequiredKeys.exit_coord],
        "output_file": config_parameters[RequiredKeys.output_file],
        "perfect": config_parameters[RequiredKeys.perfect],
    }

    seed_value: str = config_parameters.get(OptionalKeys.seed)
    if seed_value is not None:
        normalized_parameters["seed"] = seed_value
    algorithm_type: str = config_parameters.get(OptionalKeys.algorithm)
    if algorithm_type is not None:
        normalized_parameters["algorithm"] = algorithm_type
    maze_parameter: MazeParameters = MazeParameters(**normalized_parameters)
    dict_parameter: dict[str, Any] = asdict(maze_parameter)
    return maze_parameter
