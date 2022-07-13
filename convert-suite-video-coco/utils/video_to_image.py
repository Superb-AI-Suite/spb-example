#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import os
from copy import deepcopy as copy
from uuid import uuid4


def convert_label_interface(project_json):
    new_project_json = {}
    new_project_json["type"] = "image-siesta"
    new_project_json["version"] = project_json["version"]
    new_project_json["data_type"] = "image"
    new_project_json["categorization"] = {
        "properties": project_json["categorization"]["properties"]
    }
    object_tracking = project_json["object_tracking"]
    object_detection = {}
    object_detection["keypoints"] = object_tracking["keypoints"]
    object_groups = copy(object_tracking["object_groups"])
    object_detection["object_groups"] = object_groups
    object_classes = copy(object_tracking["object_classes"])
    new_object_classes = []
    for object_class in object_classes:
        new_object_class = copy(object_class)
        new_object_classes.append(new_object_class)
    object_detection["object_classes"] = new_object_classes
    annotation_types = copy(object_tracking["annotation_types"])
    object_detection["annotation_types"] = annotation_types
    new_project_json["object_detection"] = object_detection

    return new_project_json


def parse_label(label):
    num2obj_mapping = {}
    if label:
        objects = label['objects']
        for obj in objects:
            frames = obj['frames']
            obj_prop = obj['properties']
            for frame in frames:
                num = frame['num']
                new_obj = {
                    'id': obj['id'],
                    'class_id': obj['class_id'],
                    'class_name': obj['class_name'],
                    'annotation_type': obj['annotation_type'],
                    'annotation': frame['annotation'],
                    'properties': frame['properties'] + obj_prop
                }
                if num in num2obj_mapping:
                    num2obj_mapping[num].append(new_obj)
                    # count += 1
                else:
                    num2obj_mapping[num] = [new_obj]
                    # count += 1

    return num2obj_mapping


def read_vti(meta_map, project_json, label_dict):
    new_meta_dict = {}
    new_label_dict = {}
    new_project_path = 'project.json'
    # TODO: keypoint, categorization
    new_project_json = convert_label_interface(project_json)
    print("reading (video to image)")
    total_num = len(meta_map)
    for i, (dataset, data_key) in enumerate(meta_map.keys()):
        meta = meta_map[(dataset, data_key)]
        write_dir = str(Path(dataset)/data_key)
        #  write_dir = str(Path(dataset.replace(' ', '_'))/data_key)
        label_path = meta['label_path'][0]
        label = label_dict[label_path]
        num2obj_mapping = parse_label(label)
        for num, frame in enumerate(meta['frames']):
            if label:
                current_categories = {
                    'properties': label['categories']['properties']
                }
            else:
                current_categories = {'properties': []}
            if num in num2obj_mapping:
                current_objs = num2obj_mapping[num]
            else:
                current_objs = []
            new_label = {
                'objects': current_objs,
                'categories': current_categories
            }
            new_label_id = str(uuid4())
            new_label_path = os.path.join('labels', new_label_id) + '.json'
            new_label_dict[new_label_path] = new_label
            new_meta = {
                'data_key': str(Path(data_key)/frame),
                'dataset': dataset,
                #  'dataset': dataset.replace(' ', '_'),
                'image_info': meta['image_info'],
                'label_id': new_label_id,
                'label_path': new_label_path,
                'last_updated_date': meta['last_updated_date'],
                'tags': meta['tags'],
                'work_assignee': meta['work_assignee'],
                'status': meta['status'],
                'height': meta['image_info']['height'],
                'width': meta['image_info']['width']
            }
            meta_output_path = os.path.join(
                *['meta', write_dir, frame]) + '.json'
            new_meta_dict[(write_dir, frame)] = new_meta

    return new_project_path, new_project_json, new_meta_dict, new_label_dict


def convert_vti(meta_dict_list, label_dict, project_dict):
    meta_map = {}
    for i, meta in enumerate(meta_dict_list):
        meta_map[(meta['dataset'], meta['data_key'])] = meta
    return read_vti(meta_map, project_dict, label_dict)
