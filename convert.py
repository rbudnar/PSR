    
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import listdir, system, mkdir
from os.path import isfile, join

def get_pixel_count(path, save_files=False):
    img = cv2.imread(path, cv2.COLOR_BGR2RGB)

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    red_mask = create_mask(img_hsv, ['red'])
    mask_img = cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask)
    gray_img = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
    
    red_pixel_area = cv2.countNonZero(gray_img)        
    white_mask = create_mask(img_hsv, ['white'])
    white_mask_img = cv2.bitwise_and(img_hsv, img_hsv, mask=white_mask)
    white_mask_img_gray = cv2.cvtColor(white_mask_img, cv2.COLOR_BGR2GRAY)
    non_tissue_area = cv2.countNonZero(white_mask_img_gray)
    total_area = gray_img.shape[0] * gray_img.shape[1]
    percentage = red_pixel_area / (total_area - non_tissue_area)
        
    fig, axs = plt.subplots(3, 2, figsize=(18,18))
    fig.suptitle(f"Image: {path}", fontsize=18, fontweight='bold')
    fig.text(0.05, 0.05,
            f"TOTAL PIXELS: {total_area}; RED PIXELS: {red_pixel_area}; NON-TISSUE PIXELS: {non_tissue_area}; PERCENT RED: {percentage:f}",
            fontsize=14)
    axs[0, 0].imshow(rgb_img)
    axs[0, 0].set_title("Original image")
    axs[0, 1].imshow(img_hsv)
    axs[0, 1].set_title("HSV image")
    axs[1, 0].imshow(mask_img)
    axs[1, 0].set_title("HSV image with red mask")
    axs[1, 1].imshow(gray_img, cmap='gray')
    axs[1, 1].set_title("Converted image for pixel count")
    axs[2, 0].imshow(white_mask_img)
    axs[2, 0].set_title("Non-tissue mask")
    axs[2, 1].imshow(white_mask_img_gray, cmap='gray')
    axs[2, 1].set_title("Non-tissue image for pixel count")
    
    if save_files:
        i = path.rindex(".")
        foldername = path[:i]
        mkdir(foldername)
        plt.savefig(f"./{foldername}/{path}_plot.tif")
        save_img(img, f"{path}_original.tif", foldername)
        save_img(cv2.cvtColor(img_hsv, cv2.COLOR_BGR2RGB), f"{path}_hsv.tif", foldername)
        save_img(cv2.cvtColor(mask_img, cv2.COLOR_BGR2RGB), f"{path}_red_mask.tif", foldername)
        save_img(gray_img, f"{path}_red_mask_count.tif", foldername)
        save_img(cv2.cvtColor(white_mask_img, cv2.COLOR_BGR2RGB), f"{path}_white_mask.tif", foldername)
        save_img(white_mask_img_gray, f"{path}_white_mask_count.tif", foldername)
        
        white_mask_img_gray
    
    plt.close()

    return (red_pixel_area, non_tissue_area, total_area, percentage)

def create_mask(hsv_img, colors):
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

HSV_RANGES = {
    # red is a major color
    'red': [
        {
            'lower': np.array([0, 39, 64]),
            'upper': np.array([20, 255, 255])
        },
        {
            'lower': np.array([161, 39, 64]),
            'upper': np.array([180, 255, 255])
        }
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

onlyfiles = [f for f in listdir("./") if f.endswith(".tif")]
df = pd.DataFrame(columns=['filename', 'red_pixel_count', 'non_tissue_pixel_count','total_pixel_count', 'percent_red'])
filecount = len(onlyfiles)
for (i, file) in enumerate(onlyfiles):
    clear()
    print(f"Processing {i}/{filecount}: {file}")
    red_pixel_area, non_tissue_area, total_area, percentage = get_pixel_count(file, True)
    df.loc[i] = [file, red_pixel_area, non_tissue_area, total_area, percentage]

df.to_csv("./PSR_results.csv")
print("Done!")
