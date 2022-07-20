from pathlib import Path
import simplejson as json


def process(args):
    export_dir, output_path = args.export_dir
    meta_map = {}
    for p in Path(export_dir, 'meta').rglob('*.json'):
        with open(p, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta_map[meta['data_key']] = meta['label_path'][0]
    for data_key in meta_map:
        result = {}
        with open(Path(export_dir) / f'{meta_map[data_key]}', 'r', encoding='utf-8') as f:
            label = json.load(f)
            result['result'] = label
            with open(Path(output_path) / f'{data_key}' + '.json', 'r', encoding='utf-8') as c:
                json.dump(result, c)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--export-dir', type=str, required=True,
                        help='directory of unzipped export result')
    parser.add_argument('--output-path', type=str, default='instance.json',
                        help='output path to save converted dataset')
    args = parser.parse_args()
    process(args)
