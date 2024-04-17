import streamlit as st
from PIL import Image
import numpy as np
import subprocess
import os
import shutil
import requests

DATAROOT = "SD-VITON/dataroot/test"
CLOTHING_PATH = os.path.join(DATAROOT, "cloth")
IMG_PATH = os.path.join(DATAROOT, "image")
PAIRS_PATH = "SD-VITON/dataroot/test_pairs.txt"
OUTPUT_PATH = "SD-VITON/output/streamlit_input/test/unpaired/generator/output"


def test_pairs(image_name, clothing):
    f = open(PAIRS_PATH, 'w')
    f.write(f'{image_name} {clothing}')
    f.close()

def save_response_content(response, destination):
    print(destination)
    CHUNK_SIZE = 42000

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def download(id, dir, file):
    if os.path.exists("CIHP_PGN/checkpoint/CIHP_pgn") and os.path.exists("SD-VITON/tocg.pth") and os.path.exists("SD-VITON/toig.pth"):
        print(f"{file} file already exists")
    else:
        URL = "https://docs.google.com/uc?export=download"
    
        session = requests.Session()
    
        response = session.get(URL, params = { 'id' : id }, stream = True)
        token = get_confirm_token(response)
    
        if token:
            params = { 'id' : id, 'confirm' : token }
            response = session.get(URL, params = params, stream = True)

        os.makedirs(dir, exist_ok=True)
        destination = os.path.join(dir, file)
        save_response_content(response, destination)  

def download_chkpts():
    # https://drive.google.com/file/d/1eYFX7r-1K9VW81O570_W5y4p5fwpeI4H/view?usp=drive_link
    download('1eYFX7r-1K9VW81O570_W5y4p5fwpeI4H', 'CIHP_PGN/checkpoint/CIHP_pgn', 'checkpoint.txt')

    # https://drive.google.com/file/d/1o3FMhezRXcp6LXE92UYtNud0ixKFiao7/view?usp=drive_link
    download('1o3FMhezRXcp6LXE92UYtNud0ixKFiao7','CIHP_PGN/checkpoint/CIHP_pgn', 'model.ckpt-593292.data-00000-of-00001')

    # https://drive.google.com/file/d/16ihgWIxgeY8tKtd-Qn7d_P60hnWneJgu/view?usp=drive_link
    download('16ihgWIxgeY8tKtd-Qn7d_P60hnWneJgu','CIHP_PGN/checkpoint/CIHP_pgn', 'model.ckpt-593292.index')

    # https://drive.google.com/file/d/1MmpRrK8oiw27tEwn8eLG0ThHbz7MiLhs/view?usp=drive_link
    download('1MmpRrK8oiw27tEwn8eLG0ThHbz7MiLhs','CIHP_PGN/checkpoint/CIHP_pgn', 'model.ckpt-593292.meta')

    # https://drive.google.com/file/d/1D75ZQ3xnAIsKBf3eOJQF6dbyQpEUr2sO/view?usp=drive_link
    download('1D75ZQ3xnAIsKBf3eOJQF6dbyQpEUr2sO','SD-VITON', 'tocg.pth')

    # https://drive.google.com/file/d/1BsOMU2JeOCnCZDl8XrGzoFcOccpHCctT/view?usp=drive_link
    download('1BsOMU2JeOCnCZDl8XrGzoFcOccpHCctT','SD-VITON', 'toig.pth')

# Function to overlay the selected clothing on the uploaded image
def overlay_clothing(image, clothing):
    print("Pipeline : ", image, clothing)

    # prepare image directory
    if not os.path.exists(IMG_PATH): os.makedirs(IMG_PATH)
    else:
        for f in os.listdir(IMG_PATH):
            f_path = os.path.join(IMG_PATH, f)
            if os.path.isfile(f_path): os.remove(f_path)
    
    # prepare output directory
    st.text(OUTPUT_PATH)
    if os.path.exists(OUTPUT_PATH):
        for f in os.listdir(OUTPUT_PATH):
            f_path = os.path.join(OUTPUT_PATH, f)
            if os.path.isfile(f_path): os.remove(f_path)

    # resize image
    image = image.resize((768, 1024))
    print(f'Image size: {image.size}')

    # add new image
    if image.mode != 'RGB': image = image.convert('RGB')
    print(image.mode)
    image.save(os.path.join(IMG_PATH, 'input_image.jpg'))

    # write to test_pairs.txt: "output.jpg selection.jpg"
    test_pairs('input_image.jpg', clothing)

    # run pipeline
    subprocess.run(['./run_pipeline.sh'], shell=True, check=True, executable='/bin/bash')

    # display generated image
    for f in os.listdir(OUTPUT_PATH):
        f_path = os.path.join(OUTPUT_PATH, f)
        output = Image.open(f_path)
        st.image(output, caption='Generated Image', use_column_width=True)

# Main function to run the Streamlit app
def main():
    st.title("Virtual Dressing Room")
    st.write("Upload your picture:")
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        # Display the uploaded image
        image = Image.open(uploaded_image)
    
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Get list of clothing images from cloth directory
        clothing_images = os.listdir(f'{CLOTHING_PATH}')

        # Display images of clothes side by side for selection
        cols = st.columns(len(clothing_images))
        
        for i, col in enumerate(cols):
            clothing_image = Image.open(f"{CLOTHING_PATH}/{clothing_images[i]}")
            col.image(clothing_image, use_column_width=True, caption=clothing_images[i])

            # Allow user to click on the image to select it
            if col.button("Select", key=i):
                if 'clothing_selections' not in st.session_state:
                    st.session_state.clothing_selections = clothing_images[i]
                elif 'clothing_selections' in st.session_state:
                    st.session_state.clothing_selections = clothing_images[i]

        # Generate button to overlay the selected clothing on the uploaded image
        if st.button("Generate"):
            download_chkpts()
            
            if 'clothing_selections' in st.session_state:
                overlay_clothing(image, st.session_state.clothing_selections)
                # st.text('WORKS')
           
            

if __name__ == "__main__":
    main()
