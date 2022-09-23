import os
from pathlib import Path

import simplejson as json

from utils.reader_for_yolo import read_labels, read_meta, read_project


def to_yolo(
    output_path: str,
    meta_json_list: list,
    label_json: dict,
    project_json: dict,
):
    (project_type, categories), is_video = read_project(project_json)

    meta_map = {}
    for meta in meta_json_list:
        meta_map[(meta["dataset"], meta["data_key"])] = meta
    images, labels, frame_index_cutter = read_meta(meta_map, is_video)
    for label_id in list(labels.keys()):
        labels[label_id]["label"] = label_json[
            os.path.join("labels", label_id) + ".json"
        ]
    yolo_annotations = read_labels(
        labels, project_type, categories, images, frame_index_cutter, is_video
    )

    category_path = os.path.join(output_path, "category_map.json")
    Path(category_path).parents[0].mkdir(parents=True, exist_ok=True)
    with open(category_path, "w") as f:
        json.dump(categories, f)
    for annotation in yolo_annotations:
        data_path = annotation["file_name"] + ".txt"
        points_label = annotation["annotations"]
        annotation_path = os.path.join(output_path, data_path)
        Path(annotation_path).parents[0].mkdir(parents=True, exist_ok=True)
        with open(annotation_path, "w") as f:
            f.write("# class x_center y_center width height")
            for p_label in points_label:
                category_id = p_label["category_id"]
                bbox = p_label["bbox"]
                f.write("\n" + str(category_id))
                for box_point in bbox:
                    f.write(" " + str(box_point))
