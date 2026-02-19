from .maze_model import MazeModel
from enum import Enum
from mlx import Mlx
from typing import Any
from ctypes import c_void_p
import signal


class WindowScale(int, Enum):
    """
    線の長さを決定するEnum
    """
    line_length = 50


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
        self.output_file = output_file
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

        self.is_draw_route = False

    def get_maze_info(self) -> None:
        """
        initで保存したself.output_fileから、迷路のサイズなどを決定するメソッド

        Raises:
            FileNotFoundError: ファイルが見つからない場合
        """
        grid: list[str] = []

        try:
            with open(self.output_file, "r") as file:
                for line in file:
                    line = line.rstrip("\n")
                    if line == "":
                        break
                    grid.append(line)
                entry_coord = next(file).rstrip("\n")
                exit_coord = next(file).rstrip("\n")
                route = next(file).rstrip("\n")
        except FileNotFoundError as error:
            raise FileNotFoundError(error) from error

        models: dict[str, Any] = {
            "grid": grid,
            "entry_coord": entry_coord,
            "exit_coord": exit_coord,
            "route": route
        }
        self.maze_model = MazeModel(**models)
        line_length = int(WindowScale.line_length)
        self.window_width = line_length * len(self.grid[0]) + 1
        self.window_height = line_length * len(self.grid) + 1

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
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            mlx.mlx_pixel_put(mlx_ptr, win_ptr, x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            err2 = 2 * err
            if err2 > -dy:
                err -= dy
                x1 += sx
            if err2 < dx:
                err += dx
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
        line = WindowScale.line_length

        y_coord = 0
        for row in self.grid:
            x_coord = 0
            for cell in row:
                cell_bits = int(cell, 16)

                north = cell_bits & 0b0001
                east = cell_bits & 0b0010
                south = cell_bits & 0b0100
                west = cell_bits & 0b1000

                x0, y0 = x_coord, y_coord
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
        entry_x0 = self.entry_coord[0] * WindowScale.line_length + 1
        entry_x1 = entry_x0 + WindowScale.line_length - 1
        entry_y0 = self.entry_coord[1] * WindowScale.line_length + 1
        entry_y1 = entry_y0 + WindowScale.line_length - 1

        exit_x0 = self.exit_coord[0] * WindowScale.line_length + 1
        exit_x1 = exit_x0 + WindowScale.line_length - 1
        exit_y0 = self.exit_coord[1] * WindowScale.line_length + 1
        exit_y1 = exit_y0 + WindowScale.line_length - 1

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
        entry_x0 = self.entry_coord[0] * WindowScale.line_length
        entry_x1 = entry_x0 + WindowScale.line_length
        entry_y0 = self.entry_coord[1] * WindowScale.line_length
        entry_y1 = entry_y0 + WindowScale.line_length

        direction_to_delta = {
            "N": (0, -WindowScale.line_length),
            "S": (0, WindowScale.line_length),
            "E": (WindowScale.line_length, 0),
            "W": (-WindowScale.line_length, 0),
        }

        x0_coord = entry_x0
        y0_coord = entry_y0
        x1_coord = entry_x1
        y1_coord = entry_y1
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
        if self.is_draw_route:
            self._draw_route(mlx, mlx_ptr, win_ptr)
        self._draw_endpoints(mlx, mlx_ptr, win_ptr)
        self._draw_maze_grid(mlx, mlx_ptr, win_ptr)

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

    def output_maze(self) -> None:
        """
        迷路を出力するメインメソッド
        """
        mlx = Mlx()
        mlx_ptr = mlx.mlx_init()
        win_ptr = mlx.mlx_new_window(
            mlx_ptr,
            self.window_width, self.window_height,
            "A-Maze-ing"
        )
        mlx_apps = {"mlx": mlx, "mlx_ptr": mlx_ptr, "win_ptr": win_ptr}

        mlx.mlx_key_hook(win_ptr, self._on_key, mlx_apps)
        mlx.mlx_hook(win_ptr, 33, 0, self._on_close, mlx_apps)
        previous_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            self._draw_maze(mlx, mlx_ptr, win_ptr)
            mlx.mlx_loop(mlx_ptr)
        except FileNotFoundError as error:
            print(f"Error: {error}")
        finally:
            signal.signal(signal.SIGINT, previous_sigint_handler)
            mlx.mlx_destroy_window(mlx_ptr, win_ptr)
            mlx.mlx_release(mlx_ptr)
