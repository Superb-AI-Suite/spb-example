from pathlib import Path
import simplejson as json
from datetime import datetime

from utils.reader import read_project, read_meta, read_labels
from utils.video_to_image import read_vti


def process(args):
    export_dir, output_path = args.export_dir, args.output_path
    with open(Path(export_dir) / 'project.json', 'r', encoding='utf-8') as f:
        project_json = json.load(f)
    project_type, categories = read_project(project_json)
    print(project_type)
    print(categories)
    meta_map = {}
    is_video = False
    for p in Path(export_dir, 'meta').rglob('*.json'):
        with open(p, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta_map[(meta['dataset'], meta['data_key'])] = meta
        if 'frames' in meta:
            is_video = True
            print("hererer")
    if is_video == False:
        images, labels = read_meta(meta_map)
        for label_id in list(labels.keys()):
            with open(Path(export_dir) / 'labels' / f'{label_id}.json', 'r', encoding='utf-8') as f:
                labels[label_id]['label'] = json.load(f)
        annotations = read_labels(labels, project_type, categories, images)
    if is_video == True:
        new_project_path, new_project_json, new_meta_dict, new_label_dict = read_vti(
            meta_map, project_json)
        images, labels = read_meta(new_meta_dict)
        project_type = 'siesta-v2'
        for label_id in list(labels.keys()):
            labels[label_id]['label'] = new_label_dict[label_id]
        annotations = read_labels(labels, project_type, categories, images)

    result = {
        'info': {
            'description': "Exported from Superb AI Suite",
            'contributor': "Superb AI",
            'url': "https://www.superb-ai.com/",
            'date_created': str(datetime.now().isoformat())
        },
        'licenses': [],
        'categories': categories,
        'images': images,
        'annotations': annotations
    }
    Path(output_path).parents[0].mkdir(parents=True, exist_ok=True)
    with open(Path(output_path), 'w', encoding='utf-8') as f:
        json.dump(result, f)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--export-dir', type=str, required=True,
                        help='directory of unzipped export result')
    parser.add_argument('--output-path', type=str, default='instance.json',
                        help='output path to save converted dataset')
    parser.add_argument('--dataset-type', type=str,
                        default='COCO', choices=['COCO'])
    args = parser.parse_args()
    process(args)
