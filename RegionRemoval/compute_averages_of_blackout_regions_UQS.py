import pandas as pd

# Author: Gustav Nilsson Pedersen - s174562@student.dtu.dk

def convert_blackout_filename_to_original_filename(filename):
    region = filename.split('_')[-1].split('.')[0]
    split_filename = filename.split(region)
    original_image_filename = split_filename[0] + "Original.jpg"
    # print(original_image_filename)
    return original_image_filename

def compute_blackout_regions_difference_per_pixel():
    score_file = "C:\\Users\\admin\\source\\repos\\OFIQ-Project-FGFP\\install_x86_64\\Release\\bin\\score_files\\FRQE-blackout-UQS-scores.csv"
    score_df = pd.read_csv(score_file, sep=';')

    originals_df = score_df[score_df["Filename"].apply(lambda filename: "_Original" in filename)]
    # print(len(originals_df))

    region_names = [
        "LeftEyeBrow",
        "RightyeBrow",
        "LeftEye",
        "RightEye",
        "Nose",
        "Mouth",
        "UpperLip",
        "LowerLip",
        "Nasal",
        "LeftOrbital",
        "RightOrbital",
        "Mental",
        "LeftBuccal",
        "RightBuccal",
        "LeftZygoInfraParo",
        "RightZygoInfraParo",
    ]


    region_pixel_count_file = "region_pixel_count.csv" # should have row structure: <blackout-image-filename>;<region-pixel-count>
    region_pixel_count_df = pd.read_csv(region_pixel_count_file, sep=';', header=None)
    region_pixel_count_df.columns = ['Filename', 'pixel_count']
    region_pixel_count_df["Filename"] = region_pixel_count_df["Filename"].apply(lambda x: x.split("\\")[-1]) # only keep actual filename, not full path

    # print(region_pixel_count_df.head())

    region_average_difference_per_pixel_per_image_dictionary = { "Originals" : 0.0 }
    difference_per_pixel_blackout_region_scores_filenames = []
    for region in region_names:
        blackout_region_UQS_scores_df = score_df[score_df["Filename"].apply(lambda filename: f"{region}." in filename)] # ends with region
        # print(len(blackout_region_UQS_scores_df))
        # print(blackout_region_UQS_scores_df)
        

        # ========= Only consider regions where the region was actually identified, so there are >0 pixels ==========
        blackout_region_UQS_scores_and_pixel_count_df = pd.merge(blackout_region_UQS_scores_df, region_pixel_count_df, on='Filename', how='left')
    
        # ========== Remove rows that have 0 pixels in regions ==========
        blackout_region_UQS_scores_and_pixel_count_with_more_than_0_pixels_df = blackout_region_UQS_scores_and_pixel_count_df[~(blackout_region_UQS_scores_and_pixel_count_df["pixel_count"] == 0)]
        # print(len(blackout_region_UQS_scores_and_pixel_count_with_more_than_0_pixels_df))
        blackout_region_UQS_scores_df = blackout_region_UQS_scores_and_pixel_count_with_more_than_0_pixels_df[blackout_region_UQS_scores_df.columns]
        # print(blackout_region_UQS_scores_df.head())
        # print(len(blackout_region_UQS_scores_df))
        original_filenames_of_blackout_images_dict_for_lookup = dict.fromkeys(blackout_region_UQS_scores_df["Filename"].apply(convert_blackout_filename_to_original_filename).values, 0)
        # print(f"original_filenames_of_blackout_images_dict_for_lookup lenght for region {region}: {len(original_filenames_of_blackout_images_dict_for_lookup)}")
        originals_of_non_zero_images_df = originals_df[originals_df["Filename"].apply(lambda filename: filename in original_filenames_of_blackout_images_dict_for_lookup)]
        # print(len(originals_of_non_zero_images_df))



        # ========== Compute difference from original ==========
        difference_from_original_series = originals_of_non_zero_images_df["UnifiedQualityScore.scalar"] - blackout_region_UQS_scores_df["UnifiedQualityScore.scalar"].values
        # print(difference_from_original_series)
        

        # ========== Compute mean difference per pixel per image ==========
        differences_df = pd.concat([blackout_region_UQS_scores_df["Filename"].reset_index(drop=True), difference_from_original_series.reset_index(drop=True)], axis=1, ignore_index=True)
        differences_df.columns = ["Filename", "UQSDifferenceFromOriginal"]
        # print(differences_df)

        differences_df["Filename"] = differences_df["Filename"].apply(lambda x: x.split("/")[-1]) # only keep actual filename, not full path
        differences_and_pixel_count_df = pd.merge(differences_df, region_pixel_count_df, on='Filename', how='left')
        # print(differences_and_pixel_count_df)
        differences_per_pixel_series = differences_and_pixel_count_df["UQSDifferenceFromOriginal"].div(differences_and_pixel_count_df["pixel_count"], axis=0)
        differences_and_pixel_count_df["DifferencePerPixel"] = differences_per_pixel_series


        # print(difference_per_pixel_df.head())
        average_difference_per_pixel_per_image = differences_per_pixel_series.mean()
        region_average_difference_per_pixel_per_image_dictionary[region] = average_difference_per_pixel_per_image
        # print(f"Average difference per pixel per image for images with {region} blacked out: {average_difference_per_pixel_per_image}")

        difference_per_pixel_with_filename_df = pd.concat([differences_df["Filename"].reset_index(drop=True), differences_per_pixel_series.reset_index(drop=True)], axis=1, ignore_index=True)
        # print(difference_per_pixel_with_filename_df.head())
        dpp_region_filename = f"./difference_per_pixel_blackout_region_scores/blackout-region_UQS_difference_per_pixel_from_original-{region}.csv"
        difference_per_pixel_blackout_region_scores_filenames.append(dpp_region_filename)
        difference_per_pixel_with_filename_df.to_csv(dpp_region_filename, sep=';', index=False)


    # ========= Combine difference per pixel blackout region score files in one file =============

    dpp_combined_df = pd.concat([pd.read_csv(file, sep=';') for file in difference_per_pixel_blackout_region_scores_filenames], ignore_index=True)
    dpp_combined_df.to_csv(f"blackout-regions_UQS_difference_per_pixel_from_original.csv", sep=';', index=False)
