#!/bin/bash

set -e

if [ -z "$2" ]; then
    echo "Usage: $(basename $0) filename new_dir" >&2
    echo "filename will be placed in new_dir and renamed to ensure uniqueness"
    exit 1
fi

filename=$1
new_dir=$PWD/$2

if [ ! -e $new_dir ]; then
    mkdir $new_dir
fi

cd ..
for project in *; do
    if [ ! -d "$project" ]; then continue; fi
    if [ ! -d "$project/analysis" ]; then continue; fi
    cd "$project/analysis"

    if [ -e "$filename" ]; then
        ln -v "$filename" "$new_dir/${project}_$filename"
    else
        echo "skipping nonexistent $project/analysis/$filename"
    fi

    cd ../..
done
