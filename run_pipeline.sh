#!/bin/bash

CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# densepose and openpose
conda activate env1
python pipeline.py
conda deactivate

# cloth mask
python cloth_mask.py

# human parse
conda activate tf
cp SD-VITON/dataroot/test/image/* CIHP_PGN/datasets/images
cd CIHP_PGN
python inf_pgn.py
conda deactivate

# filling image-parse-v3
cd datasets/output/cihp_parsing_maps
mkdir vis_images
mv *vis.png vis_images
cd ../../../..
mv CIHP_PGN/datasets/output/cihp_parsing_maps/*.png SD-VITON/dataroot/test/image-parse-v3

# parse agnostic
python parse_agnostic.py

# image agnostic
python image_agnostic.py

echo 'Preprocessing complete'