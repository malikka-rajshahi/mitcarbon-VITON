#!/bin/bash

# running streamlit:
pipenv shell
source ~/.bash_profile
# streamlit run streamlit.py

CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# reset directories
find . -name '.DS_Store' -type f -delete
rm -rf SD-VITON/dataroot/output/streamlit_input/*
rm -rf SD-VITON/dataroot/test/agnostic-v3.2/*
rm -rf SD-VITON/dataroot/test/cloth/input_image.jpg
rm -rf SD-VITON/dataroot/test/cloth-mask/*
rm -rf SD-VITON/dataroot/test/image-densepose/*
rm -rf SD-VITON/dataroot/test/image-parse-agnostic-v3.2/*
rm -rf SD-VITON/dataroot/test/image-parse-v3/*
rm -rf SD-VITON/dataroot/test/openpose_img/*
rm -rf SD-VITON/dataroot/test/openpose_json/*

echo 'Preprocessing...'

# input and cloth image have to go through cloth mask
cp SD-VITON/dataroot/test/image/* SD-VITON/dataroot/test/cloth
conda activate env1
python cloth_mask.py

# densepose/openpose
python pipeline.py
conda deactivate

# human parse
conda activate tf
rm -rf CIHP_PGN/datasets/images/*
cp SD-VITON/dataroot/test/image/* CIHP_PGN/datasets/images
cd CIHP_PGN
python inf_pgn.py
conda deactivate

source "$CONDA_BASE/etc/profile.d/conda.sh"

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

echo 'Preprocessing complete!'

# run model
echo 'Running model...'
conda activate env1
cd SD-VITON
python ./test_generator.py --occlusion --test_name streamlit_input --tocg_checkpoint ./tocg.pth \
--gen_checkpoint ./toig.pth --datasetting unpaired --dataroot ./dataroot --data_list test_pairs.txt --composition_mask
echo 'Model ran!'
cd ..
rm -rf SD-VITON/dataroot/test/cloth/input_image.jpg
