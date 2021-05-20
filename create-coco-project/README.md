# Create New Suite Project with COCO Dataset
* With the COCO dataset, start your own Suite project.

## Pre-requisite
* Python 3.6+
```
$ pip install -r requirements.txt
```

## Data Preparation
```
# This will create data/ directory
$ bash download-coco.sh
```

## Convert COCO to Suite SDK Format
* We'll sample 5 most frequent classes in COCO validation 2017 dataset.
* This time we'll handle bounding box annotations only, but Suite can also handle polygons and keypoints.
```
# This will create upload-info.json
$ python convert.py
```

## Create Project in Suite
* [Official Guide to Create a Project](https://docs.superb-ai.com/user-manual/custom-project/create-a-new-project)
* Creating projects via SDK is WIP. So this time we'll create a project in web.
* Set any project name you want, but you have to match class names as COCO class name
    * By default converting code, you will have to set 5 classes ['person', 'car', 'chair', 'book', 'bottle']

## Upload via SDK
* After you finish creating a project, you may start uploading your data
```
$ python upload.py --project {PROJECT_NAME} --dataset {DATASET_NAME}
```
* Check your uploaded dataset via Suite web page
