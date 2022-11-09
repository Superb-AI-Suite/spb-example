from collections import defaultdict
import os
from PIL import Image, ImageDraw
import numpy as np


def create_mask(data_type, project_info, image_info, label_id, label, mask_dir):
    # project settings
    if data_type == "image-default" or data_type == "image-siesta":
        class_settings = project_info["object_detection"]
    else:
        class_settings = project_info["object_tracking"]
    class_to_group_map = {}
    for obj_group in class_settings["object_groups"]:
        for obj_class_id in obj_group["object_class_ids"]:
            class_to_group_map[obj_class_id] = obj_group
    class_infos = {
        obj_class["id"]: {"idx": idx, "group": class_to_group_map.get(obj_class["id"])}
        for idx, obj_class in enumerate(class_settings["object_classes"], 1)
    }
    # create polygons per group
    def anno_to_polygons(idx, anno, data_type):
        if data_type == "image-default":
            z_index_name = "zIndex"
            class_id = "classId"
            if len(anno["coord"]["points"]) < 3:
                return None, None
            else:
                final_pts = [(point["x"], point["y"]) for point in anno["coord"]["points"]]
        else:
            z_index_name = "z_index"
            class_id = "class_id"
            final_pts = []

            for ls in anno["coord"]["points"]:
                for i, inner_ls in enumerate(ls):
                    points = []
                    if i == 0:
                        points.append(
                            [(points["x"], points["y"]) for points in inner_ls]
                        )
                    else:
                        inner_pts = []
                        inner_pts.append(
                            [(points["x"], points["y"]) for points in inner_ls]
                        )
                        points.append(inner_pts)
                if len(points) == 1:
                    final_pts.append(points[0])
                else:
                    final_pts.append(points)

        z_index = (
            anno["meta"][z_index_name]
            if "meta" in anno and z_index_name in anno["meta"]
            else 1
        )
        group = class_infos[obj[class_id]]["group"]
        group_name = group["name"] if group is not None else None
        return group_name, {
            "instanceId": idx,
            "classId": class_infos[obj[class_id]]["idx"],
            "points": final_pts,
            "zIndex": z_index,
        }

    group_polygons = defaultdict(list)
    for idx, obj in enumerate(label["objects"], 1):
        if "siesta" in data_type:
            annotation_type = "annotation_type"
        else:
            annotation_type = "annotationType"
        if obj[annotation_type] not in ["polygon"]:
            continue
        if "image" in data_type:
            group_name, polygons = anno_to_polygons(idx, obj["annotation"], data_type)
            if polygons is not None:
                group_polygons[group_name].append(polygons)
        else:
            for frame_idx, frame in enumerate(obj["frames"]):
                group_name, polygons = anno_to_polygons(
                    idx, frame["annotation"], data_type
                )
                group_polygons[(group_name, frame_idx)].append(polygons)

    # render polygons
    for key, polygons in group_polygons.items():
        if data_type == "image-default" or data_type == "image-siesta":
            group_name, frame_idx = key, None
        else:
            group_name, frame_idx = key
        for key in ["classId", "instanceId"]:
            mask_path_prefix = os.path.join(mask_dir, key)
            if group_name is not None:
                mask_path_prefix = os.path.join(mask_path_prefix, group_name)
            if frame_idx is None:
                mask_path = os.path.join(mask_path_prefix, f"{label_id}.png")
            else:
                mask_path = os.path.join(
                    mask_path_prefix, f"{label_id}", f"{frame_idx:08d}.png"
                )
            if not os.path.exists(os.path.dirname(mask_path)):
                os.makedirs(os.path.dirname(mask_path))

            mask_image = Image.new("P", (image_info["width"], image_info["height"]), 0)
            mask_image.putpalette(color_map())
            mask_draw = ImageDraw.Draw(mask_image)

            for polygon in sorted(polygons, key=lambda p: p["zIndex"]):
                # for pts in polygon["points"]:
                mask_draw.polygon(polygon["points"], fill=polygon[key])

            mask_image.save(mask_path, format="PNG")


def color_map(N=256, normalized=False):
    def bitget(byteval, idx):
        return (byteval & (1 << idx)) != 0

    dtype = "float32" if normalized else "uint8"
    cmap = np.zeros((N, 3), dtype=dtype)
    for i in range(N):
        r = g = b = 0
        c = i
        for j in range(8):
            r = r | (bitget(c, 0) << 7 - j)
            g = g | (bitget(c, 1) << 7 - j)
            b = b | (bitget(c, 2) << 7 - j)
            c = c >> 3

        cmap[i] = np.array([r, g, b])

    cmap = cmap / 255 if normalized else cmap
    return cmap
