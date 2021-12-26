# bencode-nuo

[![python: 3.9](https://img.shields.io/badge/python-3.9-b58900.svg)](https://docs.python.org/3/whatsnew/3.9.html)
[![test: pytest](https://img.shields.io/badge/test-pytest-93a1a1.svg)](https://github.com/pytest-dev/pytest)
[![style: black](https://img.shields.io/badge/style-black-002b36.svg)](https://github.com/python/black)
[![style: isort](https://img.shields.io/badge/style-isort-2aa198.svg)](https://github.com/timothycrosley/isort)
[![typing: mypy](https://img.shields.io/badge/typing-mypy-d33682.svg)](https://github.com/python/mypy)
[![package: conda](https://img.shields.io/badge/package-conda-859900.svg)](https://artifactory.us.akuna.dev/artifactory/conda-dev/)


Simple bencode parser for Python

## Usage

**Encode:**
```python

>>> encode({'title': 'Example'})
b'd5:title7:Examplee'

>>> encode(12)
b'i12e'
```

**Decode:**
```python

>>> encode({'title': 'Example'})
b'd5:title7:Examplee'

>>> encode(12)
b'i12e'
```

## Install


## Torrents

```python
with open('path/to/file.torrent', "rb") as file:
    content = file.read()
print(decode(content))
```