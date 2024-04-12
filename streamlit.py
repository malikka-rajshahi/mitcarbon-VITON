import streamlit as st
from PIL import Image
import os
import numpy as np
import subprocess

DATAROOT = "SD-VITON/dataroot/test"
CLOTHING_PATH = os.path.join(DATAROOT, "cloth")
IMG_PATH = os.path.join(DATAROOT, "image")
PAIRS_PATH = "SD-VITON/dataroot/test_pairs.txt"
OUTPUT_PATH = "SD-VITON/output/streamlit_input/test/unpaired/generator/output"

def test_pairs(image_name, clothing):
    f = open(PAIRS_PATH, 'w')
    f.write(f'{image_name} {clothing}')
    f.close()

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
            if 'clothing_selections' in st.session_state:
                overlay_clothing(image, st.session_state.clothing_selections)
           
            

if __name__ == "__main__":
    main()
