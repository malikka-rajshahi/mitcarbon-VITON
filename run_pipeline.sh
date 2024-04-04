conda activate env1
python pipeline.py
conda deactivate

conda activate tf
cd CIHP_PGN
python inf_pgn.py
conda deactivate

cd ..