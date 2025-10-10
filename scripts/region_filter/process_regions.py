import yaml
import argparse
import sys
import os

def filter_regions_by_short_name(data, short_names_to_keep):
    """
    Filters the regions in the data, keeping only the ones where a cluster name
    contains one of the specified short names.
    """
    filtered_data = []
    for stage in data:
        if 'regions' in stage and isinstance(stage['regions'], list):
            filtered_regions = []
            for region in stage['regions']:
                if 'clusters' in region and isinstance(region['clusters'], list):
                    # Check if the last part of the cluster name exactly matches one of the short names
                    if any(
                        any(cluster.get('name', '').split('-')[-1] == s for s in short_names_to_keep)
                        for cluster in region['clusters']
                    ):
                        filtered_regions.append(region)

            if filtered_regions:
                new_stage = stage.copy()
                new_stage['regions'] = filtered_regions
                filtered_data.append(new_stage)
    return filtered_data

def main():
    """
    Main function to process the YAML file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input_file = os.path.join(script_dir, 'release_regions.yaml')

    parser = argparse.ArgumentParser(
        description='Filter regions in a YAML file by short name and print to stdout.'
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        default=default_input_file,
        help=f'The path to the input YAML file (default: {default_input_file}).'
    )
    parser.add_argument(
        '-r', '--regions',
        required=True,
        help='A comma-separated list of region short names to keep (e.g., use,usw2).'
    )

    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}", file=sys.stderr)
        sys.exit(1)

    regions_to_keep = [region.strip() for region in args.regions.split(',')]

    filtered_data = filter_regions_by_short_name(data, regions_to_keep)

    if filtered_data:
        output_str = yaml.dump(filtered_data, sort_keys=False, indent=2)
        sys.stdout.write(output_str.rstrip() + '\n')

if __name__ == '__main__':
    main()
