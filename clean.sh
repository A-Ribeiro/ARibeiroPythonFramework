#!/bin/sh
find . -type d -name '__pycache__' -exec rm -rf {} \;
rm output.jpg
rm output_map.png