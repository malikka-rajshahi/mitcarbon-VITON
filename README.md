CIHP_PGN, SD-VITON checkpoints: https://drive.google.com/drive/folders/1nJnIWXI6qpEiIVobPP_eMldwfJNDrBdd?usp=sharing

## Checkpoint Hierarchy
### In CIHP_PGN: 
./checkpoint/CIHP_pgn/checkpoint
  
./checkpoint/CIHP_pgn/model.ckpt-593292.data-00000-of-00001
  
./checkpoint/CIHP_pgn/model.ckpt-593292.index
  
./checkpoint/CIHP_pgn/model.ckpt-593292.meta

### In SD-VITON:

./tocg.pth
  
 ./toig.pth

## Conda Environments:
### env1:
conda create -n env1 python=3.8

conda activate env1

conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch-lts -c nvidia

pip install opencv-python torchgeometry Pillow tqdm tensorboardX scikit-image scipy timm==0.4.12

conda deactivate

### tf:
conda create -n tf python-3.7

conda activate tf

conda install -c conda-forge cudatoolkit=10.0 cudnn=7.6.5

conda deactivate
pip install tensorflow==1.15

pip install scipy==1.7.3 opencv-python==4.5.5.62 protobuf==3.19.1 Pillow==9.0.1 matplotlib==3.5.1

conda deactivate
