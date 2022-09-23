import numpy as np
import pycocotools.mask as maskUtils
from PIL import Image, ImageDraw
from pycocotools import _mask as coco_mask


def to_coco_polygon(suite_poly):
    return [z for v in suite_poly for z in [v["x"], v["y"]]]


def to_coco_multi_polygon(suite_multi_poly):
    return [z for w in suite_multi_poly for u in w for v in u for z in [v["x"], v["y"]]]


def convert_polygon_to_coco(points, image):
    polygon = to_coco_polygon(points)
    mask_image = Image.new("L", (image["width"], image["height"]), 0)
    ImageDraw.Draw(mask_image).polygon(polygon, outline=1, fill=1)
    mask = np.array(mask_image)

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
    polygon = to_coco_multi_polygon(points)
    mask_image = Image.new("L", (image["width"], image["height"]), 0)
    for face_polygons in points:
        ImageDraw.Draw(mask_image).polygon(
            to_coco_polygon(face_polygons[0]), outline=1, fill=1
        )
        for hole in face_polygons[1:]:
            ImageDraw.Draw(mask_image).polygon(to_coco_polygon(hole), outline=1, fill=0)
    mask = np.array(mask_image)

    mask = np.asfortranarray(mask.reshape(mask.shape[0], mask.shape[1], 1))
    rle = coco_mask.encode(mask)
    bbox = list(coco_mask.toBbox(rle)[0])
    area = int(coco_mask.area(rle)[0])

    return bbox, area, None, rle[0]


def convert_keypoint_to_coco(points, image):
    keypoints = []
    x, y, x_max, y_max = float("inf"), float("inf"), 0, 0
    num_keypoints = 0
    for point in points:
        if point["x"] or point["y"]:
            if x > point["x"]:
                x = point["x"]
            if x_max < point["x"]:
                x_max = point["x"]
            if y > point["y"]:
                y = point["y"]
            if y_max < point["y"]:
                y_max = point["y"]
        if point["state"]["visible"]:
            keypoints.append(point["x"])
            keypoints.append(point["y"])
            keypoints.append(2)
            num_keypoints += 1
        # TODO: state discrimination (three state)
        else:
            keypoints.append(0)
            keypoints.append(0)
            keypoints.append(1)
    width, height = x_max - x, y_max - y
    bbox = [x, y, width, height]
    area = width * height
    polygon = [[]]

    return bbox, area, polygon, keypoints, num_keypoints


def polygons_to_rle(polygons, img_height, img_width):
    rles_all = []
    for p in polygons:
        # polygon: [[x1, y1], [x2, y2], [x3, y3], ...]
        # flatten: [x1, y1, x2, y2, x3, y3, ...]
        flatten = [v for xy in p for v in xy]

        rles = maskUtils.frPyObjects([flatten], img_height, img_width)
        rles_all.extend(rles)

    rle = maskUtils.merge(rles_all)
    rle["counts"] = rle["counts"].decode("utf-8")
    if len(rles_all) == 0:
        rle["size"] = [img_height, img_width]
    return rle


def rle_to_mask(rle):
    return np.ascontiguousarray(maskUtils.decode(rle))


def bbox_to_yolo_bbox(bbox):
    x = bbox["x"]
    y = bbox["y"]
    width = bbox["width"]
    height = bbox["height"]

    x_center = x + width / 2
    y_center = y + height / 2

    return [x_center, y_center, width, height]


def polygon_to_yolo_bbox(points):
    polygon = to_coco_polygon(points)
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = 0, 0
    for idx, p in enumerate(polygon):
        if idx % 2:
            # x
            if p > max_x:
                max_x = p
            elif p < min_x:
                min_x = p
        else:
            # y
            if p > max_y:
                max_y = p
            elif p < min_y:
                min_y = p

    width = max_x - min_x
    height = max_y - min_y
    x_center = min_x + width / 2
    y_center = min_y + height / 2

    return [x_center, y_center, width, height]


def multi_polygon_to_yolo_bbox(points):
    polygon = to_coco_multi_polygon(points)
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = 0, 0
    for idx, p in enumerate(polygon):
        if idx % 2:
            # x
            if p > max_x:
                max_x = p
            elif p < min_x:
                min_x = p
        else:
            # y
            if p > max_y:
                max_y = p
            elif p < min_y:
                min_y = p

    width = max_x - min_x
    height = max_y - min_y
    x_center = min_x + width / 2
    y_center = min_y + height / 2

    return [x_center, y_center, width, height]
