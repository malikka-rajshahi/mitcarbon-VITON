import gdown

url = 'https://drive.google.com/uc?id=1ruJg4lqR_jgQPj-9K0PP-L2vJERYOxLP' # ATR
output = 'checkpoints/final.pth'
gdown.download(url, output, quiet=False)