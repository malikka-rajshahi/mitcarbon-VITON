import streamlit as st
from PIL import Image
import os
import numpy as np
import subprocess

DATAROOT = "SD-VITON/dataroot/test"
CLOTHING_PATH = os.path.join(DATAROOT, "cloth")
IMG_PATH = os.path.join(DATAROOT, "image")

# Function to overlay the selected clothing on the uploaded image
def overlay_clothing(image, image_name, clothing):
    print("Pipeline : ", image,clothing)

    # prepare image directory
    if not os.path.exists(IMG_PATH): os.makedirs(IMG_PATH)
    else:
        for f in os.listdir(IMG_PATH):
            f_path = os.path.join(IMG_PATH, f)
            if os.path.isfile(f_path): os.remove(f_path)

    # add image to image directory
    image.save(os.path.join(IMG_PATH, f'{image_name}'))

    # run pipeline
    subprocess.run(['./run_pipeline.sh'], shell=True, check=True, executable='/bin/bash')

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
                overlay_clothing(image, uploaded_image.name, st.session_state.clothing_selections)
           
            

if __name__ == "__main__":
    main()
