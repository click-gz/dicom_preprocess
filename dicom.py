import SimpleITK as sitk
import os, glob
import numpy as np
import pydicom

def get_slope_intercept(image):
    slope = image.RescaleSlope
    intercept = image.RescaleIntercept
    return slope, intercept

def pixel_array_to_hu(pixel_array, slope, intercept):
    hu_array = (slope * pixel_array) + intercept
    return hu_array

# Set the directory containing the DICOM files
dicom_dir = ".\\dicom\\*"
dicom_path = glob.glob(dicom_dir)
print(dicom_path)
# exit()
for file_path in dicom_path:
    # Load the DICOM files and stack them into a 3D volume
    reader = sitk.ImageSeriesReader()

    dicom_names = reader.GetGDCMSeriesFileNames(file_path)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()

    image_array = sitk.GetArrayFromImage(image)

    name1 = dicom_names[0]
    dcm_file1 = pydicom.dcmread(name1)



    # Resample the volume to a common voxel spacing of 1 mm in all directions
    new_spacing = [1, 1, 1]
    resampled_image = sitk.Resample(image, [int(sz * spc / new_spacing[i]) for i, sz, spc in zip(range(3), image.GetSize(), image.GetSpacing())], sitk.Transform(), sitk.sitkLinear, image.GetOrigin(), new_spacing, image.GetDirection(), 0.0, image.GetPixelID())
    resampled_image.SetSpacing(new_spacing)

    print("re: ", resampled_image.GetSize())
    # Convert the pixel values to Hounsfield units
    # hounsfield_image = resampled_image * image.GetMetaData("RescaleSlope") + image.GetMetaData("RescaleIntercept")
    slope, intercept = get_slope_intercept(dcm_file1)

    # hu_array = pixel_array_to_hu(resampled_image.GetArrayFromImage(), slope, intercept)
    hounsfield_image = pixel_array_to_hu(resampled_image, slope, intercept)
    # Center crop the images to a shape of 320x320x320
    crop_size = [320, 320, 320]
    crop_origin = [(sz - cp) // 2 for sz, cp in zip(hounsfield_image.GetSize(), crop_size)]
    cropped_image = sitk.RegionOfInterest(hounsfield_image, crop_size, crop_origin)

    # Resize the processed images to 128x128x128
    resize_size = [128, 128, 128]
    resized_image = sitk.Resample(cropped_image, resize_size, sitk.Transform(), sitk.sitkLinear, cropped_image.GetOrigin(), [sz * spc / rs for sz, spc, rs in zip(cropped_image.GetSize(), cropped_image.GetSpacing(), resize_size)], cropped_image.GetDirection(), 0.0, cropped_image.GetPixelID())

    # Min-max normalize the images to the range between -1 and 1
    print(type(resized_image))
    array = sitk.GetArrayFromImage(resized_image)
    min_val = array.min()
    max_val = array.max()
    normalized_image = (2.0 * resized_image - (max_val + min_val)) / (max_val - min_val)
    print(normalized_image[0].GetSize())
    print(type(normalized_image))
    # Save the images to a new directory with the same structure as the original directory
    save_dir = file_path
    for i in range(128):

        # os.makedirs(os.path.dirname(save_dir), exist_ok=True)
        # slice_idx = int(file_path.split("\\")[-1].replace(".dcm", "")) - 1
        save_path = save_dir + "\\" + str(i) + ".npy"
        np.save(save_path, normalized_image[i])

# # import cv2
# ar = sitk.GetArrayFromImage(normalized_image)
# print("ar", ar.shape)
# 
# sitk.WriteImage(normalized_image[96], "./1.nii")

