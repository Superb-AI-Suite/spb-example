import os
import json
from pathlib import Path
from collections import defaultdict


def process(args):
    images_dir, annotations_path = args.images_dir, args.annotations_path
    num_classes = args.num_classes

    # Load annotation JSON
    with open(annotations_path) as f:
        data = json.load(f)
        images = data['images']
        categories = data['categories']
        annotations = data['annotations']

    # Load image infos
    image_infos = {
        image_info['id']: {
            'file_name': image_info['file_name']
        }
        for image_info in images
    }

    # Load class (category) infos
    class_infos = {
        class_info['id']: {
            'name': class_info['name']
        }
        for class_info in categories
    }

    # Choose N most frequent classes
    class_counts = defaultdict(int)
    for anno in annotations:
        class_counts[anno['category_id']] += 1
    class_counts = sorted([(k, v) for k, v in class_counts.items()], key=lambda x: -x[1])
    if num_classes == 0: num_classes = len(class_counts)
    selected_class_ids = [k for k, _ in class_counts[:num_classes]]
    print('Please create project with this class names:',
          [class_infos[k]['name'] for k in selected_class_ids])

    # Prep for upload
    image_annos = defaultdict(list)
    for anno in annotations:
        class_id = anno['category_id']
        if class_id not in selected_class_ids:
            continue
        image_name = image_infos[anno['image_id']]['file_name']
        bbox = anno['bbox']
        image_annos[image_name].append({
            'class_name': class_infos[class_id]['name'],
            'annotation': {
                'coord': {
                    'x': bbox[0],
                    'y': bbox[1],
                    'width': bbox[2],
                    'height': bbox[3]
                }
            }
        })
    with open('upload-info.json', 'w') as f:
        json.dump(
            {
                'image_file_dir': str(images_dir),
                'images': [
                    {
                        'image_name': k,
                        'annotations': v
                    }
                    for k, v in image_annos.items()
                ]
            }, f
        )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--images-dir',
        type=Path,
        default=os.path.join('data', 'val2017'))
    parser.add_argument(
        '--annotations-path',
        type=Path,
        default=os.path.join('data', 'annotations', 'instances_val2017.json'))
    parser.add_argument(
        '--num-classes',
        type=int,
        default=5,
        help='Set to 0 if you want to use all classes')
    args = parser.parse_args()
    process(args)
