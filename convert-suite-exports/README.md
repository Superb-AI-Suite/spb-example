# Convert Suite Export to Other Dataset Formats

## Pre-requisite
* Python 3.6+
* Install python dependencies
```
$ pip install -r requirements.txt
```

## Dataset format / annotation type supports
### Datasets
* COCO, YOLO
* (WIP: Pascal VOC)
### Annotation types
* Bounding box, Polygon segmentation
    * Please note that RLE segmentation output is compressed RLE string. It's also supported through cocoapi
    * COCO stuff segmentation task uses compressed RLE string.
* (WIP: Keypoints, categorization)

## Convert Export Results
* Please download and extract exported zip file. You can use sample export zip file from Export Guide page.
* User manual for export: https://docs.superb-ai.com/user-manual/manipulate-labels/export-and-download-labels
```
$ python convert.py --export-path {EXPORT_PATH} --output-path {OUTPUT_PATH} --dataset-type COCO
$ python convert.py --export-path {EXPORT_PATH} --output-path {OUTPUT_PATH} --dataset-type YOLO
```

## Notes
### RLE
* use pycocotools to decode compressed RLE
    * https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/coco.py#L268
