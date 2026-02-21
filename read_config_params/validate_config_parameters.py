from enum import Enum
from .maze_parameter import MazeParameters
from typing import Any


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
        "WIDTH": config_parameters[RequiredKeys.width],
        "HEIGHT": config_parameters[RequiredKeys.height],
        "ENTRY": config_parameters[RequiredKeys.entry_coord],
        "EXIT": config_parameters[RequiredKeys.exit_coord],
        "OUTPUT_FILE": config_parameters[RequiredKeys.output_file],
        "PERFECT": config_parameters[RequiredKeys.perfect],
    }

    seed_value: str | None = config_parameters.get(OptionalKeys.seed)
    if seed_value is not None:
        normalized_parameters["SEED"] = seed_value
    algorithm_type: str | None = config_parameters.get(OptionalKeys.algorithm)
    if algorithm_type is not None:
        normalized_parameters["ALGORITHM"] = algorithm_type
    maze_parameter: MazeParameters = MazeParameters(**normalized_parameters)
    dict_parameter: dict[str, Any] = maze_parameter.model_dump()
    return dict_parameter
