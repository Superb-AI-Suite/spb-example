from collections import defaultdict
import os
from PIL import Image, ImageDraw
import numpy as np


def create_mask(data_type, project_info, image_info, label_id, label, mask_dir):
    # project settings
    if data_type == 'image':
        class_settings = project_info['object_detection']
    else:
        class_settings = project_info['object_tracking']
    class_to_group_map = {}
    for obj_group in class_settings['object_groups']:
        for obj_class_id in obj_group['object_class_ids']:
            class_to_group_map[obj_class_id] = obj_group
    class_infos = {
        obj_class['id']: {
            'idx': idx,
            'group': class_to_group_map.get(obj_class['id'])
        }
        for idx, obj_class in enumerate(class_settings['object_classes'], 1)
    }

    # create polygons per group
    def anno_to_polygons(idx, anno):
        if len(anno['coord']['points']) < 3:
            return None, None
        points = [(point['x'], point['y']) for point in anno['coord']['points']]
        z_index = anno['meta']['zIndex'] if 'meta' in anno and 'zIndex' in anno['meta'] else 1
        group = class_infos[obj['classId']]['group']
        group_name = group['name'] if group is not None else None
        return group_name, {
                'instanceId': idx,
                'classId': class_infos[obj['classId']]['idx'],
                'points': points,
                'zIndex': z_index
            }

    group_polygons = defaultdict(list)
    for idx, obj in enumerate(label['objects'], 1):
        if obj['annotationType'] not in ['polygon']:
            continue
        if data_type == 'image':
            group_name, polygons = anno_to_polygons(idx, obj['annotation'])
            if polygons is not None:
                group_polygons[group_name].append(polygons)
        else:
            for frame_idx, frame in enumerate(obj['frames']):
                group_name, polygons = anno_to_polygons(idx, frame['annotation'])
                group_polygons[(group_name, frame_idx)].append(polygons)

    # render polygons
    for key, polygons in group_polygons.items():
        if data_type == 'image':
            group_name, frame_idx = key, None
        else:
            group_name, frame_idx = key

        for key in ['classId', 'instanceId']:
            mask_path_prefix = os.path.join(mask_dir, key)
            if group_name is not None:
                mask_path_prefix = os.path.join(mask_path_prefix, group_name)
            if frame_idx is None:
                mask_path = os.path.join(mask_path_prefix, f'{label_id}.png')
            else:
                mask_path = os.path.join(mask_path_prefix, f'{label_id}', f'{frame_idx:08d}.png')
            if not os.path.exists(os.path.dirname(mask_path)):
                os.makedirs(os.path.dirname(mask_path))
            
            mask_image = Image.new('P', (image_info['width'], image_info['height']), 0)
            mask_image.putpalette(color_map())
            mask_draw = ImageDraw.Draw(mask_image)

            for polygon in sorted(polygons, key=lambda p: p['zIndex']):
                mask_draw.polygon(polygon['points'], fill=polygon[key])

            mask_image.save(mask_path, format='PNG')


def color_map(N=256, normalized=False):
    def bitget(byteval, idx):
        return ((byteval & (1 << idx)) != 0)

    dtype = 'float32' if normalized else 'uint8'
    cmap = np.zeros((N, 3), dtype=dtype)
    for i in range(N):
        r = g = b = 0
        c = i
        for j in range(8):
            r = r | (bitget(c, 0) << 7-j)
            g = g | (bitget(c, 1) << 7-j)
            b = b | (bitget(c, 2) << 7-j)
            c = c >> 3

        cmap[i] = np.array([r, g, b])

    cmap = cmap/255 if normalized else cmap
    return cmap
