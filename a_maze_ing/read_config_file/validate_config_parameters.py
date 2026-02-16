from enum import Enum
from typing import Optional
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
    任意キーのEnum(現時点で未使用)

    Args:
        Enum (_type_): Enum
    """
    seed = "SEED"
    algorithm = "ALGORITHM"


def check_optional_keys(parameters: dict) -> dict:
    """
    任意キーの検証。intなどに失敗した場合ValueError

    Args:
        parameters (dict): 必須キーをバリデート済みのパラメータ

    Returns:
        dict: 検証済みのパラメータ
    """
    seed_value: Optional[str] = parameters.get(OptionalKeys.seed)
    if seed_value is not None:
        parameters[OptionalKeys.seed] = int(seed_value)
    return parameters


def check_required_keys(config_parameters: dict) -> None:
    """
    必須のキーを全て持っているか検証し、持っていなければValueErrorを発生させる

    Args:
        config_parameters (dict): _description_
    """
    missing_keys = [
        key
        for key in RequiredKeys
        if key not in config_parameters
    ]
    if len(missing_keys) != 0:
        raise ValueError(f"Missing keys: {missing_keys}")
    else:
        return


def put_required_keys(config_parameters: dict) -> dict:
    """
    必須パラメータをdictに変形して返す。int化に失敗した場合、またはPERFECTが真偽値の文字列じゃない場合はValueError

    Args:
        config_parameters (dict): パラメータ

    Raises:
        ValueError: PERFECTキーの値がTrue, False以外の文字列の場合、また、intが失敗した場合

    Returns:
        dict: 必須キーが格納されたパラメータ
    """
    entry_coord = config_parameters[RequiredKeys.entry_coord].split(",")
    exit_coord = config_parameters[RequiredKeys.exit_coord].split(",")
    if config_parameters[RequiredKeys.perfect] == "True":
        is_perfect = True
    elif config_parameters[RequiredKeys.perfect] == "False":
        is_perfect = False
    else:
        raise ValueError(f"Invalid bool: {config_parameters['PERFECT']}")

    config_parameters[RequiredKeys.width] = int(
        config_parameters[RequiredKeys.width])
    config_parameters[RequiredKeys.height] = int(
        config_parameters[RequiredKeys.height])
    config_parameters[RequiredKeys.entry_coord] = (
        int(entry_coord[0]), int(entry_coord[1]))
    config_parameters[RequiredKeys.exit_coord] = (
        int(exit_coord[0]), int(exit_coord[1]))
    config_parameters[RequiredKeys.output_file] = config_parameters[
        "OUTPUT_FILE"]
    config_parameters[RequiredKeys.perfect] = is_perfect
    return config_parameters


def validate_config_parameters(config_parameters: dict) -> dict:
    """
    読み込んだconfig.txtの形式が正しいかどうかチェックし、正しくない場合ValueErrorを発生させる

    Args:
        config_parameters (dict): パラメータ

    Returns:
        dict: 正しいパラメータ
    """
    check_required_keys(config_parameters)
    required_parameters = put_required_keys(config_parameters)
    all_parameters = check_optional_keys(required_parameters)
    normalized_parameters = {
        "width": all_parameters[RequiredKeys.width],
        "height": all_parameters[RequiredKeys.height],
        "entry_coord": all_parameters[RequiredKeys.entry_coord],
        "exit_coord": all_parameters[RequiredKeys.exit_coord],
        "output_file": all_parameters[RequiredKeys.output_file],
        "perfect": all_parameters[RequiredKeys.perfect],
    }

    seed_value = all_parameters.get(OptionalKeys.seed)
    if seed_value is not None:
        normalized_parameters["seed"] = seed_value
    maze_parameter = MazeParameters(**normalized_parameters)
    return maze_parameter
