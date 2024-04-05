# running densepose and openpose
conda activate env1
python pipeline.py
conda deactivate

# running human parse
conda activate tf
cp SD-VITON/dataroot/test/image/* CIHP_PGN/datasets/images
cd CIHP_PGN
python inf_pgn.py
conda deactivate

# running parse agnostic
cd ..
python parse_agnostic.py

# running image agnostic
python image_agnostic.py
