# Convert Exported Polygon segmentation to Bitmask segmentation
* Convert Polygons from Image, Video Project

## Prerequisite
* Install python dependencies
```
$ pipenv install
```
* WIP: Docker version

## Convert Export Result
* Download export result in Export History Tab [Link](https://docs.superb-ai.com/user-manual/manipulate-labels/export-and-download-labels)
   * Sample export results for image and video are given in [exports](exports) folder
* [Export Result format](https://docs.superb-ai.com/user-manual/manipulate-labels/export-result-format)
    * Mask was also included in exported zip files but that function will be deprecated.
    * Use this code to create masks.
* Note! - Only labels submitted through [our annotations apps](https://docs.superb-ai.com/user-manual/manage-annotations/create-edit-delete-annotations#create-annotations) are available, this code will skip invalid labels.
* Color map is hard-coded, check code to change colors - Mask images will have different color compared to our detailed view or annotation app.
   * This is because our mask uses 8-bit color map to represent pixel values from 0 to 255
   * class and instance index starts from 1 w.r.t. 'object_classes' in project.json or 'objects' in label JSON

### Image (New) Project
```
# Change "image-sample" to your exported file name
# Unzip your exported file
$ cd exports; unzip image-sample.zip; cd ..
# run code
$ cd src
$ python main.py --path ../exports/image-sample
```

* masks will be saved under given directory
```
image-sample
└─ project.json              # projects.json, labels, meta existed before
└─ labels
└─ meta
└─ masks                     # masks directory is created
   └─ classId
      └─ {group-name}        # classes without group will skip this directory
         └─ {label-id}.png
            ...
         ...
   └─ instanceId             # same structure as classId
```

### Video Project 
```
# Change "video-sample" to your exported file name
# Unzip your exported file
$ cd exports; unzip video-sample.zip; cd ..
# run code
$ cd src
$ python main.py --path ../exports/video-sample
```

* masks will be saved under given directory
```
video-sample
└─ project.json              # projects.json, labels, meta existed before
└─ labels
└─ meta
└─ masks                     # masks directory is created
   └─ classId
      └─ {group-name}        # classes without group will skip this directory
         └─ {label-id}
            └─ 00000000.png
            ├─ 00000001.png
               ...
            ...
         ...
   └─ instanceId             # same structure as classId
```
