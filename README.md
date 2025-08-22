# loudstream

A file-streaming Python API around [libebur128](https://github.com/jiixyj/libebur128/tree/master/ebur128).

## Install

```bash
pip install loudstream

# OR

uv add loudstream
```

## Usage

```python
from loudstream import Meter

lufs, peak = Meter().measure("some-file.wav")
```

## Running Tests

```bash
uv venv
uv pip install .
uv run pytest -v
```

