from flask import Flask, render_template, request, flash, url_for, session, send_from_directory
from PIL import Image
import os
import subprocess
import traceback
app = Flask(__name__)

DATAROOT = "SD-VITON/dataroot/test"
CLOTHING_PATH = os.path.join(DATAROOT, "cloth")
IMG_PATH = os.path.join(DATAROOT, "image")
PAIRS_PATH = "SD-VITON/dataroot/test_pairs.txt"
OUTPUT_PATH = "SD-VITON/output/streamlit_input/test/unpaired/generator/output"

app.config['MAX_LENGTH'] = 200 * 1024 * 1024  # 200MB limit
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.secret_key = 'SD-VITON-mitcarbon-2664825'

def test_pairs(image_name, clothing):
    f = open(PAIRS_PATH, 'w')
    f.write(f'{image_name} {clothing}')
    f.close()

@app.route('/SD-VITON/dataroot/test/<path:filename>')
def get_dataroot_image(filename):
    return send_from_directory(DATAROOT, filename)

@app.route('/SD-VITON/output/streamlit_input/test/unpaired/generator/output/<path:filename>')
def get_output_image(filename):
    print(filename)
    return send_from_directory(OUTPUT_PATH, filename)

@app.route("/", methods=['GET', 'POST'])
def main():
    image_name = None
    output = None
    if 'uploaded' not in session: session['uploaded'] = False

    if request.method == 'POST':
        if 'file' in request.files:
            input_file = request.files.get('file')
            if input_file and input_file.filename != '':
                filename = input_file.filename
                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    flash('Invalid file format. Please upload JPG, PNG, or JPEG.')
                else:
                    try:
                        image = Image.open(input_file.stream)
                        image = image.resize((768, 1024))
                        print(f'Image size: {image.size}')

                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        print(image.mode)
                        image.save(os.path.join(IMG_PATH, 'input_image.jpg'))

                        session['uploaded_image'] = 'input_image.jpg'
                        image_name = 'input_image.jpg'
                        flash('Image uploaded successfully!')
                        session['uploaded'] = True

                        clothing_images = os.listdir(CLOTHING_PATH)
                        return render_template("flask_display.html", clothing_images=clothing_images, image=image_name)
                    except IOError:
                        flash('Invalid image file.')

        if 'generate' in request.form and session['uploaded']:
            try:
                image_name = session.get('uploaded_image')
                selected_cloth = request.form.get('selected_cloth')
                print("Pipeline : ", image_name, selected_cloth)
                    
                # prepare output directory
                if os.path.exists(OUTPUT_PATH):
                    for f in os.listdir(OUTPUT_PATH):
                        f_path = os.path.join(OUTPUT_PATH, f)
                        if os.path.isfile(f_path): os.remove(f_path)

                # write to test_pairs.txt: "output.jpg selection.jpg"
                test_pairs('input_image.jpg', selected_cloth)

                # run pipeline
                try:
                    subprocess.run(['./run_pipeline.sh'], shell=True, check=True, executable='/bin/bash')
                    for f in os.listdir(OUTPUT_PATH): output = f
                except subprocess.CalledProcessError as e:
                    flash(f'Error during processing: {str(e)}')
                    traceback.print_exc()
            except Exception as e:
                flash(f'An error occurred: {str(e)}')
                traceback.print_exc()
    
    clothing_images = os.listdir(CLOTHING_PATH)
    return render_template("flask_display.html", clothing_images=clothing_images, image=image_name, output=output)