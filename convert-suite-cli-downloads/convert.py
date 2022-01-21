from pathlib import Path
import simplejson as json
from datetime import datetime

from utils.reader import read_project, read_images, read_labels


def process(args):
    download_dir, output_path = args.download_dir, args.output_path
    with open(Path(download_dir) / 'project.json', 'r', encoding='utf-8') as f:
        project_json = json.load(f)
    _, categories = read_project(project_json)

    meta_map = {}
    for p in Path(download_dir).rglob('*.json'):
        rel_path = str(Path(p).relative_to(download_dir))
        if rel_path == 'project.json':
            continue
        with open(p, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta_map[(meta['dataset'], meta['data_key'])] = (meta, str(p))

    images = read_images(meta_map)
    annotations = read_labels(images, categories, meta_map)

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
    parser.add_argument('--download-dir', type=str, required=True, help='Directory where you executed spb download')
    parser.add_argument('--output-path', type=str, default='instance.json', help='output path to save converted dataset')
    parser.add_argument('--dataset-type', type=str, default='COCO', choices=['COCO'])
    args = parser.parse_args()
    process(args)
