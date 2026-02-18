from .validate_config_parameters import validate_config_parameters
from typing import Any
from .maze_parameter import MazeParameters


def parse_config_text(text: str) -> dict[str, Any]:
    """
    読み込んだconfig.txtの内容を読み取り、一行ごとに(key=変数)の形で分離し、dictに格納する。同名のキーがある場合、ValueErrorを発生させる。また、行内に'='がない場合、IndexErrorが発生する

    Args:
        text (str): config.txtの中身

    Returns:
        dict: パース結果
    """
    lines = text.splitlines()
    config_parameters: dict[str, Any] = {}
    for line in lines:
        if line.startswith("#"):
            continue
        line_item = line.split("=")
        key = line_item[0]
        if key in config_parameters.keys():
            raise ValueError(f"Duplicate key: {key}")
        value = line_item[1]
        config_parameters[key] = value
    return config_parameters


def read_config_params(config_file: str) -> MazeParameters:
    """
    config.txtの内容を読み取り、値をバリデートしてMazeParametersインスタンスとして返す

    Args:
        config_file (str): config.txtのファイルパス

    Returns:
        MazeParameters: 迷路のパラメータインスタンス
    """
    with open(config_file, "r") as file_obj:
        config_text = file_obj.read()
    config_parameters: dict[str, Any] = parse_config_text(config_text)
    return validate_config_parameters(config_parameters)
