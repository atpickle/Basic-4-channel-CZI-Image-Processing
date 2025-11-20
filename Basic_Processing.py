def rename_and_copy_czi_files(main_folder_path):
    import os
    import shutil
    """
    Rename all .czi files in each subfolder of a directory to the name of the folder with an incremental number at the end,
    and copy them to a new "All" folder.

    Parameters
    ----------
    main_folder_path : str
        Path to the main folder containing subfolders with .czi files.
    Returns
    -------
    None
    """
    # First, rename all .czi files
    for root, dirs, files in os.walk(main_folder_path):
        for folder_name in dirs:
            if folder_name == "All":
                continue  # Skip the "All" folder
            folder_path = os.path.join(root, folder_name)
            
            # Get a list of all CZI files in the folder
            czi_files = [file for file in os.listdir(folder_path) if file.endswith(".czi")]
            
            # Sort the files to ensure they are renamed in the order they appear in the folder
            czi_files.sort()

            # Rename the CZI files
            for j, czi_file in enumerate(czi_files):
                new_name = f"{folder_name}_{j+1:02d}.czi"
                os.rename(os.path.join(folder_path, czi_file), os.path.join(folder_path, new_name))

    # Create the "All" folder if it doesn't exist
    all_folder_path = os.path.join(main_folder_path, "All")
    if not os.path.exists(all_folder_path):
        os.makedirs(all_folder_path)

    # Then, copy all renamed .czi files into the "All" folder
    for root, dirs, files in os.walk(main_folder_path):
        for folder_name in dirs:
            if folder_name == "All":
                continue  # Skip the "All" folder
            folder_path = os.path.join(root, folder_name)
            
            # Get a list of all renamed CZI files in the folder
            czi_files = [file for file in os.listdir(folder_path) if file.endswith(".czi")]
            
            # Copy the files to the "All" folder, skipping repeat files
            for file_name in czi_files:
                src_file_path = os.path.join(folder_path, file_name)
                dst_file_path = os.path.join(all_folder_path, file_name)
                
                if not os.path.exists(dst_file_path):
                    shutil.copy2(src_file_path, dst_file_path)

def Split_CZI_Channels(folder_path):

    import os
    import shutil
    import czifile
    from tifffile import imwrite    

    for filename in os.listdir(folder_path):
        if filename.endswith(".czi"):
            czi_path = os.path.join(folder_path, filename)
            with czifile.CziFile(czi_path) as czi:
                image_arrays = czi.asarray()
                for channel_idx, channel_image in enumerate(image_arrays):
                    tiff_path = os.path.splitext(czi_path)[0] + f"_C_{channel_idx}.tiff"
                    imwrite(tiff_path, channel_image)
    
    # Move the czi file to the "Original_CZI" folder
    czi_folder = os.path.join(folder_path, '0_Original CZI')
    os.makedirs(czi_folder, exist_ok=True)

    files = os.listdir(folder_path)
    for file in files:
        if file.endswith('.czi'):
                shutil.move(os.path.join(folder_path, file), czi_folder)
                   
    print(f"✓ Converted czi files to tiffs")

def Apply_Gaussian(folder_path, sigma, display, save):
    import cv2
    import os
    import matplotlib.pyplot as plt
    from scipy import ndimage
    """Apply a Gaussian filter to images in a folder

    Parameters
    ----------
    folder_path : str
        Path to the folder containing the images
    sigma : float
        Standard deviation of the Gaussian kernel

    Returns
    -------
    None
    """

    # Get a list of all image files in the folder
    image_files = [file for file in os.listdir(folder_path) if file.endswith('.tiff') or file.endswith('.tif')]

    # Iterate over each image file
    for image_file in image_files:
        # Construct the full path to the image file
        image_path = os.path.join(folder_path, image_file)

        # Read the image
        image = cv2.imread(image_path)

        # Apply Gaussian filter
        filtered_image = ndimage.gaussian_filter(image, sigma)

        if display:
            plt.imshow(cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB))
            plt.title(f"Gaussian Filtered: {image_file}")
            plt.axis('off')
            plt.show()

        if save:
            filtered_image_path = os.path.join(folder_path, image_file)
            cv2.imwrite(filtered_image_path, filtered_image)

def Convert_to_8bit(folder_path):
    import os
    import cv2

    # Get a list of all TIFF files in the folder
    image_files = [file for file in os.listdir(folder_path) if file.endswith('.tiff') or file.endswith('.tif')]

    # Iterate over each image file
    for image_file in image_files:
        # Construct the full path to the image file
        image_path = os.path.join(folder_path, image_file)

        # Read the image
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        # Convert the image to 8-bit
        image_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')

        # Save the 8-bit image
        cv2.imwrite(image_path, image_8bit)

    print(f"✓ Converted all TIFF images in {folder_path} to 8-bit")

# def Background_Subtraction(folder_path, radius, display, save):

#     import os
#     import warnings
#     from skimage import io
#     from skimage.restoration import rolling_ball
#     import numpy as np
#     import tifffile
#     from matplotlib import pyplot as plt

#     """
#     Apply a 50-pixel radius rolling ball background subtraction to TIFF files in a folder and save the results.

#     Parameters
#     ----------
#     folder_path : str
#         Path to the folder containing the TIFF images.
#     radius : int, optional
#         Radius of the rolling ball. Default is 50.

#     Returns
#     -------
#     None
#     """
#     # Create a subfolder for the processed images
#     processed_folder = os.path.join(folder_path, "1_Background Subtraction")
#     os.makedirs(processed_folder, exist_ok=True)

#     # Get a list of all TIFF files in the folder
#     image_files = [file for file in os.listdir(folder_path) if file.endswith('.tiff') or file.endswith('.tif')]

