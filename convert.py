
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import listdir, system, mkdir
from os.path import isfile, join
import argparse

RED_MASK = "red_mask"
RED_MASK_COUNT = "red_mask_count"
WHITE_MASK = "white_mask"
WHITE_MASK_COUNT = "white_mask_count"
ORIGINAL = "original"
HSV = "hsv"

"""
These HSV Ranges can be modified as needed to change the mask.
Note that only white and red are used here.
"""
HSV_RANGES = {
    # red is a major color
    # note that other shades of red were tested for analysis
    'red': [
        {
            'lower': np.array([154, 118, 106]),
            'upper': np.array([194, 249, 206])
        },
    ],
    # yellow is a minor color
    'yellow': [
        {
            'lower': np.array([21, 39, 64]),
            'upper': np.array([40, 255, 255])
        }
    ],
    # green is a major color
    'green': [
        {
            'lower': np.array([41, 39, 64]),
            'upper': np.array([80, 255, 255])
        }
    ],
    # cyan is a minor color
    'cyan': [
        {
            'lower': np.array([81, 39, 64]),
            'upper': np.array([100, 255, 255])
        }
    ],
    # blue is a major color
    'blue': [
        {
            'lower': np.array([101, 39, 64]),
            'upper': np.array([140, 255, 255])
        }
    ],
    # violet is a minor color
    'violet': [
        {
            'lower': np.array([141, 39, 64]),
            'upper': np.array([160, 255, 255])
        }
    ],
    # next are the monochrome ranges
    # black is all H & S values, but only the lower 25% of V
    'black': [
        {
            'lower': np.array([0, 0, 0]),
            'upper': np.array([180, 255, 63])
        }
    ],
    # gray is all H values, lower 15% of S, & between 26-89% of V
    'gray': [
        {
            'lower': np.array([0, 0, 64]),
            'upper': np.array([180, 38, 228])
        }
    ],
    'white': [
        {
            'lower': np.array([6, 0, 145]),
            'upper': np.array([46, 40, 245])
        }
    ]
}


def get_pixel_count(path_to_img_dir, filename, HSV_RANGES, original_image=None, save_files=False):
    """
    Generates pixel counts for red stained tissue, non tissue area, total area, and the resulting percentage.
    Tissue area is quantified as total_area - non_tissue_area.
    """
    images = dict()
    img = cv2.imread(
        f"./{path_to_img_dir}/{filename}") if original_image is None else original_image

    images[ORIGINAL] = rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    images[HSV] = img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask_red = create_mask(img_hsv, ['red'], HSV_RANGES)
    images[RED_MASK] = red_mask = cv2.bitwise_and(
        img_hsv, img_hsv, mask=mask_red)
    images[RED_MASK_COUNT] = red_mask_count = cv2.cvtColor(
        red_mask, cv2.COLOR_BGR2GRAY)
    red_pixel_area = cv2.countNonZero(red_mask_count)

    mask_white = create_mask(img_hsv, ['white'], HSV_RANGES)
    images[WHITE_MASK] = white_mask = cv2.bitwise_and(
        img_hsv, img_hsv, mask=mask_white)
    images[WHITE_MASK_COUNT] = white_mask_count = cv2.cvtColor(
        white_mask, cv2.COLOR_BGR2GRAY)

    non_tissue_area = cv2.countNonZero(white_mask_count)
    total_area = red_mask_count.shape[0] * red_mask_count.shape[1]
    percentage = red_pixel_area / (total_area - non_tissue_area)

    return (red_pixel_area, non_tissue_area, total_area, percentage, images)


def generate_plot(images, filename, total_area, red_pixel_area, non_tissue_area, percentage, path_to_new_folder, save_files, clear_fig=False):
    """
    Generates a plot with all 6 images used for analysis with resulting pixel counts and percentages.
    """
    fig, axs = plt.subplots(3, 2, figsize=(18, 18))
    fig.suptitle(f"Image: {filename}", fontsize=18, fontweight='bold')
    fig.text(0.05, 0.05,
             f"TOTAL PIXELS: {total_area}; RED PIXELS: {red_pixel_area}; NON-TISSUE PIXELS: {non_tissue_area}; PERCENT RED: {percentage:f}",
             fontsize=14)
    axs[0, 0].imshow(images[ORIGINAL])
    axs[0, 0].set_title("Original image")
    axs[0, 1].imshow(images[HSV])
    axs[0, 1].set_title("HSV image")
    axs[1, 0].imshow(images[RED_MASK])
    axs[1, 0].set_title("HSV image with red mask")
    axs[1, 1].imshow(images[RED_MASK_COUNT], cmap='gray')
    axs[1, 1].set_title("Converted image for pixel count")
    axs[2, 0].imshow(images[WHITE_MASK])
    axs[2, 0].set_title("Non-tissue mask")
    axs[2, 1].imshow(images[WHITE_MASK_COUNT], cmap='gray')
    axs[2, 1].set_title("Non-tissue image for pixel count")

    if save_files:
        plt.savefig(f"{path_to_new_folder}/{filename}_plot.tif")

    plt.close()


def save_images(images, path_to_new_folder, filename):
    """
    Persists generated images for review.
    """
    for (key, image) in images.items():
        save_img(cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                 f"{filename}_{key}.tif", path_to_new_folder)


def create_mask(hsv_img, colors, HSV_RANGES):
    """
    Creates a binary mask from HSV image using given colors.
    """
    mask = np.zeros((hsv_img.shape[0], hsv_img.shape[1]), dtype=np.uint8)

    for color in colors:
        for color_range in HSV_RANGES[color]:
            mask += cv2.inRange(
                hsv_img,
                color_range['lower'],
                color_range['upper']
            )

    return mask


def clear():
    system('cls')


def save_img(img, img_name, path):
    cv2.imwrite(f"./{path}/{img_name}", img)


def generate_path_to_new_folder(filename, path_to_img_dir):
    i = filename.rindex(".")
    foldername = filename[:i]
    return f"./{path_to_img_dir}/{foldername}"


def run(path_to_img_dir, image_format, save_files=True):
    """
    Runs the procedure to generate pixel counts for the given images.
    """
    # Grab files from specified directory
    onlyfiles = [f for f in listdir(
        path_to_img_dir) if f.endswith(image_format)]
    # create Data frame for pixel stats results
    df = pd.DataFrame(columns=['filename', 'red_pixel_count',
                               'non_tissue_pixel_count', 'total_pixel_count', 'percent_red'])
    filecount = len(onlyfiles)
    for (i, filename) in enumerate(onlyfiles):
        clear()
        print(f"Processing {i}/{filecount}: {filename}")
        red_pixel_area, non_tissue_area, total_area, percentage, images = get_pixel_count(
            path_to_img_dir, filename, HSV_RANGES)

        path_to_new_folder = generate_path_to_new_folder(
            filename, path_to_img_dir)

        if save_files:
            mkdir(path_to_new_folder)
            save_images(images, path_to_new_folder, filename)

        generate_plot(images, filename, total_area, red_pixel_area,
                      non_tissue_area, percentage, path_to_new_folder, save_files)
        # add results to dataframe
        df.loc[i] = [filename, red_pixel_area,
                     non_tissue_area, total_area, percentage]

    df.to_csv("./PSR_results.csv")
    print("Done!")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-p", "--path", help="path to the images folder, e.g., ./python convert.py -p './images'", required=True)
    ap.add_argument(
        "-x", "--ext", help="image file extension", default=".tif")
    args = vars(ap.parse_args())

    run(args["path"], image_format=args["ext"])
