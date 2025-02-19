Face Region Quality Estimation
===========================

This is the Face Region Quality Estimation (FRQE) project.

It is dependent on the Fine-Grained Face Parsing version of OFIQ. That project must be installed for this project to work.

Before running FRQE, you have to change some hard coded full paths to the installation of the Fine-Grained Face Parsing version of OFIQ.
These paths are found here:
- FRQE.py
    - Line 19
    - Line 131
    - Line 140
- run_OFIQ_blackout-images.ps1
    - Line 3
    - Line 9
- run_OFIQ_test-images.ps1
    - Line 3
    - Line 9
- RegionRemoval\black_out_sub_regions.py
    - Line 39
    - Line 41
- RegionRemoval\compute_averages_of_blackout_regions_UQS.py
    - Line 12


FRQE.py runs on the images in the Test-images folder.

It starts a powershell subprocess running OFIQ-FGFP on the images in Test-images. This produces an aligned image and a FGFP mask saved in the installation folder of OFIQ-FGFP.

Then a copy of the aligned image is created for each region with that specific region blacked out. These are saved in the blakout-images folder.

It starts a powershell subprocess running OFIQ-FGFP on the images in blackout-images, computing UQS for each image. The score file is saved in the installation folder of OFIQ-FGFP.

Then the difference in UQS per pixel for each blackout image is computed. The values are saved in blackout-regions_UQS_difference_per_pixel_from_original.csv.

Then the FRQE algorithm is run for the images in Test-images, which computes the heat maps and saves them in the heatmaps folder. The original image alongside the heat map is saved as one image file in the combined folder
--------------------------------


![Example heatmap and image](./combined/combined_image2.png)
