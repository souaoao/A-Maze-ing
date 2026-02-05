def validate_config_parameters(config_parameters: dict) -> dict:
    """
    読み込んだconfig.txtの形式が正しいかどうかチェックし、正しくない場合ValueErrorを発生させる

    Args:
        config_parameters (dict): パラメータ

    Returns:
        dict: 正しいパラメータ
    """
    required_keys = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT"
    ]
    missing_keys = [
        keys
        for keys in required_keys
        if keys not in config_parameters.keys()
    ]
    if len(missing_keys) != 0:
        raise ValueError(f"Missing keys: {missing_keys}")

    entry_coord = config_parameters["ENTRY"].split(",")
    exit_coord = config_parameters["EXIT"].split(",")
    if config_parameters["PERFECT"] == "True":
        is_perfect = True
    elif config_parameters["PERFECT"] == "False":
        is_perfect = False
    else:
        raise ValueError(f"Invalid bool: {config_parameters['PERFECT']}")

    validated_parameters = {
        "WIDTH": int(config_parameters["WIDTH"]),
        "HEIGHT": int(config_parameters["HEIGHT"]),
        "ENTRY": (int(entry_coord[0]), int(entry_coord[1])),
        "EXIT": (int(exit_coord[0]), int(exit_coord[1])),
        "OUTPUT_FILE": config_parameters["OUTPUT_FILE"],
        "PERFECT": is_perfect
    }
    return validated_parameters


def perse_config_text(text: str) -> dict:
    """
    読み込んだconfig.txtの内容を読み取り、一行ごとに(key=変数)の形で分離し、dictに格納する。同名のキーがある場合、ValueErrorを発生させる

    Args:
        text (str): config.txtの中身

    Returns:
        dict: パース結果
    """
    lines = text.splitlines()
    config_parameters = {}
    for line in lines:
        line_item = line.split("=")
        key = line_item[0]
        if key in config_parameters.keys():
            raise ValueError(f"Duplicate key: {key}")
        value = line_item[1]
        config_parameters[key] = value
    return config_parameters


def read_config_file(config_file) -> dict:
    """
    config.txtファイルを読み込み、設定を返す

    Returns:
        dict: 迷路の幅、高さ、シード値などが格納されたdict
    """
    with open(config_file, "r") as config_file:
        config_text = config_file.read()
    config_parameters = perse_config_text(config_text)
    return validate_config_parameters(config_parameters)
