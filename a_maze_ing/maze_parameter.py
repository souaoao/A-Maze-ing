from pydantic import BaseModel, model_validator, field_validator, Field
from typing import Optional


class MazeParameters(BaseModel):
    """
    迷路のパラメータをバリデートして格納するクラス

    Args:
        BaseModel (_type_): BaseModelクラス

    Raises:
        ValueError: entry_coordが迷路サイズの外にある場合
        ValueError: exit_coordが迷路サイズの外にある場合
        ValueError: outputファイルのパスが.txtで終わっていない場合
    """
    width: int = Field(...)
    height: int = Field(...)
    entry_coord: tuple[int, int] = Field(...)
    exit_coord: tuple[int, int] = Field(...)
    output_file: str = Field(...)
    perfect: bool = Field(...)
    seed: Optional[int] = Field(None)

    @field_validator("entry_coord", "exit_coord", mode="before")
    @classmethod
    def perse_coord(
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
            ValueError: entry_coordが迷路サイズの外にある場合
            ValueError: exit_coordが迷路サイズの外にある場合
            ValueError: outputファイルのパスが.txtで終わっていない場合

        Returns:
            MazeParameters: バリデート済みのMazeParametersインスタンス
        """
        if (
            self.width < self.entry_coord[0]
            or self.height < self.entry_coord[1]
        ):
            raise ValueError("Invalid entry coord (maze size < entry coord)")
        if (
            self.width < self.exit_coord[0]
            or self.height < self.exit_coord[1]
        ):
            raise ValueError("Invalid exit coord (maze size < exit coord)")
        if not self.output_file.endswith(".txt"):
            raise ValueError("output_file must end with '.txt'")
        return self
