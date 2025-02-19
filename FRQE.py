import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import cv2
import os.path
import subprocess

from RegionRemoval.black_out_sub_regions import create_blackout_images
from RegionRemoval.compute_averages_of_blackout_regions_UQS import compute_blackout_regions_difference_per_pixel


def compute_Face_Region_Quality_Estimation_heatmap(image_file):

    image_name_base, ext = os.path.splitext(image_file)


    # NOTE: change to your local path to FGFP masks in OFIQ-FGFP
    face_parsing_mask_path = f"C:\\Users\\admin\\source\\repos\\OFIQ-Project-FGFP\\install_x86_64\\Release\\bin\\FGFP_images\\FGFP_{image_name_base}.png"

    face_parsing_mask_gray = cv2.imread(face_parsing_mask_path, cv2.IMREAD_GRAYSCALE) # Assumed to have size 200x200
    # aligned image is cropped before being input to Fine-Grained Face Parsing algorithm. To adjust for this, 22 pixels must be added in each direction in the places specified (when face parsing size is 200x200)
    face_parsing_mask_padding = cv2.copyMakeBorder(face_parsing_mask_gray, 0, 22, 11, 11, cv2.BORDER_CONSTANT, (0))

    region_class_dictionary = {
        "LeftEyeBrow" : 2,
        "RightyeBrow" : 3,
        "LeftEye" : 4,
        "RightEye" : 5,
        "Nose" : 10,
        "Mouth" : 11,
        "UpperLip" : 12,
        "LowerLip" : 13,
        "Nasal" : 20,
        "RightOrbital" : 21,
        "LeftOrbital" : 22,
        "Mental" : 23,
        "RightBuccal" : 24,
        "LeftBuccal" : 25,
        "RightZygoInfraParo" : 26,
        "LeftZygoInfraParo" : 27
    }

    class_region_dictionary = {region_number: region_name for region_name, region_number in region_class_dictionary.items()} # reversed


    # Difference per pixel in region of image with region blacked out (from original UQS)
    uqs_deviation_df = pd.read_csv("blackout-regions_UQS_difference_per_pixel_from_original.csv", sep=';')

    uqs_deviation_df.columns = ["Filename", "UQS-Deviation"]
    uqs_deviation_dictionary = pd.Series(uqs_deviation_df["UQS-Deviation"].values,index=uqs_deviation_df["Filename"]).to_dict()


    region_number_UQS_difference_dictionary = {}
    for region_name, region_number in region_class_dictionary.items():
        region_blackout_filename = f"{image_name_base}_Blackout_{region_name}.jpg"
        if region_blackout_filename not in uqs_deviation_dictionary:
            region_number_UQS_difference_dictionary[region_number] = 0
            # print(region_blackout_filename)
            continue    
        region_difference = uqs_deviation_dictionary[region_blackout_filename]
        if region_difference > 0.1:
            region_difference = 0.1
        if region_difference < 0:
            region_difference = 0
        region_number_UQS_difference_dictionary[region_number] = region_difference

    # print(region_number_UQS_difference_dictionary)



    # create copy of class region mask
    # for every pixel, check class and access mean value in the mean value list and assign that as the new pixel value

    averaged_regions_image = np.zeros((222,222))

    for i in range(0,222):
        for k in range(0,222):
            if face_parsing_mask_padding[i,k] not in region_number_UQS_difference_dictionary:
                averaged_regions_image[i,k] = 0
                continue
            averaged_regions_image[i,k] = region_number_UQS_difference_dictionary[face_parsing_mask_padding[i,k]]

    # cv2.imwrite(f'Region-Removal-based/averaged-regions/averaged_regions_{image_name_base}.png', averaged_regions_image)
    plt.imsave(f'heatmaps/FRQE_heatmap_{image_name_base}.png', averaged_regions_image, cmap=plt.get_cmap('RdYlGn'), vmin=0, vmax=0.1)



    heatmap_image = cv2.imread(f'heatmaps/FRQE_heatmap_{image_name_base}.png')

    for i in range(0,222):
        for k in range(0,222):
            region_class_number = face_parsing_mask_padding[i, k]
            if region_class_number not in class_region_dictionary:
                heatmap_image[i,k] = (0,0,0)

    cv2.imwrite(f'heatmaps/FRQE_heatmap_{image_name_base}.png', heatmap_image)


    axes = []
    fig = plt.figure()
    axes.append(fig.add_subplot(1,2,1))

    original_aligned_img = cv2.imread(f"blackout-images/{image_name_base}_Blackout_Original.jpg")
    rgb_original_img = cv2.cvtColor(original_aligned_img, cv2.COLOR_BGR2RGB)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(rgb_original_img)                           
    plt.box(False)
    
    axes.append(fig.add_subplot(1,2,2))
    
    plt.xticks([])
    plt.yticks([])
    rgb_heatmap_img = cv2.cvtColor(heatmap_image, cv2.COLOR_BGR2RGB)
    plt.imshow(rgb_heatmap_img)

    # save
    plt.tight_layout()
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
        hspace = 0, wspace = 0.05)
    plt.margins(10,10)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    plt.savefig(f"combined/combined_{image_name_base}.png", bbox_inches='tight', pad_inches = 0)


# run ofiq on images to create aligned image and FGFP mask
ofiq_script_path = "C:\\Users\\admin\\source\\repos\\FaceRegionScores\\run_OFIQ_test-images.ps1" # NOTE: change to your local full path
process = subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", ofiq_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
print(stdout.decode())

for root, dirs, files in os.walk("Test-images"):
    create_blackout_images(files)


ofiq_script_path = "C:\\Users\\admin\\source\\repos\\FaceRegionScores\\run_OFIQ_blackout-images.ps1" # NOTE: change to your local full path
process = subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", ofiq_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.communicate()

compute_blackout_regions_difference_per_pixel()


for root, dirs, files in os.walk("Test-images"):
    for file in files:
        compute_Face_Region_Quality_Estimation_heatmap(file)

print("Face Region Quality Estimation finished.")