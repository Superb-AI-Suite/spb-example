from decimal import ROUND_DOWN, Decimal
from pathlib import Path

import semver

from .suite_convert import (
    bbox_to_yolo_bbox,
    multi_polygon_to_yolo_bbox,
    polygon_to_yolo_bbox,
)


def read_project(project_json):
    project_type = project_json.get("type")
    is_video = False

    if project_type == "image-siesta":
        return read_siesta_project(project_json, "object_detection"), is_video
    elif project_type == "video-siesta":
        is_video = True
        return read_siesta_project(project_json, "object_tracking"), is_video
    elif project_type == "image-default":
        raise NotImplementedError


def read_siesta_project(project_json: dict, obj_type: str):
    if semver.compare(project_json["version"], "0.4.0") < 0:
        project_type = "siesta-v1"
    else:
        project_type = "siesta-v2"
    object_class_to_group_name = {
        o_id: g["name"]
        for g in project_json[obj_type]["object_groups"]
        for o_id in g["object_class_ids"]
    }
    categories = []
    for o in project_json[obj_type]["object_classes"]:
        if o["annotation_type"] in ["box", "polygon"]:
            categories.append(
                {
                    "id": len(categories) + 1,
                    "name": o["name"],
                    "supercategory": object_class_to_group_name.get(o["id"]),
                }
            )
        elif o["annotation_type"] in ["polyline"]:
            print("skipping polyline")
        elif o["annotation_type"] in ["keypoint"]:
            print("skipping keypoints")
    return project_type, categories


def read_meta(meta_map, is_video):
    images = []
    labels = {}
    image_count = 0
    frame_index_cutter = []
    frame_index_cutter.append(0)
    if is_video:
        for (dataset, data_key), meta in meta_map.items():
            image_ids = []
            for frame in meta["frames"]:
                images.append(
                    {
                        "id": image_count,
                        "dataset": dataset,
                        "file_name": str(Path(dataset) / data_key / frame),
                    }
                )
                image_ids.append(image_count)
                image_count += 1
            labels[meta["label_id"]] = {"image_id": image_ids}
            frame_index_cutter.append(image_count)
    else:
        for idx, ((dataset, data_key), meta) in enumerate(meta_map.items()):
            images.append(
                {
                    "id": idx,
                    "dataset": dataset,
                    "file_name": str(Path(dataset) / data_key),
                }
            )
            labels[meta["label_id"]] = {"image_id": idx}
    return images, labels, frame_index_cutter


def read_labels(labels, project_type, categories, images, frame_index_cutter, is_video):
    annotations = []
    image_map = {i["id"]: i for i in images}
    category_map = {c["name"]: c["id"] for c in categories}
    label_count = 0
    num_labels = len(labels)
    for i, (label_id, label_info) in enumerate(labels.items()):
        print("Reading..." + f" (converting progress: {i+1}/{num_labels})")
        image_id, label = label_info["image_id"], label_info["label"]
        if project_type == "death-valley":
            raise NotImplementedError
        elif project_type in ["siesta-v1", "siesta-v2"]:
            if label:
                annotations_in_label, nums = read_siesta_label(
                    label,
                    project_type,
                    category_map,
                    label_count,
                    frame_index_cutter,
                    is_video,
                )
            else:
                continue
        else:
            raise NotImplementedError
        for idx, anno in enumerate(annotations_in_label):
            if is_video:
                image_id = nums[idx]
            anno["bbox"] = [
                Decimal(x).quantize(Decimal(".001"), rounding=ROUND_DOWN)
                for x in anno["bbox"]
            ]
        annotations.append(
            {
                "id": len(annotations_in_label) + 1,
                "image_id": image_id,
                "file_name": image_map[image_id]["file_name"],
                "dataset": image_map[image_id]["dataset"],
                "annotations": annotations_in_label,
            }
        )

        label_count += 1
    return annotations


def read_siesta_label(
    label, project_type, category_map, label_count, frame_index_cutter, is_video
):
    if project_type == "siesta-v1":
        ANNO_KEY = "annotationType"
        CLASS_NAME_KEY = "className"
    else:
        ANNO_KEY = "annotation_type"
        CLASS_NAME_KEY = "class_name"
    nums = []
    annotations = []

    for o in label["objects"]:
        if is_video:
            frames = o["frames"]
        else:
            frames = [
                {"num": 0, "annotation": o["annotation"], "properties": o["properties"]}
            ]
        for frame in frames:
            if is_video:
                nums.append(frame["num"] + frame_index_cutter[label_count])
            if o[ANNO_KEY] == "box" or o[ANNO_KEY] == "polygon":
                if o[ANNO_KEY] == "box":
                    c = frame["annotation"]["coord"]
                    bbox = bbox_to_yolo_bbox(c)
                elif o[ANNO_KEY] == "polygon":
                    p = frame["annotation"]["coord"]["points"]
                    if frame["annotation"].get("multiple", False):
                        bbox = multi_polygon_to_yolo_bbox(p)
                    else:
                        bbox = polygon_to_yolo_bbox(p)
                annotations.append(
                    {
                        "category_id": category_map[o[CLASS_NAME_KEY]],
                        "bbox": bbox,
                    }
                )
            else:
                continue
    return annotations, nums
