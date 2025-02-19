
# NOTE: Change to location of your OFIQ-FGFP install
Set-Location -Path "C:\\Users\\admin\\source\\repos\\OFIQ-Project-FGFP\\install_x86_64\\Release\\bin" # Change to location of your OFIQ-FGFP install

$ofiq_command = ".\\OFIQSampleApp"


# NOTE: Change to location of your local FaceRegionScores repo
$FRQE_path = "C:\\Users\\admin\\source\\repos\\FaceRegionScores" # NOTE: Change to location of your local FaceRegionScores repo

# # Compute UQS and CQMs
# $arguments = @(
#     "-c ..\\..\\..\\data\\"
#     "-i $($sub_dir.FullName)"
#     "-o .\score_files\$($sub_dir.Name)-scores.csv"
# )

# Compute only UQS
$arguments = @(
    "-c ..\\..\\..\\data\\ofiq_config_UQS_only.jaxn"
    "-i $($FRQE_path)\\blackout-images"
    "-o .\score_files\FRQE-blackout-UQS-scores.csv"
)

Start-Process -FilePath $ofiq_command -ArgumentList $arguments -Wait
