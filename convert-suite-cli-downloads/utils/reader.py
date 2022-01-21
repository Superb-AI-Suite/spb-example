import semver
from PIL import Image, ImageDraw
import numpy as np
from decimal import Decimal, ROUND_DOWN


def read_project(project_json):
    project_type = project_json.get('type')
    if project_type != 'image-siesta':
        raise NotImplementedError("Only the latest version of our annotation app")
    if semver.compare(project_json['version'], '0.4.0') < 0:
        raise NotImplementedError

    object_class_to_group_name = {
        o_id: g['name']
        for g in project_json['object_detection']['object_groups']
            for o_id in g['object_class_ids']
    }
    categories = []
    for o in project_json['object_detection']['object_classes']:
        if o['annotation_type'] in ['box', 'polygon']:
            categories.append({
                'id': len(categories) + 1,
                'name': o['name'],
                'supercategory': object_class_to_group_name.get(o['id'])
            })
    return project_type, categories


def read_images(meta_map):
    images = []
    for idx, ((dataset, data_key), (meta, json_path)) in enumerate(meta_map.items()):
        image_path = json_path[:-5]
        image = Image.open(image_path)
        width, height = image.size
        images.append({
            'id': idx,
            'license': None,
            'dataset': dataset,
            'file_name': data_key,
            'height': height,
            'width': width,
            'date_captured': None,
        })
    return images


def read_labels(images, categories, meta_map):
    annotations = []
    category_map = {c['name']: c['id'] for c in categories}
    for image in images:
        dataset, file_name = image['dataset'], image['file_name']
        meta, _ = meta_map[(dataset, file_name)]
        label = meta['result']
        if label is None:
            continue
        annotations_in_label = read_siesta_label(label, category_map, image)
        for anno in annotations_in_label:
            if anno.get('segmentation') is not None and 'counts' not in anno['segmentation']:
                anno['segmentation'] = [[
                    Decimal(x).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    for x in anno['segmentation'][0]
                ]]
            anno['bbox'] = [Decimal(x).quantize(Decimal('.01'), rounding=ROUND_DOWN) for x in anno['bbox']]
            anno['area'] = Decimal(anno['area']).quantize(Decimal('.01'), rounding=ROUND_DOWN) 

            annotations.append({
                'id': len(annotations) + 1,
                'image_id': image['id'],
                'is_crowd': 0,
                **anno
            })
    return annotations


def read_siesta_label(label, category_map, image):
    annotations = []
    for o in label['objects']:
        if o['annotation_type'] == 'box':
            c = o['annotation']['coord']
            bbox = [c['x'], c['y'], c['width'], c['height']]
            area = c['width'] * c['height']
            segmentation = None
        elif o['annotation_type'] == 'polygon':
            if o['annotation'].get('multiple', False):
                # Polygon point segmentation is not available in multipolygon
                bbox, area, _, segmentation = convert_multi_polygon_to_coco(o['annotation']['coord']['points'], image)
            else:
                bbox, area, segmentation, _ = convert_polygon_to_coco(o['annotation']['coord']['points'], image)
                # bbox, area, _, segmentation = convert_polygon_to_coco(o['annotation']['coord']['points'], image) # Use this for RLE segmentation
        else:
            continue

        annotations.append({
            'category_id': category_map[o['class_name']],
            'bbox': bbox,
            'area': area,
            'segmentation': segmentation,
        })
    return annotations


def to_coco_polygon(suite_poly):
    return [z for v in suite_poly for z in [v['x'], v['y']]]


def convert_polygon_to_coco(points, image):
    polygon = to_coco_polygon(points)
    mask_image = Image.new('L', (image['width'], image['height']), 0)
    ImageDraw.Draw(mask_image).polygon(polygon, outline=1, fill=1)
    mask = np.array(mask_image)

    from pycocotools import _mask as coco_mask
    mask = np.asfortranarray(mask.reshape(mask.shape[0], mask.shape[1], 1))
    rle = coco_mask.encode(mask)
    bbox = list(coco_mask.toBbox(rle)[0])
    area = int(coco_mask.area(rle)[0])

    return bbox, area, [polygon], rle[0]


def convert_multi_polygon_to_coco(points, image):
    """
    points is triple nested list of points consist of x and y.
    * Ref: Multipolygon in https://en.wikipedia.org/wiki/GeoJSON#Geometries
    """
    mask_image = Image.new('L', (image['width'], image['height']), 0)
    for face_polygons in points:
        ImageDraw.Draw(mask_image).polygon(to_coco_polygon(face_polygons[0]), outline=1, fill=1)
        for hole in face_polygons[1:]:
            ImageDraw.Draw(mask_image).polygon(to_coco_polygon(hole), outline=1, fill=0)
    mask = np.array(mask_image)

    from pycocotools import _mask as coco_mask
    mask = np.asfortranarray(mask.reshape(mask.shape[0], mask.shape[1], 1))
    rle = coco_mask.encode(mask)
    bbox = list(coco_mask.toBbox(rle)[0])
    area = int(coco_mask.area(rle)[0])

    return bbox, area, None, rle[0]
