import argparse
from analyzer import RED_MASK, RED_MASK_COUNT, WHITE_MASK, WHITE_MASK_COUNT, ORIGINAL, HSV, get_pixel_count, generate_plot
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')


def draw_figure(figure_canvas_agg, loc=(0, 0)):
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def count_pixels_and_plot(path, fig, HSV_RANGES, save_files=False):
    img = cv2.imread(path, cv2.COLOR_BGR2RGB)
    red_pixel_area, non_tissue_area, total_area, percentage, images = get_pixel_count(
        ".", path, HSV_RANGES, img, save_files=False)
    draw_plot(fig, path, red_pixel_area, non_tissue_area,
              total_area, percentage, images)

    print(f"RED PIXELS: {red_pixel_area}")
    print(f"NON-TISSUE PIXELS: {non_tissue_area}")
    print(f"TOTAL PIXELS: {total_area}")
    print(f"PERCENT RED: {percentage}")


def draw_plot(fig, path, red_pixel_area, non_tissue_area, total_area, percentage, images):
    fig.clear()
    fig.suptitle(f"Image: {path}", fontsize=14, fontweight='bold')
    fig.text(0.05, 0.05,
             f"TOTAL PIXELS: {total_area}; RED PIXELS: {red_pixel_area}; NON-TISSUE PIXELS: {non_tissue_area}; PERCENT RED: {percentage:f}",
             fontsize=10)

    plot_image(images[ORIGINAL], "Original image", 321)
    plot_image(images[HSV], "HSV image", 322)
    plot_image(images[RED_MASK], "HSV image with red mask", 323)
    plot_image(images[RED_MASK_COUNT],
               "Converted image for pixel count", 324, gray=True)
    plot_image(images[WHITE_MASK], "Non-tissue mask", 325)
    plot_image(images[WHITE_MASK_COUNT],
               "Non-tissue image for pixel count", 326, gray=True)


def plot_image(image, text, plot, gray=False):
    ax = plt.subplot(plot)
    ax.title.set_text(text)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plt.imshow(image, cmap="gray") if gray else plt.imshow(image)


def setup_window(image_path):
    HSV_RANGES = {
        'red': [
            {
                'lower': np.array([154, 118, 106]),
                'upper': np.array([194, 249, 206])
            },
        ],
        'white': [
            {
                'lower': np.array([6, 0, 145]),
                'upper': np.array([46, 40, 245])
            }
        ]
    }

    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
    sg.change_look_and_feel('DarkAmber')

    layout = [
        [
            sg.Frame("Red mask settings", [[
                sg.Frame("Lower Bound", [
                    [sg.Text("R"), sg.Slider(range=(
                        0, 255), default_value=HSV_RANGES['red'][0]['lower'][0], resolution=1, orientation="h")],
                    [sg.Text("G"), sg.Slider(range=(
                        0, 255), default_value=HSV_RANGES['red'][0]['lower'][1], resolution=1, orientation="h")],
                    [sg.Text("B"), sg.Slider(range=(
                        0, 255), default_value=HSV_RANGES['red'][0]['lower'][2], resolution=1, orientation="h")]
                ]),
                sg.Frame("Upper Bound", [
                    [sg.Text("R"), sg.Slider(range=(
                        0, 255), default_value=HSV_RANGES['red'][0]['upper'][0], resolution=1, orientation="h")],
                    [sg.Text("G"), sg.Slider(range=(
                        0, 255), default_value=HSV_RANGES['red'][0]['upper'][1], resolution=1, orientation="h")],
                    [sg.Text("B"), sg.Slider(range=(
                        0, 255), default_value=HSV_RANGES['red'][0]['upper'][2], resolution=1, orientation="h")]
                ]),
            ]], border_width=0)
        ],
        [sg.Canvas(size=(figure_w, figure_h), key='canvas')],
        [sg.Button('Close')]
    ]

    # Create the Window
    window = sg.Window('Picker', layout)
    window.Finalize()
    canvas_elem = window['canvas']
    graph = FigureCanvasTkAgg(fig, master=canvas_elem.TKCanvas)
    canvas = canvas_elem.TKCanvas
    currentVals = None

    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)

    while True:
        event, values = window.read(timeout=100)

        if event in (None, 'Close'):
            break
        if currentVals != values:
            canvas.delete("all")
            HSV_RANGES = {
                'red': [
                    {
                        'lower': np.array([values[0], values[1], values[2]]),
                        'upper': np.array([values[3], values[4], values[5]])
                    },
                ],
                'white': [
                    {
                        'lower': np.array([6, 0, 145]),
                        'upper': np.array([46, 40, 245])
                    }
                ]
            }
            count_pixels_and_plot(image_path, fig, HSV_RANGES)
            draw_figure(figure_canvas_agg)
        currentVals = values

    window.close()


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the image")
args = vars(ap.parse_args())

setup_window(args["image"])
