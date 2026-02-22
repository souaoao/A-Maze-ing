*This project has been created as part of the 42 curriculum by smiyata.*

# A-Maze-ing

## Description
本プロジェクトは、42 Rank02 の課題向けに作成した Python 製の迷路生成・可視化プログラムである。  
以下の機能を実装している。

- 設定ファイル（`KEY=VALUE`）の読み込み
- 乱数シード（`SEED`）による再現可能な迷路生成
- 課題仕様どおりの 16 進壁表現での出力
- 最短経路（`N/E/S/W`）の計算と保存
- MLX を使ったインタラクティブ表示

迷路生成ロジックは `mazegen` パッケージ（`MazeGenerator`）として再利用可能。

### Features
- `pydantic` による必須キー検証
- 迷路生成アルゴリズム
  - `DFS`（サンプル設定のデフォルト）
  - `BFS`
- `PERFECT=True`（木構造ベースの完全迷路）
- `PERFECT=False`（制約を守りつつ追加通路を開通）
- 3x3 の完全開放領域を禁止
- 閉鎖セルで「42」を可視化（小さい迷路ではコンソール通知して省略）
- 課題仕様の出力フォーマット
  - 16進グリッド
  - 空行
  - ENTRY座標
  - EXIT座標
  - 最短経路文字列
- MLX 操作
  - `ESC`: 終了
  - `1`: 迷路再生成
  - `2`: 最短経路の表示/非表示
  - `3`: 壁色変更
  - `4`: アニメーション描画

## Instructions
### Requirements
- Python `3.10+`
- `mlx` を表示できる Linux/X11 環境

### Setup
```zsh
make install
```

### Run
```zsh
make run
```
または install 済み環境において、
```zsh
python3 a_maze_ing.py config.txt
```

### Debug
```zsh
make debug
```

### Lint / Type check
```zsh
make lint
```

### Build reusable package
```zsh
make build
```
生成物（distディレクトリ）:
- `mazegen-1.0.0.tar.gz`
- `mazegen-1.0.0-py3-none-any.whl`

これらのパスを `requirements.txt` に記載した上で、
```zsh
make install
make run
```
を実行することで、パッケージ化した `mazegen` を用いた実行が可能。

### Clean temporary files
```zsh
make clean
```

### Config File Format
1 行につき 1 つの `KEY=VALUE` を記述する。  
`#` で始まる行はコメントとして無視する。

### Mandatory keys
- `WIDTH=<int>`
  - 迷路の幅（セル数）
- `HEIGHT=<int>`
  - 迷路の高さ（セル数）
- `ENTRY=<x>,<y>`
  - 入口座標（< WIDTH, HEIGHT）
- `EXIT=<x>,<y>`
  - 出口座標（< WIDTH, HEIGHT かつ `ENTRY` と異なる）
- `OUTPUT_FILE=<path>.txt`
  - 出力ファイル名（`.txt` 必須）
- `PERFECT=<bool>`
  - `True` または `False`

### Optional keys
- `SEED=<int>`
  - 乱数シード
- `ALGORITHM=DFS|BFS`
  - 生成アルゴリズム

### Default example (`config.txt`)
```txt
WIDTH=11
HEIGHT=11
ENTRY=0,0
EXIT=10,10
OUTPUT_FILE=maze.txt
PERFECT=True
#Optional
#seed=100
#ALGORITHM=DFS
```

### Output File Format
各セルは「閉じている壁」をビットで表し、16進 1 桁で出力する。

- bit `0`: North
- bit `1`: East
- bit `2`: South
- bit `3`: West

`1` は壁あり（閉）、`0` は壁なし（開）を示す。

構成:
1. 迷路行（16進、1行1段）
2. 空行
3. `entry_x,entry_y`
4. `exit_x,exit_y`
5. `N`,`E`,`S`,`W` のみで表す最短経路

すべての行末は `\n` とする。

### Algorithm Choice
#### 採用アルゴリズム
- `DFS`（深さ優先・再帰バックトラッカー）
- `BFS`（幅優先展開）

#### この選択理由
- 隣接セルの壁整合性を維持しやすい
- 方向シャッフルで自然にランダム化できる
- 追加制約と両立しやすい
  - 外周壁を壊さない
  - 「42」領域を閉鎖セルとして保護
  - 3x3 完全開放の禁止

### Reusable Part (`mazegen`)
再利用対象はリポジトリルートの `mazegen` パッケージであり、  
主なエントリーポイントは `MazeGenerator` クラスである。

#### Basic usage
```python
from mazegen import MazeGenerator

config = {
    "WIDTH": 20,
    "HEIGHT": 15,
    "ENTRY": (0, 0),
    "EXIT": (19, 14),
    "OUTPUT_FILE": "maze.txt",
    "PERFECT": True,
    "SEED": 42,
    "ALGORITHM": "DFS",
}

generator = MazeGenerator(config)
```

#### Custom parameters
- サイズ: `WIDTH`, `HEIGHT`
- 再現性: `SEED`
- アルゴリズム: `ALGORITHM`（`DFS`/`BFS`）
- 完全迷路モード: `PERFECT`

#### 生成構造と解へのアクセス
`MazeGenerator` は `generator.map` に迷路オブジェクトを保持する。  
以下にアクセス可能である。

- `generator.map.grid`（壁ビットの2次元配列）
- `generator.map.shortest_path`（方向文字の配列）

※この内部構造は再利用用データであり、出力テキスト形式そのものではない。

### Team & Project Management
#### 役割分担
- `smiyata`: config.txtのパース及びバリデーション, 迷路の表示機能, 実行環境の作成
- `hwakatsu`:

#### 計画と実際
- 初期計画
  1. `MazeGenerator` の入出力仕様の合意
  2. `config.txt` 入力処理の実装
  3. 迷路生成アルゴリズムおよび表示機能の実装
  4. 3 で実装した機能の統合
  5. 実行環境の整理および `mazegen` パッケージの作成
- 進行中の変更
  - 入力形式を `BaseModel` インスタンスから `dict` へ変更

#### うまくいった点
- 事前に入出力仕様を概ね確定していたため、統合作業を短期間で完了できた。
- こまめなマージを実施し、同一ファイルでの同時作業を最小化した結果、コンフリクトの発生を防止できた。

#### 改善できる点
- Pull Request のレビューが十分ではなかったため、相互のコード理解が不十分となる場面があった。

#### 使用ツール
- Python 3.10+
- `pydantic`
- `flake8`, `mypy`
- `make`
- `build`
- MLX Python binding (`mlx`)

## Resources
### 参考資料
- 42 subject PDF: `maze_en.subject.pdf`

### AI利用について
AI は以下の用途で使用した。
- README 下書き・文章改善
- 課題要件との照合チェック
- セクション構成の見直し

最終的な実装判断および文書内容は、コードと挙動を確認した上で手動調整した。
