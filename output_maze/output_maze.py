from .maze_model import MazeModel
from enum import Enum
from mlx import Mlx
from typing import Any, TextIO
from ctypes import c_void_p
import signal
import time


class GenerateConfig(int, Enum):
    """
    線の長さを決定するEnum
    """
    line_length = 50
    sleep_time = 1


class KeyCode(int, Enum):
    """
    KeyCodeのEnum
    """
    esc = 65307
    one = 49
    two = 50
    three = 51
    four = 52


class Colors(int, Enum):
    """
    カラーコードのEnum
    """
    white = 0xFFFFFFFF
    blue = 0xFF0000FF
    green = 0xFF00FF00
    red = 0xFFFF0000
    yellow = 0xFFFFFF00
    magenta = 0xFFFF00FF
    cyan = 0xFF00FFFF


class OutputMaze():
    """
    maze.txt（または任意のファイルパス）から迷路を作成するクラス
    """
    def __init__(self, output_file: str) -> None:
        """
        output_fileの内容を行い、MazeModelクラスでバリデートを行う

        Args:
            output_file (_type_): 迷路の生成結果が記録されたファイル
        """
        self.output_file: str = output_file
        self.get_maze_info()

        self.line_colors: list[Colors] = [
            Colors.white,
            Colors.yellow,
            Colors.magenta,
            Colors.cyan
        ]
        self.line_color_index: int = 0
        self.line_color: int = self.line_colors[self.line_color_index]
        self.entry_color: int = Colors.green
        self.exit_color: int = Colors.red
        self.route_color: int = Colors.blue

        self.is_draw_route: bool = False
        self.is_animation: bool = False
        self._is_key_guide_printed: bool = False

    def get_maze_info(self) -> None:
        """
        initで保存したself.output_fileから、迷路のサイズなどを決定するメソッド

        Raises:
            FileNotFoundError: ファイルが見つからない場合
        """
        try:
            file: TextIO
            with open(self.output_file, "r") as file:
                line: str
                grid: list[str] = []
                for line in file:
                    line = line.rstrip("\n")
                    if line == "":
                        break
                    grid.append(line)
                entry_coord: str = next(file).rstrip("\n")
                exit_coord: str = next(file).rstrip("\n")
                route: str = next(file).rstrip("\n")
        except FileNotFoundError as error:
            raise FileNotFoundError(error)

        models: dict[str, Any] = {
            "grid": grid,
            "entry_coord": entry_coord,
            "exit_coord": exit_coord,
            "route": route
        }
        self.maze_model: MazeModel = MazeModel(**models)
        line_length = int(GenerateConfig.line_length)
        self.window_width: int = line_length * len(self.grid[0]) + 1
        self.window_height: int = line_length * len(self.grid) + 1

    @property
    def grid(self) -> list[str]:
        """
        self.maze_model.gridを、self.gridに略すために必要なメソッド

        Returns:
            list[str]: grid
        """
        return self.maze_model.grid

    @property
    def entry_coord(self) -> tuple[int, int]:
        """
        同上

        Returns:
            tuple[int, int]: entry_coord
        """
        return self.maze_model.entry_coord

    @property
    def exit_coord(self) -> tuple[int, int]:
        """
        同上

        Returns:
            tuple[int, int]: exit_coord
        """
        return self.maze_model.exit_coord

    @property
    def route(self) -> str:
        """
        同上

        Returns:
            str: route
        """
        return self.maze_model.route

    @staticmethod
    def _on_close(mlx_apps: dict[str, Any]) -> None:
        """
        xボタンを押したときに画面を閉じる

        Args:
            mlx_apps (dict[str, Any]): mlxのポインタなど
        """
        mlx_apps["mlx"].mlx_loop_exit(mlx_apps["mlx_ptr"])

    @staticmethod
    def _draw_straight_line(
        mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p,
        x1: int, y1: int, x2: int, y2: int, color: int
    ) -> None:
        """
        ブレゼンハムのアルゴリズムで、(x1, y1)から(x2, y2)間の直線を描画

        Args:
            mlx (Mlx): mlx
            mlx_ptr (c_void_p): mlx_ptr
            win_ptr (c_void_p): win_ptr
            x1 (int): 始点のx座標
            y1 (int): 始点のy座標
            x2 (int): 終点のx座標
            y2 (int): 終点のy座標
            color (int): 色
        """
        dx: int = abs(x2 - x1)
        dy: int = abs(y2 - y1)
        sx: int = 1 if x1 < x2 else -1
        sy: int = 1 if y1 < y2 else -1
        delta: int = dx - dy

        while True:
            mlx.mlx_pixel_put(mlx_ptr, win_ptr, x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            delta2: int = 2 * delta
            if delta2 > -dy:
                delta -= dy
                x1 += sx
            if delta2 < dx:
                delta += dx
                y1 += sy

    def _draw_square(
        self,
        mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p,
        x1: int, y1: int, x2: int, y2: int, color: int
    ) -> None:
        """
        四角を描画するメソッド

        Args:
            mlx (Mlx): mlxインスタンス
            mlx_ptr (c_void_p): mlxポインタ
            win_ptr (c_void_p): winポインタ
            x1 (int): 左上角のx座標
            y1 (int): 左上角のy座標
            x2 (int): 右下角のx座標
            y2 (int): 右下角のy座標
            color (int): カラーコード
        """
        y_coord: int
        for y_coord in range(y1, y2):
            self._draw_straight_line(
                mlx, mlx_ptr, win_ptr,
                x1, y_coord, x2, y_coord,
                color
            )

    def _draw_maze_grid(
        self, mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p
    ) -> None:
        """
        迷路の壁を出力するメソッド

        Args:
            mlx (Mlx): mlxインスタンス
            mlx_ptr (c_void_p): mlxポインタ
            win_ptr (c_void_p): winポインタ
        """
        line: int = GenerateConfig.line_length

        y_coord: int = 0
        row: str
        for row in self.grid:
            x_coord: int = 0
            cell = str
            for cell in row:
                cell_bits: int = int(cell, 16)

                north: int = cell_bits & 0b0001
                east: int = cell_bits & 0b0010
                south: int = cell_bits & 0b0100
                west: int = cell_bits & 0b1000

                x0: int
                y0: int
                x1: int
                y1: int
                x0, y0= x_coord, y_coord
                x1, y1 = x_coord + line, y_coord + line

                if north:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x0, y0, x1, y0,
                        self.line_color
                    )
                if east:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x1, y0, x1, y1,
                        self.line_color
                    )
                if south:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x0, y1, x1, y1,
                        self.line_color
                    )
                if west:
                    self._draw_straight_line(
                        mlx, mlx_ptr, win_ptr,
                        x0, y0, x0, y1,
                        self.line_color
                    )
                x_coord += line
                if self.is_animation:
                    mlx.mlx_do_sync(mlx_ptr)
                    time.sleep(GenerateConfig.sleep_time * 0.0001)
            y_coord += line

    def _draw_endpoints(
        self, mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p
    ) -> None:
        """
        入口と出口のマスを塗りつぶすメソッド

        Args:
            mlx (Mlx): mlxインスタンス
            mlx_ptr (c_void_p): mlxポインタ
            win_ptr (c_void_p): winポインタ
        """
        entry_x0: int = self.entry_coord[0] * GenerateConfig.line_length + 1
        entry_x1: int = entry_x0 + GenerateConfig.line_length - 1
        entry_y0: int = self.entry_coord[1] * GenerateConfig.line_length + 1
        entry_y1: int = entry_y0 + GenerateConfig.line_length - 1

        exit_x0: int = self.exit_coord[0] * GenerateConfig.line_length + 1
        exit_x1: int = exit_x0 + GenerateConfig.line_length - 2
        exit_y0: int = self.exit_coord[1] * GenerateConfig.line_length + 1
        exit_y1: int = exit_y0 + GenerateConfig.line_length - 1

        self._draw_square(
            mlx, mlx_ptr, win_ptr,
            entry_x0, entry_y0, entry_x1, entry_y1,
            self.entry_color
        )
        self._draw_square(
            mlx, mlx_ptr, win_ptr,
            exit_x0, exit_y0, exit_x1, exit_y1,
            self.exit_color
        )

    def _draw_route(
        self, mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p
    ) -> None:
        """
        最短経路を描画するメソッド

        Args:
            mlx (Mlx): mlxインスタンス
            mlx_ptr (c_void_p): mlxポインタ
            win_ptr (c_void_p): winポインタ
        """
        LINE_LENGTH: int = GenerateConfig.line_length

        entry_x0: int = int(self.entry_coord[0] * LINE_LENGTH + LINE_LENGTH * 0.2)
        entry_x1: int = int(entry_x0 + LINE_LENGTH * 0.6)
        entry_y0: int = int(self.entry_coord[1] * LINE_LENGTH + LINE_LENGTH * 0.2)
        entry_y1: int = int(entry_y0 + LINE_LENGTH * 0.6)

        direction_to_delta = {
            "N": (0, -LINE_LENGTH),
            "S": (0, LINE_LENGTH),
            "E": (LINE_LENGTH, 0),
            "W": (-LINE_LENGTH, 0),
        }

        x0_coord: int = entry_x0
        y0_coord: int = entry_y0
        x1_coord: int = entry_x1
        y1_coord: int = entry_y1
        direction: str
        for direction in self.route:
            x_diff, y_diff = direction_to_delta[direction]
            x0_coord += x_diff
            y0_coord += y_diff
            x1_coord += x_diff
            y1_coord += y_diff

            self._draw_square(
                mlx, mlx_ptr, win_ptr,
                x0_coord, y0_coord,
                x1_coord, y1_coord,
                self.route_color
            )

    def _draw_maze(
        self,
        mlx: Mlx, mlx_ptr: c_void_p, win_ptr: c_void_p
    ) -> None:
        """
        mlxウィンドウに描画するメソッド

        Args:
            mlx (Mlx): mlxインスタンス
            mlx_ptr (c_void_p): mlxポインタ
            win_ptr (c_void_p): winポインタ
        """
        mlx.mlx_clear_window(mlx_ptr, win_ptr)
        self._draw_maze_grid(mlx, mlx_ptr, win_ptr)
        if self.is_draw_route:
            self._draw_route(mlx, mlx_ptr, win_ptr)
        self._draw_endpoints(mlx, mlx_ptr, win_ptr)

    def _on_key(self, keycode: int, mlx_apps: dict[str, Any]) -> None:
        """
        何かしらのキーを押した際に、色々やるメソッド

        Args:
            keycode (int): 押されたキーのキーコード
            mlx_apps (dict[str, Any]): mlxのいろいろ
        """
        if keycode == KeyCode.esc:
            mlx_apps["mlx"].mlx_loop_exit(mlx_apps["mlx_ptr"])
        if keycode == KeyCode.one:
            try:
                self.get_maze_info()
            except FileNotFoundError as error:
                print(f"Error: {error}")
                mlx_apps["mlx"].mlx_loop_exit(mlx_apps["mlx_ptr"])
            self._draw_maze(
                mlx_apps["mlx"], mlx_apps["mlx_ptr"], mlx_apps["win_ptr"]
            )
        if keycode == KeyCode.two:
            self.is_draw_route = not self.is_draw_route
            self._draw_maze(
                mlx_apps["mlx"], mlx_apps["mlx_ptr"], mlx_apps["win_ptr"]
            )
        if keycode == KeyCode.three:
            self.line_color_index = (
                self.line_color_index + 1
            ) % len(self.line_colors)
            self.line_color = self.line_colors[self.line_color_index]
            self._draw_maze(
                mlx_apps["mlx"], mlx_apps["mlx_ptr"], mlx_apps["win_ptr"]
            )
        if keycode == KeyCode.four:
            self.is_animation = True
            self._draw_maze(
                mlx_apps["mlx"], mlx_apps["mlx_ptr"], mlx_apps["win_ptr"]
            )
            self.is_animation = False

    def output_maze(self) -> None:
        """
        迷路を出力するメインメソッド
        """
        mlx: Mlx = Mlx()
        mlx_ptr: c_void_p = mlx.mlx_init()
        win_ptr: c_void_p = mlx.mlx_new_window(
            mlx_ptr,
            self.window_width, self.window_height,
            "A-Maze-ing"
        )
        mlx_apps: dict[str, Any] = {"mlx": mlx, "mlx_ptr": mlx_ptr, "win_ptr": win_ptr}

        mlx.mlx_key_hook(win_ptr, self._on_key, mlx_apps)
        mlx.mlx_hook(win_ptr, 33, 0, self._on_close, mlx_apps)
        previous_sigint_handler: _HANDLER = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            self._draw_maze(mlx, mlx_ptr, win_ptr)
            print(
                "Key controls: "
                "ESC=close, 1=reload maze, 2=toggle route, "
                "3=change wall color, 4=draw animation"
            )
            mlx.mlx_loop(mlx_ptr)
        except FileNotFoundError as error:
            print(f"Error: {error}")
        finally:
            signal.signal(signal.SIGINT, previous_sigint_handler)
            mlx.mlx_destroy_window(mlx_ptr, win_ptr)
            mlx.mlx_release(mlx_ptr)
