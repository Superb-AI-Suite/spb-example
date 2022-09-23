from decimal import ROUND_DOWN, Decimal
from pathlib import Path

import semver

from .suite_convert import (convert_keypoint_to_coco,
                            convert_multi_polygon_to_coco,
                            convert_polygon_to_coco, to_coco_multi_polygon,
                            to_coco_polygon)


def read_project(project_json):
    project_type = project_json.get("type")
    is_video = False
    if project_type == "image-siesta":
        return read_siesta_project(project_json, "object_detection"), is_video
    elif project_type == "video-siesta":
        is_video = True
        return read_siesta_project(project_json, "object_tracking"), is_video
    elif project_type == "image-default":
        return read_death_valley_project(project_json), is_video
    raise NotImplementedError


def read_siesta_project(project_json, obj_type):
    if semver.compare(project_json["version"], "0.4.0") < 0:
        project_type = "siesta-v1"
    else:
        project_type = "siesta-v2"
    object_class_to_group_name = {
        o_id: g["name"]
        for g in project_json[obj_type]["object_groups"]
        for o_id in g["object_class_ids"]
    }
    seg_categories = []
    kp_categories = []
    for o in project_json[obj_type]["object_classes"]:
        if o["annotation_type"] in ["box", "polygon", "polyline"]:
            seg_categories.append(
                {
                    "id": len(seg_categories) + 1,
                    "name": o["name"],
                    "supercategory": object_class_to_group_name.get(o["id"]),
                }
            )
        elif o["annotation_type"] in ["keypoint"]:
            points = project_json[obj_type]["keypoints"][len(kp_categories)]["points"]
            edges = project_json[obj_type]["keypoints"][len(kp_categories)]["edges"]
            kp_categories.append(
                {
                    "id": len(kp_categories) + 1,
                    "name": o["name"],
                    "supercategory": object_class_to_group_name.get(o["id"]),
                    "keypoints": [point["name"] for point in points],
                    "skeleton": [[edge["u"], edge["v"]] for edge in edges],
                }
            )
    return project_type, seg_categories, kp_categories


def read_death_valley_project(project_json):
    object_class_to_group_name = {
        o_name: g["name"]
        for g in project_json["groups"]
        for o_name in g["info"]["classes"]
    }
    categories = []
    for o in project_json["objects"]:
        shapes = list(o["info"]["shapes"].keys())
        if shapes[0] in ["box", "polygon"]:
            categories.append(
                {
                    "id": o["class_id"],
                    "name": o["class_name"],
                    "supercategory": object_class_to_group_name.get(o["class_name"]),
                }
            )
    return "death-valley", categories


def read_meta(meta_map, is_video):
    images = []
    labels = {}
    image_count = 0
    frame_index_cutter = []
    frame_index_cutter.append(0)
    if is_video:
        for (dataset, data_key), meta in meta_map.items():
            if "height" not in meta["image_info"] or "width" not in meta["image_info"]:
                raise Exception(
                    "Only labels annotated through annotation app is supported."
                )
            image_ids = []
            for frame in meta["frames"]:
                images.append(
                    {
                        "id": image_count,
                        "license": None,
                        "dataset": dataset,
                        "file_name": str(Path(dataset) / data_key / frame),
                        "height": meta["image_info"]["height"],
                        "width": meta["image_info"]["width"],
                        "date_captured": None,
                    }
                )
                image_ids.append(image_count)
                image_count += 1
            labels[meta["label_id"]] = {"image_id": image_ids}
            frame_index_cutter.append(image_count)
    else:
        for idx, ((dataset, data_key), meta) in enumerate(meta_map.items()):
            if "height" not in meta["image_info"] or "width" not in meta["image_info"]:
                raise Exception(
                    "Only labels annotated through annotation app is supported."
                )
            images.append(
                {
                    "id": idx,
                    "license": None,
                    "dataset": dataset,
                    "file_name": data_key,
                    "height": meta["image_info"]["height"],
                    "width": meta["image_info"]["width"],
                    "date_captured": None,
                }
            )
            labels[meta["label_id"]] = {"image_id": idx}
    return images, labels, frame_index_cutter


