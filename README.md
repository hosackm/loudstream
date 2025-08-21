# loudstream

A file-streaming Python API around [libebur128](https://github.com/jiixyj/libebur128/tree/master/ebur128).

## Install

```bash
uv sync
```

## Usage

```python
from loudstream import Meter

lufs, peak = Meter().measure("some-file.wav")
```

## Running Tests

```bash
uv run pytest
```

