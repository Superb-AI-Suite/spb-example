import tqdm
import os
import json
from pathlib import Path

import spb.sdk


def process(args):
    project_name, dataset_name = args.project, args.dataset
    # This will cause error if project name is invalid
    spb_client = spb.sdk.Client(project_name=project_name)

    # Print project information
    print('Project Name: {}'.format(spb_client.get_project_name()))
    print('Total number of data: {}'.format(spb_client.get_num_data()))

    # Load upload information
    with open(args.upload_info, 'r') as f:
        upload_info = json.load(f)

    # Uploading Images
    for image_info in tqdm.tqdm(upload_info['images']):
        image_path = os.path.join(upload_info['image_file_dir'], image_info['image_name'])
        data_handler = spb_client.upload_image(image_path, dataset_name)

    # Adding Objects
    def get_spb_data(spb_client, page_size=10):
        num_data = spb_client.get_num_data()
        num_page = (num_data + page_size - 1) // page_size
        def generator():
            for page_idx in range(num_page):
                for data_handler in spb_client.get_data_page(page_idx=page_idx, page_size=page_size):
                    yield data_handler
        return {'iterable': generator(), 'total': num_data}

    image_to_anno = {
        image_info['image_name']: image_info['annotations']
        for image_info in upload_info['images']
    }
    for data_handler in tqdm.tqdm(**get_spb_data(spb_client)):
        data_key = data_handler.get_key()
        for anno in image_to_anno[data_key]:
            annotation = anno['annotation']
            class_name = anno['class_name']
            data_handler.add_object_label(class_name, annotation)
        data_handler.update_data()


if __name__ == '__main__':
    print(f'This guide was made with this version: v{spb.sdk.__version__}')

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=str)
    parser.add_argument('--dataset', type=str)
    parser.add_argument('--upload-info', type=Path, default='upload-info.json')
    args = parser.parse_args()
    process(args)
