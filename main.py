#!/usr/bin/python3

from os import listdir, stat
from os.path import join, isdir

from sys import argv

import json

# Index in sys.argv where the root directory is to be found
ARGV_PATH_INDEX = 1

# According to docs, block size is always 512 when using os.path
BLOCK_SIZE = 512

def get_size_on_disk(path):
    # Calculate size of used blocks
    return stat(path).st_blocks * BLOCK_SIZE

def get_filesystem_tree(root_path):
    # Start root node of tree
    tree = {}

    # Navigate over every child
    for child in listdir(root_path):
        # Get full path of child
        child_path = join(root_path, child)

        # If child is a directory
        if isdir(child_path):
            # Make a branch with child tree
            tree[child] = get_filesystem_tree(child_path)
        else:
            # Make a leaf with child size
            tree[child] = get_size_on_disk(child_path)

    # Return tree
    return tree

if len(argv) >= ARGV_PATH_INDEX + 1:

    try:
        root_tree = get_filesystem_tree(argv[ARGV_PATH_INDEX])
        print(json.dumps(root_tree))
    except Exception as e:
        print('Error:', e)
else:
    print('Usage: disk-usage-pie DIRECTORY_TO_GRAPH')