#     if not image_files:
#         return

#     # Suppress low contrast image warnings
#     warnings.filterwarnings("ignore", category=UserWarning, message=".*is a low contrast image.*")

#     # Iterate over each image file
#     for image_file in image_files:
#         # Construct the full path to the image file
#         image_path = os.path.join(folder_path, image_file)

#         # Read the image
#         with tifffile.TiffFile(image_path) as tif:
#             image = tif.asarray()

#         # Apply the rolling ball algorithm for background subtraction
#         background = rolling_ball(image, radius=radius)
#         subtracted_image = image - background

#         # Ensure the pixel values are within the valid range
#         subtracted_image = np.clip(subtracted_image, 0, 255).astype(np.uint8)
#         if display:
#             # Display the subtracted image
#             plt.imshow(subtracted_image, cmap='gray')
#             plt.title(f"Background Subtracted: {image_file}")
#             plt.axis('off')
#             plt.show()

#         # Save the processed image to the processed folder
#         if save: 
#             processed_image_path = os.path.join(processed_folder, image_file)
#             tifffile.imwrite(processed_image_path, subtracted_image)


def Background_Subtraction(folder_path, radius, display, save):
    import os
    import warnings
    from skimage.restoration import rolling_ball
    import numpy as np
    import tifffile
    from matplotlib import pyplot as plt
    import shutil

    """
    Apply a rolling ball background subtraction to TIFF files in a folder and save the results.
    Move the original images into a new folder called "Unprocessed tiffs".

    Parameters
    ----------
    folder_path : str
        Path to the folder containing the TIFF images.
    radius : int
        Radius of the rolling ball.
    display : bool
        Whether to display the processed images.
    save : bool
        Whether to save the processed images.

    Returns
    -------
    None
    """
    # Create subfolders for processed and unprocessed images
    processed_folder = os.path.join(folder_path, "1_Background Subtraction")
    unprocessed_folder = os.path.join(folder_path, "Unprocessed tiffs")
    os.makedirs(processed_folder, exist_ok=True)
    os.makedirs(unprocessed_folder, exist_ok=True)

    # Get a list of all TIFF files in the folder
    image_files = [file for file in os.listdir(folder_path) if file.endswith('.tiff') or file.endswith('.tif')]

    if not image_files:
        print("No TIFF files found in the folder.")
        return

    # Suppress low contrast image warnings
    warnings.filterwarnings("ignore", category=UserWarning, message=".*is a low contrast image.*")

    # Iterate over each image file
    for image_file in image_files:
        # Construct the full path to the image file
        image_path = os.path.join(folder_path, image_file)

        # Read the image
        with tifffile.TiffFile(image_path) as tif:
            image = tif.asarray()

        # Apply the rolling ball algorithm for background subtraction
        background = rolling_ball(image, radius=radius)
        subtracted_image = image - background

        # Ensure the pixel values are within the valid range
        subtracted_image = np.clip(subtracted_image, 0, 255).astype(np.uint8)

        if display:
            # Display the subtracted image
            plt.imshow(subtracted_image, cmap='gray')
            plt.title(f"Background Subtracted: {image_file}")
            plt.axis('off')
            plt.show()

        # Save the processed image to the processed folder
        if save:
            processed_image_path = os.path.join(processed_folder, image_file)
            tifffile.imwrite(processed_image_path, subtracted_image)

        # Move the original image to the "Unprocessed tiffs" folder
        shutil.move(image_path, os.path.join(unprocessed_folder, image_file))


def Optimize_Contrast(folder_path, display, save):
    import skimage
    from skimage import io, exposure
    import matplotlib.pyplot as plt
    import os
    import numpy as np

    """Optimize the contrast of images in a folder and display the results

    Parameters
    ----------
    folder_path : str
        Path to the folder containing the images

    Returns
    -------
    None
    """
    # Get a list of all image files in the folder
    image_files = [file for file in os.listdir(folder_path) if file.endswith('.tiff') or file.endswith('.tif')]

    # Iterate over each image file
    for image_file in image_files:
        # Construct the full path to the image file
        image_path = os.path.join(folder_path, image_file)

        img = skimage.io.imread(image_path)

        # Normalize the image to be between -1 and 1
        img = img / np.max(np.abs(img))

        # Optimize the contrast of the image
        img_optimized = exposure.equalize_adapthist(img)

        # Specify the file path of the optimized image
        optimized_image_path = os.path.join(folder_path, image_file)

       

        if display:
            fig, axes = plt.subplots(1, 2, figsize=(10, 5))
            axes[0].imshow(img, cmap='gray')
            axes[0].set_title('Original Image')
            axes[0].axis('off')
            axes[1].imshow(img_optimized, cmap='gray')
            axes[1].set_title('Optimized Image')
            axes[1].axis('off')
            plt.show()

        if save:
            skimage.io.imsave(optimized_image_path, img_optimized)

def Copy_all_tiffs_to_single_folder(folder_path):
    import os
    import shutil   
        
    # Create the "All" directory if it doesn't exist
    all_dir = os.path.join(folder_path, "All")
    os.makedirs(all_dir, exist_ok=True)
    
    # Walk through the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".tiff") or file.endswith(".tif"):
                # Copy the file to the "All" directory
                src_file = os.path.join(root, file)
                dest_file = os.path.join(all_dir, file)
                
                # Check if the source and destination files are the same
                if os.path.abspath(src_file) != os.path.abspath(dest_file):
                    shutil.copy2(src_file, dest_file)
                else:
                    print(f"Skipping {src_file} as it is the same as {dest_file}")