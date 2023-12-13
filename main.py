#!/usr/bin/python3

import sys, os, json, time, base64, subprocess

# Index in sys.argv where the root directory is to be found
ARGV_PATH_INDEX = 1

# According to docs, block size is always 512 when using os.path
BLOCK_SIZE = 512

TEMPLATE_DIR = 'template'
HTML_FILE_NAME = 'index.html'
HTML_TEMPLATE_PATH = f'{TEMPLATE_DIR}/{HTML_FILE_NAME}'

DUMP_DIR = f'/tmp/disk-usage-pie/{time.time_ns()}'
HTML_DUMP_PATH = f'{DUMP_DIR}/{HTML_FILE_NAME}'
HTML_PLACEHOLDER_TREE = '{{TREE_JSON_BASE64}}'

def insert_into_dict(parent_dict, keys, value):
    if len(keys) == 0:
        raise Exception('No keys given!')
    elif len(keys) == 1:
        # Set value into dict at key
        parent_dict[keys[0]] = value
    else:
        # Get first key of list
        key = keys[0]
        # Remove key from rest of list
        keys = keys[1:]
        # Create child dict if it doesn't exist yet
        if key not in parent_dict:
            parent_dict[key] = {}
        # Rerun this method with child dict
        insert_into_dict(parent_dict[key], keys, value)

def get_filesystem_tree(root_path, verbose = False):
    # Run du
    if verbose: print('Running DU utility')
    du_proc = subprocess.run(['/usr/bin/du', '-a', '--block-size=1', root_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Make sure du exited without errors
    if du_proc.returncode == 0:
        tree = {}

        # Decode du output
        du_output = du_proc.stdout.decode('utf-8')
        du_lines = du_output.strip().split('\n')
        line_count = len(du_lines)

        # Iterate over du line
        for i, line in enumerate(du_lines):
            # Print progress if verbose
            if verbose:
                # Print every x percent complete
                if i % (line_count / 20) <= 1:
                    print(f'Parsing line {i + 1} / {line_count} ({int((i + 1) / line_count * 100)}%)')

            # Split DU output line
            line_parts = line.strip().split('\t')

            # Get size in bytes
            size = int(line_parts[0].strip())

            # Get the path that leads to file
            real_path = line_parts[1].strip()

            # Get the path that would be relevant for the user (relative to target)
            show_path = os.path.relpath(real_path, root_path)

            # Only handle files
            if os.path.isfile(real_path):
                # Split path into parts
                path_parts = show_path.split('/')

                # Insert file size into tree
                insert_into_dict(tree, path_parts, size)
        return tree   
    else:
        raise Exception('DU exited with non-zero return code', du_proc.stderr.decode('utf-8'))

def encode_tree(tree):
    # Convert object to JSON
    json_tree = json.dumps(tree)

    # Convert JSON string to bytes array
    bytes_tree = json_tree.encode('utf-8')

    # Encode JSON to base64
    return base64.b64encode(bytes_tree).decode('ascii')

def generate_html(tree):
    # Read template
    with open(HTML_TEMPLATE_PATH, 'r') as f:
        html = f.read().strip()

        # Replace placeholders
        html = html.replace(HTML_PLACEHOLDER_TREE, encode_tree(tree))

        return html

def generate_dump(tree):
    # Generate dirs leading to dump directory
    os.makedirs(os.path.dirname(DUMP_DIR), exist_ok=True)

    # Copy template files
    cp_proc = subprocess.run(['/usr/bin/cp', '-r', f'{TEMPLATE_DIR}', DUMP_DIR], stderr=subprocess.PIPE)
    if cp_proc.returncode != 0:
        raise Exception('CP exited with non-zero return code', cp_proc.stderr.decode('utf-8'))

    # Write HTML to dump file
    with open(HTML_DUMP_PATH, 'w') as f:
        f.write(generate_html(tree))

# Check if path was given
if len(sys.argv) >= ARGV_PATH_INDEX + 1:
    try:
        # Get usage tree of path
        root_tree = get_filesystem_tree(sys.argv[ARGV_PATH_INDEX], verbose=True)

        # Generate dump dir
        generate_dump(root_tree)

        print(HTML_DUMP_PATH)
    except Exception as e:
        e.with_traceback()
else:
    print('Usage: disk-usage-pie DIRECTORY_TO_GRAPH')