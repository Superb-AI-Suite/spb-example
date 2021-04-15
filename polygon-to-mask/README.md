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
* [Export Result format](https://docs.superb-ai.com/user-manual/manipulate-labels/export-result-format)
    * Note that masks are only given in legacy project.
    * Use this code to create mask images.
* Note! - Only labels submitted through [our annotations apps](https://docs.superb-ai.com/user-manual/manage-annotations/create-edit-delete-annotations#create-annotations) are available, this code will skip invalid labels.
* Color map is fixed - Masks will have different color map compared to colors from our detailed view or annotation app.
    * We support custom class / object color in our app, but it's not suitable for training data.
    * Each pixel will have values between 0 ~ 255
        * class and instance index starts from 1 w.r.t. 'object_classes' in project.json or 'objects' in label JSON

### Image (New) Project
```
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
         └─ {label-id}.json
            ...
         ...
   └─ instanceId             # same structure as classId
```

### Video Project 
```
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
