from pydantic import BaseModel, model_validator, Field
from typing import Optional


class MazeParameters(BaseModel):
    width: int = Field(...)
    height: int = Field(...)
    entry_coord: tuple[int, int] = Field(...)
    exit_coord: tuple[int, int] = Field(...)
    output_file: str = Field(...)
    perfect: bool = Field(...)
    seed: Optional[int] = Field(None)

    @model_validator(mode='after')
    def check_parameters(self) -> "MazeParameters":
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
