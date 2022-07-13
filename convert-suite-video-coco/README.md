# Convert Suite Export to Other Dataset Formats

## Pre-requisite

- Python 3.6+
- Install python dependencies

```
$ pip install -r requirements.txt
```

## Dataset format / annotation type supports

### Datasets

- COCO
- (WIP: Pascal VOC, YOLO)

### Annotation types

- Bounding box, Polygon segmentation, Rotated Box, Keypoints
  - Please note that RLE segmentation output is compressed RLE string. It's also supported through cocoapi
  - COCO stuff segmentation task uses compressed RLE string.
  - Please note that since COCO does not have a Rotated Box, we turn our Rotated Box into Polygon format
- (WIP: categorization)

## Convert Export Results

- Please download and extract exported zip file. You can use sample export zip file from Export Guide page.
- User manual for export: https://docs.superb-ai.com/user-manual/manipulate-labels/export-and-download-labels

```
$ python convert.py --export-dir {EXPORT_DIR} --output-path {OUTPUT_PATH} --dataset-type COCO
```

## Notes

### RLE

- use pycocotools to decode compressed RLE
  - https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/coco.py#L268
