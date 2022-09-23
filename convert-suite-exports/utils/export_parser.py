from zipfile import ZipFile

import simplejson as json


def parse_export_zip_file(path):
    with ZipFile(path) as zip_file:
        meta_json_list = []
        label_json = {}
        file_list = zip_file.namelist()
        metas = [f for f in file_list if f.startswith("meta/") and f.endswith(".json")]
        project_json = json.loads(zip_file.open("project.json", "r").read())
        for meta in metas:
            meta_info = json.loads(zip_file.open(meta).read())
            label_path = meta_info["label_path"][0]
            label_json[label_path] = json.loads(zip_file.open(label_path).read())
            meta_json_list.append(meta_info)
        return meta_json_list, label_json, project_json
