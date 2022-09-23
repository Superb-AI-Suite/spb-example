import os
from datetime import datetime
from pathlib import Path

import simplejson as json

from utils.reader_for_coco import read_labels, read_meta, read_project


def to_coco(
    output_path: str,
    meta_json_list: list,
    label_json: dict,
    project_json: dict,
):
    (project_type, seg_categories, kp_categories), is_video = read_project(project_json)

    meta_map = {}
    for meta in meta_json_list:
        meta_map[(meta["dataset"], meta["data_key"])] = meta
    images, labels, frame_index_cutter = read_meta(meta_map, is_video)

    for label_id in list(labels.keys()):
        labels[label_id]["label"] = label_json[
            os.path.join("labels", label_id) + ".json"
        ]
    seg_annotations, kp_annotations = read_labels(
        labels,
        project_type,
        seg_categories,
        kp_categories,
        images,
        frame_index_cutter,
        is_video,
    )

    seg_result = {
        "info": {
            "description": "Exported from Superb AI Suite",
            "contributor": "Superb AI",
            "url": "https://www.superb-ai.com/",
            "date_created": str(datetime.now().isoformat()),
        },
        "licenses": [],
        "categories": seg_categories,
        "images": images,
        "annotations": seg_annotations,
    }
    kp_result = {
        "info": {
            "description": "Exported from Superb AI Suite",
            "contributor": "Superb AI",
            "url": "https://www.superb-ai.com/",
            "date_created": str(datetime.now().isoformat()),
        },
        "licenses": [],
        "categories": kp_categories,
        "images": images,
        "annotations": kp_annotations,
    }

    seg_output_path = os.path.join(output_path, "segmentation_instances.json")
    Path(seg_output_path).parents[0].mkdir(parents=True, exist_ok=True)
    with open(Path(seg_output_path), "w", encoding="utf-8") as f:
        json.dump(seg_result, f)

    kp_output_path = os.path.join(output_path, "keypoint_instances.json")
    Path(kp_output_path).parents[0].mkdir(parents=True, exist_ok=True)
    with open(Path(kp_output_path), "w", encoding="utf-8") as f:
        json.dump(kp_result, f)
