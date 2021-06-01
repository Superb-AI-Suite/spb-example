# Suite to Other Datasets

## Pre-requisite
* Python 3.6+
* Install python dependencies
```
$ pip install -r requirements.txt
```

## Dataset format / annotation type supports
* Supported Datasets
    * COCO Dataset
* WIP
    * Pascal VOC
    * YOLO
* Supported annotation types: bounding box, polygon segmentation
    * WIP: Keypoints, categorization

## Convert Export Results
* Please download and extract exported zip file before.
* User manual for export: https://docs.superb-ai.com/user-manual/manipulate-labels/export-and-download-labels
```
$ python convert.py --export-dir {EXPORT_DIR} --output-path {OUTPUT_PATH} --dataset-type COCO
```
