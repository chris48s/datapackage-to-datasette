# datapackage-to-datasette

[![Run tests](https://github.com/chris48s/datapackage-to-datasette/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/chris48s/datapackage-to-datasette/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/chris48s/datapackage-to-datasette/branch/master/graph/badge.svg?token=6EPIKL61VO)](https://codecov.io/gh/chris48s/datapackage-to-datasette)
[![PyPI Version](https://img.shields.io/pypi/v/datapackage-to-datasette.svg)](https://pypi.org/project/datapackage-to-datasette/)
![License](https://img.shields.io/pypi/l/datapackage-to-datasette.svg)
![Python Compatibility](https://img.shields.io/badge/dynamic/json?query=info.requires_python&label=python&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fdatapackage-to-datasette%2Fjson)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

Import Frictionless Data
[Datapackage](https://frictionlessdata.io/data-package/)s
into SQLite and generate
[Datasette metadata](https://datasette.readthedocs.io/en/stable/metadata.html).

## Setup

```sh
pip install datapackage-to-datasette
```

## Usage

### On the console

Import a datapackage from a local file

```sh
datapackage-to-datasette mydatabase.db /path/to/datapackage.json metadata.json
```

or from a URL

```sh
datapackage-to-datasette mydatabase.db https://pkgstore.datahub.io/core/co2-ppm/10/datapackage.json metadata.json
```

If the datasette metadata file already exists, you can pass
`--write-mode replace` or `--write-mode merge` to overwrite
or merge with the existing datasette metadata file.

### As a library

```py
from datapackage_to_datasette import datapackage_to_datasette, DataImportError

try:
    datapackage_to_datasette(
        'mydatabase.db',
        '/path/to/datapackage.json',
        'metadata.json',
        write_mode='replace'
    )
except DataImportError:
    raise
```
