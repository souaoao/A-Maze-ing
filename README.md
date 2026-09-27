*This project was created as part of the 42 curriculum by smiyata and
hwakatsu.*

# A-Maze-ing

A-Maze-ing is a configurable maze-generation engine and interactive visualizer
written in Python. It turns a validated configuration into a maze, preserves a
set of structural constraints, finds a shortest route, and writes the result in
a compact hexadecimal wall format.

This team project demonstrates graph algorithms, deterministic generation,
bit-level data modelling, validation, file-format design, reusable packaging,
and Git-based collaboration.

## What it does

```text
config.txt
    -> Pydantic validation
    -> DFS or BFS maze generation
    -> structural constraint checks
    -> BFS shortest-path search
    -> hexadecimal maze file
    -> MLX visualization
```

The application supports:

- recursive DFS and iterative BFS generation;
- reproducible output from a random seed;
- perfect and imperfect maze modes;
- symmetric wall updates represented by four-bit cell values;
- a protected, fully closed `42` pattern on sufficiently large maps;
- prevention of fully open 3 × 3 areas;
- shortest routes encoded with `N`, `E`, `S`, and `W`; and
- a reusable `mazegen` package independent of the visualizer.

## Engineering design

### Validated configuration

The configuration layer parses `KEY=VALUE` lines and normalizes them through a
Pydantic model before generation starts. It validates positive dimensions,
entry and exit bounds, distinct endpoints, a `.txt` output path, and the
optional `DFS` or `BFS` algorithm value.

Required keys:

| Key | Meaning |
| --- | --- |
| `WIDTH` | Maze width in cells |
| `HEIGHT` | Maze height in cells |
| `ENTRY` | Start coordinate as `x,y` |
| `EXIT` | Goal coordinate as `x,y` |
| `OUTPUT_FILE` | Output path ending in `.txt` |
| `PERFECT` | Whether to keep a tree-shaped maze |

Optional keys:

| Key | Meaning | Default behavior |
| --- | --- | --- |
| `SEED` | Integer random seed | Uses an unseeded random sequence |
| `ALGORITHM` | `DFS` or `BFS` | Uses DFS |

Example:

```text
WIDTH=19
HEIGHT=15
ENTRY=0,0
EXIT=18,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=DFS
```

Lines beginning directly with `#` are ignored. The parser intentionally expects
one assignment per remaining line.

### Four-bit wall model

Each cell stores its closed walls in the low four bits of an integer:

| Bit | Value | Wall |
| ---: | ---: | --- |
| 0 | `0b0001` | North |
| 1 | `0b0010` | East |
| 2 | `0b0100` | South |
| 3 | `0b1000` | West |

A set bit means that the wall is closed. Opening a passage updates both cells:
for example, removing one cell's east wall also removes its neighbor's west
wall. The outer boundary remains closed.

The output stores each four-bit value as one uppercase hexadecimal digit. This
keeps the serialized grid compact while preserving every wall.

### Maze generation

Both algorithms begin with every wall closed and mark the protected `42` cells
as unavailable:

- **DFS** uses recursive backtracking and shuffles candidate directions with a
  local `random.Random` instance.
- **BFS** expands cells through a queue and uses the same seeded direction
  shuffling.

With `PERFECT=True`, the traversable graph is a tree: it is connected and has
one route between any two traversable cells. With `PERFECT=False`, the generator
opens additional eligible walls after building the initial maze. These extra
connections can introduce cycles while retaining the structural checks.

Before opening a wall, the engine verifies that:

- the neighboring cell is inside the grid;
- the wall is not part of the outer boundary;
- neither cell belongs to the protected `42` region;
- the passage is not already open; and
- the change would not create a fully open 3 × 3 area.

### Shortest-path search

Generation and solution are separate steps. Regardless of whether DFS or BFS
generated the maze, the solver runs BFS from `ENTRY` to `EXIT`. It records each
cell's predecessor and reconstructs one shortest route as cardinal direction
letters.

For a grid with `V = WIDTH × HEIGHT` cells and at most four neighbors per cell,
the shortest-path search is `O(V)` in time and space.

### Protected `42` region

