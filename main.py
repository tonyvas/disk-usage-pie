#!/usr/bin/python3

import sys, os, json, time, base64

# Index in sys.argv where the root directory is to be found
ARGV_PATH_INDEX = 1

# According to docs, block size is always 512 when using os.path
BLOCK_SIZE = 512

HTML_TEMPLATE_PATH = 'template.html'

DUMP_PATH = f'/tmp/disk-usage-pie/{time.time_ns()}'
HTML_DUMP_PATH = f'{DUMP_PATH}/pie.html'
HTML_PLACEHOLDER_TREE = '{{TREE_JSON_BASE64}}'

def get_size_on_disk(path):
    # Calculate size of used blocks
    return os.stat(path).st_blocks * BLOCK_SIZE

def get_filesystem_tree(root_path):
    # Start root node of tree
    tree = {}

    try:
        # Navigate over every child
        for child in os.listdir(root_path):
            # Get full path of child
            child_path = os.path.join(root_path, child)

            # If child is a directory
            if os.path.isdir(child_path):
                # Make a branch with child tree
                tree[child] = get_filesystem_tree(child_path)
            elif os.path.isfile(child_path):
                # Make a leaf with child size
                tree[child] = get_size_on_disk(child_path)
    except PermissionError as e:
        # Assume directory is empty if we do not have permission to navigate dir
        pass

    # Return tree
    return tree

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
    # Generate dump directory
    os.makedirs(DUMP_PATH, exist_ok=True)

    # Write HTML to dump file
    with open(HTML_DUMP_PATH, 'w') as f:
        f.write(generate_html(tree))

# Check if path was given
if len(sys.argv) >= ARGV_PATH_INDEX + 1:
    try:
        # Get usage tree of path
        root_tree = get_filesystem_tree(sys.argv[ARGV_PATH_INDEX])

        # Generate dump dir
        generate_dump(root_tree)

        print(HTML_DUMP_PATH)
    except Exception as e:
        print('Error:', e)
else:
    print('Usage: disk-usage-pie DIRECTORY_TO_GRAPH')