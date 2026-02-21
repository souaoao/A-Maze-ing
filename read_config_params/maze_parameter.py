from pydantic import BaseModel, model_validator, field_validator, Field
from typing import Optional
from enum import Enum


class ALGORITHMType(str, Enum):
    """
    アルゴリズムのタイプのEnumサンプル

    Args:
        str (_type_): _description_
        Enum (_type_): _description_
    """
    dfs = "DFS"
    bfs = "BFS"


class MazeParameters(BaseModel):
    """
    迷路のパラメータをバリデートして格納するクラス

    Args:
        BaseModel (_type_): BaseModelクラス

    Raises:
        ValueError: ENTRYが迷路サイズの外にある場合
        ValueError: EXITが迷路サイズの外にある場合
        ValueError: outputファイルのパスが.txtで終わっていない場合
    """
    WIDTH: int = Field(...)
    HEIGHT: int = Field(...)
    ENTRY: tuple[int, int] = Field(...)
    EXIT: tuple[int, int] = Field(...)
    OUTPUT_FILE: str = Field(...)
    PERFECT: bool = Field(...)
    SEED: Optional[int] = Field(None)
    ALGORITHM: Optional[str] = Field(None)

    @field_validator("ENTRY", "EXIT", mode="before")
    def parse_coord(
        cls,
        coord_string: str | tuple[int, int]
    ) -> tuple[int, int]:
        """
        ,区切りの文字列で渡された座標情報を,区切りでtupleにする

        Args:
            coord_string (str | tuple[int, int]): 入口もしくは出口の二次元座標を,区切りで表した文字列

        Returns:
            tuple[int, int]: 座標のタプル
        """
        if isinstance(coord_string, tuple):
            return coord_string
        x, y = coord_string.split(",")
        return (int(x), int(y))

    @model_validator(mode='after')
    def check_parameters(self) -> "MazeParameters":
        """
        バリデート

        Raises:
            ValueError: ENTRYが迷路サイズの外にある場合
            ValueError: EXITが迷路サイズの外にある場合
            ValueError: outputファイルのパスが.txtで終わっていない場合

        Returns:
            MazeParameters: バリデート済みのMazeParametersインスタンス
        """
        if (
            self.ENTRY[0] < 0
            or self.ENTRY[1] < 0
            or self.WIDTH <= self.ENTRY[0]
            or self.HEIGHT <= self.ENTRY[1]
        ):
            raise ValueError("Invalid entry coord (maze size < entry coord)")
        if (
            self.EXIT[0] < 0
            or self.EXIT[1] < 0
            or self.WIDTH <= self.EXIT[0]
            or self.HEIGHT <= self.EXIT[1]
        ):
            raise ValueError("Invalid exit coord (maze size < exit coord)")
        if not self.OUTPUT_FILE.endswith(".txt"):
            raise ValueError("OUTPUT_FILE must end with '.txt'")
        if self.ALGORITHM is not None:
            allowed = {item.value for item in ALGORITHMType}
            if self.ALGORITHM not in allowed:
                raise ValueError(f"ALGORITHM must be one of {allowed}")
        return self