For maps at least 9 cells wide and 7 cells high, the generator builds an
18-cell `42` pattern around the center. Every protected cell stays at `0xF`, so
all four of its walls remain closed. Entry and exit coordinates inside this
region are rejected.

Smaller maps skip the pattern and print an explanatory message.

## Output format

The output file contains:

1. one hexadecimal grid row per maze row;
2. one blank line;
3. the entry coordinate;
4. the exit coordinate; and
5. the shortest route.

```text
F9...
C2...
...

0,0
18,14
EESS...
```

Each line ends with a newline. The route contains only `N`, `E`, `S`, and `W`.

## Project structure

| Path | Responsibility |
| --- | --- |
| `a_maze_ing.py` | CLI orchestration and application-level error handling |
| `read_config_params/` | Parsing, normalization, and Pydantic validation |
| `mazegen/maze_generate.py` | Generation, constraints, solving, and output |
| `output_maze/maze_model.py` | Validation of serialized maze data |
| `output_maze/output_maze.py` | MLX rendering and keyboard interaction |
| `tests/test_a_maze_ing.py` | Core behavior and invariant tests |
| `pyproject.toml` | Reusable `mazegen` package definition |

## Run locally

Requirements:

- Python 3.10 or later;
- `make`; and
- an environment compatible with the bundled MLX Python binding for graphical
  output.

```bash
make install
make run
```

Run with another configuration:

```bash
.venv/bin/python3 a_maze_ing.py path/to/config.txt
```

Other commands:

```bash
make debug   # run under pdb
make lint    # run flake8 and mypy
make build   # build the reusable mazegen package
make clean   # remove generated local files
```

### Visualizer controls

| Key | Action |
| --- | --- |
| `1` | Generate the maze again |
| `2` | Show or hide the shortest route |
| `3` | Change the wall color |
| `4` | Toggle drawing animation |
| `ESC` | Close the window |

## Reuse as a package

The algorithm is exposed through `MazeGenerator`:

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
grid = generator.map.grid
route = generator.map.shortest_path
```

`make build` creates a source distribution and wheel under `dist/`.

## Tests

The `unittest` suite verifies behavior rather than mirroring implementation
lines. It covers:

- configuration parsing and invalid-input rejection;
- deterministic generation from a fixed seed;
- valid DFS- and BFS-generated routes;
- matching walls between neighboring cells and closed outer walls;
- the tree invariant for a perfect maze;
- extra connections in imperfect mode;
- prevention of fully open 3 × 3 areas;
- preservation of all 18 protected `42` cells;
- hexadecimal output structure; and
- validation of loaded grid and route data.

Run the tests after installation:

```bash
.venv/bin/python3 -m unittest discover -s tests -v
```

## Team collaboration

The work was divided around a shared interface so the generator and visualizer
could be developed independently and integrated through the output file.

### smiyata

- configuration parsing and validation;
- maze visualization; and
- runtime environment setup.

### hwakatsu

- DFS/BFS generation design and implementation;
- shortest-path calculation;
- four-bit wall representation;
- reusable `mazegen` packaging; and
- the 3 × 3, protected `42`, and outer-wall constraints.

The team agreed on the generator's input and output contract early, then merged
small branches frequently to reduce overlapping edits. The main improvement
identified in retrospect was to make pull-request review more thorough so both
contributors understood more of the other component's implementation.

## Design boundaries

- DFS generation is recursive, so very large maps can reach Python's recursion
  limit.
- Imperfect mode adds eligible passages heuristically; it does not sample
  uniformly from all possible imperfect mazes.
- If no wall is eligible, imperfect mode cannot guarantee an additional
  passage.
- The protected `42` pattern is disabled below 9 × 7.
- The configuration parser is strict: blank lines and indented comments are not
  accepted as comments.
- The graphical layer depends on the bundled MLX binding and a compatible
  display environment. Core generation and tests do not require opening a GUI.
- Tests cover representative invariants and configurations; they are not a
  formal proof for every size and seed.

## Resources

- [Python documentation](https://docs.python.org/3/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search)
- 42 project subject: `maze_en.subject.pdf`

## AI usage

AI was used to review documentation structure, improve wording, and identify
test cases. Suggestions were checked against the implementation before being
included. The project code and final technical decisions remain the authors'
work.
