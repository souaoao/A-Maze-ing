from enum import Enum


class RequiredKeys(Enum):
    """
    必須キーのEnum

    Args:
        Enum (_type_): Enum
    """
    width = "WIDTH"
    height = "HEIGHT"
    entry_point = "ENTRY"
    exit_point = "EXIT"
    output_file = "OUTPUT_FILE"
    perfect = "PERFECT"


class OptionalKeys(Enum):
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
    parameters["SEED"] = int(parameters.get("SEED"))
    return parameters


def check_all_required_keys(config_parameters: dict) -> None:
    """
    必須のキーを全て持っているか検証し、持っていなければValueErrorを発生させる

    Args:
        config_parameters (dict): _description_
    """
    missing_keys = [
        key.value
        for key in RequiredKeys
        if key.value not in config_parameters
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
    entry_coord = config_parameters["ENTRY"].split(",")
    exit_coord = config_parameters["EXIT"].split(",")
    if config_parameters["PERFECT"] == "True":
        is_perfect = True
    elif config_parameters["PERFECT"] == "False":
        is_perfect = False
    else:
        raise ValueError(f"Invalid bool: {config_parameters['PERFECT']}")

    config_parameters["WIDTH"] = int(config_parameters["WIDTH"])
    config_parameters["HEIGHT"] = int(config_parameters["HEIGHT"])
    config_parameters["ENTRY"] = (int(entry_coord[0]), int(entry_coord[1]))
    config_parameters["EXIT"] = (int(exit_coord[0]), int(exit_coord[1]))
    config_parameters["OUTPUT_FILE"] = config_parameters["OUTPUT_FILE"]
    config_parameters["PERFECT"] = is_perfect
    return config_parameters
    # line too longがめんどくさいので一旦Enum未適用


def validate_config_parameters(config_parameters: dict) -> dict:
    """
    読み込んだconfig.txtの形式が正しいかどうかチェックし、正しくない場合ValueErrorを発生させる

    Args:
        config_parameters (dict): パラメータ

    Returns:
        dict: 正しいパラメータ
    """
    check_all_required_keys(config_parameters)
    required_parameters = put_required_keys(config_parameters)
    all_parameters = check_optional_keys(required_parameters)
    return all_parameters
