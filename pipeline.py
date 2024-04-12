import json
import os
import shutil
import cv2
import mediapipe as mp
import numpy as np
from google.protobuf.json_format import MessageToDict
import time

start_time = time.time()
print('Running openpose and densepose')

# Put dataroot/test path here, the exact way it represented in SD-VITON.
DATAROOT = "SD-VITON/dataroot/test"
IMG_PATH = os.path.join(DATAROOT,"image")
APPLY_NET_PATH = "DensePose/detectron2/projects/DensePose/apply_net.py"
DENSEPOSE_CONFIG = "DensePose/detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml"
DENSEPOSE_PATH = os.path.join(DATAROOT,"image-densepose")
HUMANPARSE_PATH = "CIHP_PGN/datasets/images"

def generate_MP_JSON(image_path,test_path):

  # ---- Mediapipe config ----
  mp_drawing        = mp.solutions.drawing_utils
  mp_holistic       = mp.solutions.holistic
  mp_pose           = mp.solutions.pose
  mp_drawing_styles = mp.solutions.drawing_styles

  # Defining the default Openpose JSON structure
  # (template from openpose output)
  json_data = {
    "version": 1.3,
    "people": [
      {
        "person_id"              : [-1],
        "pose_keypoints_2d"      : [],
        "face_keypoints_2d"      : [],
        "hand_left_keypoints_2d" : [],
        "hand_right_keypoints_2d": [],
        "pose_keypoints_3d"      : [],
        "face_keypoints_3d"      : [],
        "hand_left_keypoints_3d" : [],
        "hand_right_keypoints_3d": []
      }
    ]
  }

	# Batch loading all images (path specified by the Hydra cfg file)
  img_folder = os.listdir(image_path)
  print(img_folder)
	# Loop over all the sorted  video files in the folder
  for i in range(len(img_folder)):
    img = img_folder[i]
    img_folder[i] = os.path.join(image_path,img_folder[i])

    count = 0
    with mp_pose.Pose(	min_detection_confidence	= 0.5,
            min_tracking_confidence = 0.75,
            model_complexity        = 2,
            smooth_landmarks        = True) as pose:
      print(img_folder[i])
      frame = cv2.imread(img_folder[i])
      height, width, _ = frame.shape
      count += 1
      blank = np.zeros_like(frame , dtype = np.uint8)
      # ------------- MEDIAPIPE DETECTION IN FRAME -------------
      results = pose.process(frame)

      landmarks_list = results.pose_landmarks

      if landmarks_list:  landmarks = landmarks_list.landmark
      # 3D view of landmarks
      # qq = mp_drawing.plot_landmarks( landmarks_list,  mp_pose.POSE_CONNECTIONS)

      # Plot and save the landmarks on the image
      mp_drawing.draw_landmarks(
        blank,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

      # write image to storage
      filename=img.replace(".jpg","_rendered.png")
      path_name = os.path.join(*[test_path ,  "openpose_img",filename])
      cv2.imwrite(path_name, blank)

      axes_weights=[1.0, 1.0, 0.2, 1.0]
      # scale the z dimension for all landmarks by 0.2
      temp = [landmarks[i].z * axes_weights[2] for i in range(len(landmarks))]
      # replace with the updated z value
      for i in range(len(landmarks)):
        landmarks[i].z = temp[i]

      tmp =[]
      onlyList = []
      list4json = []

      # converting the landmarks to a list
      for idx, coords in enumerate(landmarks):
        coords_dict = MessageToDict(coords)
        # print(coords_dict)
        qq = (coords_dict['x'], coords_dict['y'], coords_dict['visibility'])
        tmp.append(qq)

      #  SCALING the x and y coordinates with the resolution of the image to get px corrdinates
      for i in range(len(tmp)):
        tmp[i] = ( int(np.multiply(tmp[i][0], width)), \
              int(np.multiply(tmp[i][1], height)), \
              tmp[i][2])
      # Calculate the two additional joints for openpose and add them
      # NECK KPT
      tmp[1] = ( (tmp[11][0] - tmp[12][0]) / 2 + tmp[12][0], \
            (tmp[11][1] + tmp[12][1]) / 2 , \
            0.95 )
      # saving the hip mid point in the list for later use
      stash = tmp[8]
      # HIP_MID
      tmp.append(stash)
      tmp[8] = ( (tmp[23][0] - tmp[24][0]) / 2 + tmp[24][0], \
            (tmp[23][1] + tmp[24][1]) / 2 , \
            0.95 )

      # Reordering list to comply to openpose format
      # For the order table,refer to the Notion page
      # restoring the saved hip mid point
      mp_to_op_reorder = [0, 1, 12, 14, 16, 11, 13, 15, 8, 24, 26, 28, 23, 25, 27, 5, 2, 33, 7, 31, 31, 29, 32, 32, 30, 0, 0, 0, 0, 0, 0, 0, 0]

      onlyList = [tmp[i] for i in mp_to_op_reorder]

      # delete the last 8 elements to conform to OpenPose joint length of 25
      del onlyList[-8:]

      # OpenPose format requires only a list of all landmarkpoints. So converting to a simple list
      for nums in onlyList:
        for val in nums:
          list4json.append(val)

      # Making the JSON openpose format and adding the data
      json_data = {
        "version": 1.3,
        "people": [
          {
            "person_id"              : [-1],
            "pose_keypoints_2d"      : list4json,
            "face_keypoints_2d"      : [],
            "hand_left_keypoints_2d" : [],
            "hand_right_keypoints_2d": [],
            "pose_keypoints_3d"      : [],
            "face_keypoints_3d"      : [],
            "hand_left_keypoints_3d" : [],
            "hand_right_keypoints_3d": []
          }
        ]
      }

      json_filename = str(img) + ".json"
      json_filename = json_filename.replace(".jpg","_keypoints")
      path_name = os.path.join(*[test_path ,  "openpose_json",json_filename])
      with open(path_name, 'w') as fl:
        fl.write(json.dumps(json_data, indent=2, separators=(',', ': ')))

      # plt.close(fig)
    cv2.destroyAllWindows()

# Generate openpose_img and openpose_json
generate_MP_JSON(IMG_PATH,DATAROOT)

# Generate image-densepose
os.system(f"python {APPLY_NET_PATH} show {DENSEPOSE_CONFIG} \
https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl \
{IMG_PATH} dp_segm -v --opts MODEL.DEVICE cpu")

# Move generated images to densepose folder in dataroot
def move_files(source_folder, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    files = os.listdir(source_folder)
    for file in files:
        # if file.startswith("outputres"):
            source_file_path = os.path.join(source_folder, file)
            shutil.move(source_file_path, destination_folder)
            print(f"Moved {file} to {destination_folder}")

end_time = time.time()
execution_time = end_time - start_time
print("Done with openpose and densepose.\nExecution time: {:.4f} seconds".format(execution_time))
print('----------------------------------------------------------------------------------------')