def read_labels(
    labels,
    project_type,
    seg_categories,
    kp_categories,
    images,
    frame_index_cutter,
    is_video,
):
    seg_annotations = []
    kp_annotations = []
    image_map = {i["id"]: i for i in images}
    categories = seg_categories + kp_categories

    category_map = {c["name"]: c["id"] for c in categories}
    label_count = 0  # for vided frame count
    num_labels = len(labels)
    for i, (label_id, label_info) in enumerate(labels.items()):
        print("Analyzing..." + f" (converting progress: {i+1}/{num_labels})")
        image_id, label = label_info["image_id"], label_info["label"]
        if project_type == "death-valley":
            raise NotImplementedError
        elif project_type in ["siesta-v1", "siesta-v2"]:
            if label:
                (
                    seg_annotations_in_label,
                    kp_annotations_in_label,
                    nums,
                ) = read_siesta_label(
                    label,
                    project_type,
                    category_map,
                    image_map,
                    image_id,
                    frame_index_cutter,
                    label_count,
                    is_video,
                )
            else:  # current label has no submitted or ongoing annotations
                continue
        else:
            raise NotImplementedError
        for idx, anno in enumerate(seg_annotations_in_label):
            if is_video:
                image_id = nums[idx]
            if (
                anno.get("segmentation") is not None
                and "counts" not in anno["segmentation"]
            ):
                anno["segmentation"] = [
                    [
                        Decimal(x).quantize(Decimal(".01"), rounding=ROUND_DOWN)
                        for x in anno["segmentation"]
                    ]
                ]
            anno["bbox"] = [
                Decimal(x).quantize(Decimal(".01"), rounding=ROUND_DOWN)
                for x in anno["bbox"]
            ]
            anno["area"] = Decimal(anno["area"]).quantize(
                Decimal(".01"), rounding=ROUND_DOWN
            )
            seg_annotations.append(
                {
                    "id": len(seg_annotations) + 1,
                    "image_id": image_id,
                    "iscrowd": 0,
                    **anno,
                }
            )
        for anno in kp_annotations_in_label:
            if is_video:
                image_id = nums[idx]
            anno["bbox"] = [
                Decimal(x).quantize(Decimal(".01"), rounding=ROUND_DOWN)
                for x in anno["bbox"]
            ]
            anno["area"] = Decimal(anno["area"]).quantize(
                Decimal(".01"), rounding=ROUND_DOWN
            )
            anno["keypoints"] = [
                Decimal(x).quantize(Decimal(".01"), rounding=ROUND_DOWN)
                for x in anno["keypoints"]
            ]
            if anno.get("segmentation") is not None:
                seg = []
                for s in anno["segmentation"]:
                    inner_seg = []
                    for x in s:
                        inner_seg.append(
                            Decimal(x).quantize(Decimal(".01"), rounding=ROUND_DOWN)
                        )
                    seg.append(inner_seg)
                anno["segmentation"] = seg

            kp_annotations.append(
                {
                    "id": len(kp_annotations) + 1,
                    "image_id": image_id,
                    "iscrowd": 0,
                    **anno,
                }
            )
        label_count += 1
    return seg_annotations, kp_annotations


def read_siesta_label(
    label,
    project_type,
    category_map,
    image_map,
    image_id,
    frame_index_cutter,
    label_count,
    is_video,
):
    if project_type == "siesta-v1":
        ANNO_KEY = "annotationType"
        CLASS_NAME_KEY = "className"
    else:
        ANNO_KEY = "annotation_type"
        CLASS_NAME_KEY = "class_name"
    nums = []
    seg_annotations = []
    kp_annotations = []
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
                image = image_map[image_id[frame["num"]]]
            else:
                image = image_map[image_id]
            if o[ANNO_KEY] == "box" or o[ANNO_KEY] == "polygon":
                if o[ANNO_KEY] == "box":
                    c = frame["annotation"]["coord"]
                    bbox = [c["x"], c["y"], c["width"], c["height"]]
                    area = c["width"] * c["height"]
                    segmentation, rle = None, None
                elif o[ANNO_KEY] == "polygon":
                    if frame["annotation"].get("multiple", False):
                        bbox, area, _, rle = convert_multi_polygon_to_coco(
                            frame["annotation"]["coord"]["points"], image
                        )
                    else:
                        bbox, area, segmentation, rle = convert_polygon_to_coco(
                            frame["annotation"]["coord"]["points"], image
                        )
                seg_annotations.append(
                    {
                        "category_id": category_map[o[CLASS_NAME_KEY]],
                        "bbox": bbox,
                        "area": area,
                        "segmentation": rle,
                        # 'segmentation': segmentation,
                    }
                )
            elif o[ANNO_KEY] == "keypoint":
                (
                    bbox,
                    area,
                    segmentation,
                    keypoints,
                    num_keypoints,
                ) = convert_keypoint_to_coco(
                    frame["annotation"]["coord"]["points"], image
                )
                kp_annotations.append(
                    {
                        "category_id": category_map[o[CLASS_NAME_KEY]],
                        "bbox": bbox,
                        "area": area,
                        "segmentation": segmentation,
                        "keypoints": keypoints,
                        "num_keypoints": num_keypoints,
                    }
                )
            else:
                continue
    return seg_annotations, kp_annotations, nums
