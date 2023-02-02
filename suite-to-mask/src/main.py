import os
import json
import glob
import tqdm

from exceptions import ProjectTypeError
from utils.mask import create_mask


def process(path):
    project_path = os.path.join(path, "project.json")
    with open(project_path, "r", encoding="utf-8") as f:
        project_info = json.load(f)
    try:
        data_type = project_info["data_type"]
        assert data_type in ["image", "image sequence"]
    except (KeyError, AssertionError):
        raise ProjectTypeError("Legacy projects are not supported")
    data_type = project_info.get("type", "image-default")
    meta_dir = os.path.join(path, "meta", "**", "*.json")
    for meta_path in tqdm.tqdm(glob.glob(meta_dir, recursive=True)):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        image_info = meta["image_info"]
        dataset, data_key = meta["dataset"], meta["data_key"]
        if "width" not in image_info:
            print(
                f"[WARNING, {dataset}/{data_key}] skipped: Image info does not exist, please submit through our annotation app"
            )
            continue
        label_id = meta["label_id"]
        label_path = os.path.join(path, "labels", f"{label_id}.json")
        with open(label_path, "r", encoding="utf-8") as f:
            label = json.load(f)

        mask_dir = os.path.join(path, "masks")
        create_mask(data_type, project_info, image_info, label_id, label, mask_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", type=str, required=True, help="path to unzipped export result"
    )
    args = parser.parse_args()
    try:
        process(path=args.path)
    except Exception as e:
        print(e)
