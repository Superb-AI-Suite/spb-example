from coco import to_coco
from config import dataset_convert_choices
from utils.export_parser import parse_export_zip_file
from yolo import to_yolo


def process(args):
    export_path, output_path, dataset_type = (
        args.export_path,
        args.output_path,
        args.dataset_type,
    )

    meta_json_list, label_json, project_json = parse_export_zip_file(export_path)

    assert dataset_type in dataset_convert_choices

    if dataset_type == "COCO":
        to_coco(
            output_path=output_path,
            meta_json_list=meta_json_list,
            label_json=label_json,
            project_json=project_json,
        )
    elif dataset_type == "YOLO":
        to_yolo(
            output_path=output_path,
            meta_json_list=meta_json_list,
            label_json=label_json,
            project_json=project_json,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--export-path",
        type=str,
        required=True,
        help="directory of export zip file",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="converted_result",
        help="output path to save converted dataset",
    )
    parser.add_argument(
        "--dataset-type", type=str, default="COCO", choices=dataset_convert_choices
    )
    args = parser.parse_args()
    process(args)
