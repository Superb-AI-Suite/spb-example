# Convert Suite CLI Downloads to Other Dataset Formats

## Pre-requisite
* Python 3.6+
* Install python dependencies
```
$ pip install -r requirements.txt
```

## Dataset format / annotation type supports
### Datasets
* COCO
* (WIP: Pascal VOC, YOLO)
### Annotation types
* Bounding box, Polygon segmentation
    * Please note that RLE segmentation output is compressed RLE string. It's also supported through cocoapi
    * COCO stuff segmentation task uses compressed RLE string.
* (WIP: Keypoints, categorization)
* NOTE: deprecated image annotation app is not supported

## Convert CLI Downloads
* Download your Suite project using Suite CLI (link)[https://docs.superb-ai.com/reference/downloading-data-labels]
```
# configure spb cli first, refer to the guide above
$ mkdir data; cd data
$ spb download
# this will create project.json and image/label JSON files under "data" directory
```

* Run converting code
```
$ python convert.py --download-dir data --dataset-type COCO
```

* Check result with sample codes (optional)
    * Run jupyter notebook under "viz" directory

## Notes
### RLE
* use pycocotools to decode compressed RLE
    * https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/coco.py#L268
