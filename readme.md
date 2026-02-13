# Picrosirius Red Stain Tissue Image Quantification

## Overview

This tool automates the quantification of tissue images stained with Picrosirius Red (PSR) using Python and OpenCV. It calculates the percentage of pixels attributed to the red stain, effectively quantifying collagen content or similar features.

The primary way to use this tool is through the **PSR Analyzer GUI** (`psr_analyzer_gui.py`), which provides an interactive interface for color selection, mask configuration, and high-performance batch processing.

## Setup

1.  **Python 3.x**: Ensure you have Python installed (download from [python.org](https://www.python.org/)).
2.  **Clone/Download**: Download this repository to your local machine.
3.  **Install Dependencies**: Open a command prompt in the project folder and run:
    ```bash
    pip install -r requirements.txt
    ```

## PSR Analyzer GUI

The GUI allows you to interactively build color masks and process images with precision.

### Starting the Application
Simply run:
```bash
python psr_analyzer_gui.py
```

### Key Features

*   **Interactive Color Selection**: 
    *   Click "Load Image" to open a tissue sample.
    *   Click anywhere on the image to select a color.
    *   Adjust the **Hue, Saturation, and Value (HSV) tolerances** to expand or contract the selection range.
    *   Click "Add Color" to add that specific range to either the **Red Mask** (target tissue) or the **Non-Tissue Mask** (background/voids).
    *   You can add multiple colors to each mask to capture various shades and lighting conditions.
*   **Zoom and Pan**: Use the toolbar below the image to zoom into specific areas for pixel-perfect color picking.
*   **Save/Load Settings**: Once you've perfected your mask configurations, use "Save Settings" to create a JSON file. This allows you to reload the exact same parameters for future analysis, ensuring consistency.
*   **Parallel Batch Processing**:
    *   Click "Batch Process" to analyze an entire folder of images.
    *   Select your input folder containing `.jpg` images and a destination folder for results.
    *   The tool will process images in parallel using multiple CPU cores for maximum speed.
    *   A progress bar will track the operation.

### Batch Results Structure
The output folder will contain:
*   **`plots/`**: A folder containing summary plots for every image, allowing for rapid visual review.
*   **Individual Subfolders**: Detailed results for each image, including the generated masks and filtered images.
*   **`PSR_results.csv`**: A spreadsheet containing the quantification data (pixel counts and percentages) for all processed images.
*   **`image_settings.json`**: A record of the exact color settings used for that specific batch run.

---

## Command Line Interface (Advanced)

For users who prefer the command line or want to integrate the analyzer into other scripts, `analyzer.py` can be run directly:

```bash
python analyzer.py -p "./path/to/your/images/folder"
```

*   `-p`: Path to the image directory.
*   `-x`: (Optional) Image file extension (defaults to `.tif`).

Results will be saved similarly to the batch processing output, with a `PSR_results.csv` file generated in the target directory.
