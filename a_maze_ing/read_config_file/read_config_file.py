from read_config_file.validate_config_parameters import (
    validate_config_parameters
)
from typing import Any


def perse_config_text(text: str) -> dict[str, Any]:
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
        line_item = line.split("=")
        key = line_item[0]
        if key in config_parameters.keys():
            raise ValueError(f"Duplicate key: {key}")
        value = line_item[1]
        config_parameters[key] = value
    return config_parameters


def read_config_file(config_file) -> dict[str, Any]:
    """
    config.txtファイルを読み込み、設定を返す

    Returns:
        dict: 迷路の幅、高さ、シード値などが格納されたdict
    """
    with open(config_file, "r") as config_file:
        config_text = config_file.read()
    config_parameters = perse_config_text(config_text)
    return validate_config_parameters(config_parameters)
