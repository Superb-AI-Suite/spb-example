# Convert Suite Export to format to upload labels through Superb AI CLI to Suite

## Pre-requisite

- Python 3.6+
- Install python dependencies

```
$ pip install -r requirements.txt
```

## Dataset format / annotation type supports

### Datasets

- Superb AI Suite export

### Annotation types

- Supports any annotation type that the Superb AI Suite supports

## Convert Export Results

- You should set the output path to represent a folder that you want to upload from.
  - You can then from that folder upload to Superb AI Suite.
  - User manual for CLI upload: https://docs.superb-ai.com/developers/command-line-interface/uploading-raw-data-and-labels
- Please download and extract exported zip file. You can use sample export zip file from Export Guide page.
- User manual for export: https://docs.superb-ai.com/user-manual/manipulate-labels/export-and-download-labels

```
$ python convert.py --export-dir {EXPORT_DIR} --output-path {OUTPUT_PATH}
```
