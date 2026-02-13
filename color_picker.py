import argparse
from analyzer import RED_MASK, RED_MASK_COUNT, WHITE_MASK, WHITE_MASK_COUNT, ORIGINAL, HSV, get_pixel_count, generate_plot
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
import matplotlib
matplotlib.use('TkAgg')


def count_pixels_and_plot(path, fig, HSV_RANGES, img, save_files=False):
    red_pixel_area, non_tissue_area, total_area, percentage, images = get_pixel_count(
        ".", path, HSV_RANGES, img, save_files=False)
    draw_plot(fig, path, red_pixel_area, non_tissue_area,
              total_area, percentage, images)

    print(f"RED PIXELS: {red_pixel_area}")
    print(f"NON-TISSUE PIXELS: {non_tissue_area}")
    print(f"TOTAL PIXELS: {total_area}")
    print(f"PERCENT RED: {percentage}")
    return images


def draw_plot(fig, path, red_pixel_area, non_tissue_area, total_area, percentage, images):
    fig.clear()
    fig.suptitle(f"Image: {path}", fontsize=14, fontweight='bold')
    fig.text(0.05, 0.05,
             f"TOTAL PIXELS: {total_area}; RED PIXELS: {red_pixel_area}; NON-TISSUE PIXELS: {non_tissue_area}; PERCENT RED: {percentage:f}",
             fontsize=10)

    plot_image(images[ORIGINAL], "Original image", 321)
    # Convert HSV to RGB for correct display
    hsv_display = cv2.cvtColor(images[HSV], cv2.COLOR_HSV2RGB)
    plot_image(hsv_display, "HSV image", 322)
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
    
    img = cv2.imread(image_path)
    images = {}

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Pixel Counter")
    root.geometry("1000x1000")

    fig = plt.figure(figsize=(7, 7), dpi=100)

    canvas_frame = ctk.CTkFrame(root)
    canvas_frame.pack(side="right", fill="both", expand=True)

    figure_canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    figure_canvas.draw()
    figure_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    def on_click(event):
        if event.inaxes and event.inaxes.get_title() in ["Original image", "HSV image"]:
            x, y = int(event.xdata), int(event.ydata)
            hsv_img = images[HSV]
            h, s, v = hsv_img[y, x]
            h, s, v = int(h), int(s), int(v)
            
            print(f"Clicked pixel HSV: ({h}, {s}, {v})")

            if mask_selection.get() == 'red':
                lower = np.array([max(0, h - 10), max(0, s - 40), max(0, v - 40)])
                upper = np.array([min(255, h + 10), min(255, s + 40), min(255, v + 40)])
                print(f"Setting Red mask range to: lower={lower}, upper={upper}")
                red_lower_h_slider.set(lower[0])
                red_lower_s_slider.set(lower[1])
                red_lower_v_slider.set(lower[2])
                red_upper_h_slider.set(upper[0])
                red_upper_s_slider.set(upper[1])
                red_upper_v_slider.set(upper[2])
            else:
                lower = np.array([max(0, h - 10), max(0, s - 40), max(0, v - 40)])
                upper = np.array([min(255, h + 10), min(255, s + 40), min(255, v + 40)])
                print(f"Setting Non-Tissue mask range to: lower={lower}, upper={upper}")
                white_lower_h_slider.set(lower[0])
                white_lower_s_slider.set(lower[1])
                white_lower_v_slider.set(lower[2])
                white_upper_h_slider.set(upper[0])
                white_upper_s_slider.set(upper[1])
                white_upper_v_slider.set(upper[2])
            
            update_plot()

    fig.canvas.mpl_connect('button_press_event', on_click)

    def update_plot(value=None):
        nonlocal images
        HSV_RANGES['red'][0]['lower'] = np.array([
            int(red_lower_h_slider.get()),
            int(red_lower_s_slider.get()),
            int(red_lower_v_slider.get())
        ])
        HSV_RANGES['red'][0]['upper'] = np.array([
            int(red_upper_h_slider.get()),
            int(red_upper_s_slider.get()),
            int(red_upper_v_slider.get())
        ])
        HSV_RANGES['white'][0]['lower'] = np.array([
            int(white_lower_h_slider.get()),
            int(white_lower_s_slider.get()),
            int(white_lower_v_slider.get())
        ])
        HSV_RANGES['white'][0]['upper'] = np.array([
            int(white_upper_h_slider.get()),
            int(white_upper_s_slider.get()),
            int(white_upper_v_slider.get())
        ])
        images = count_pixels_and_plot(image_path, fig, HSV_RANGES, img)
        figure_canvas.draw()

    sliders_frame = ctk.CTkFrame(root, width=300)
    sliders_frame.pack(side="left", fill="y")

    # Mask selection
    mask_selection_frame = ctk.CTkFrame(sliders_frame)
    mask_selection_frame.pack(pady=10)
    ctk.CTkLabel(mask_selection_frame, text="Color Picker Target").pack()
    mask_selection = ctk.StringVar(value="red")
    ctk.CTkRadioButton(mask_selection_frame, text="Red Mask", variable=mask_selection, value="red").pack(anchor="w")
    ctk.CTkRadioButton(mask_selection_frame, text="Non-Tissue Mask", variable=mask_selection, value="white").pack(anchor="w")


    # Red mask sliders
    red_mask_frame = ctk.CTkFrame(sliders_frame)
    red_mask_frame.pack(pady=10)
    ctk.CTkLabel(red_mask_frame, text="Red Mask Settings").pack()

    # Lower bound sliders
    lower_bound_frame = ctk.CTkFrame(red_mask_frame)
    lower_bound_frame.pack(pady=5)
    ctk.CTkLabel(lower_bound_frame, text="Lower Bound").pack()

    for i, label in enumerate("HSV"):
        frame = ctk.CTkFrame(lower_bound_frame)
        frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(frame, text=label, width=10).pack(side='left')
        slider = ctk.CTkSlider(frame, from_=0, to=255, command=update_plot)
        slider.set(HSV_RANGES['red'][0]['lower'][i])
        slider.pack(fill='x', expand=True, side='left', padx=5)
        if i == 0: red_lower_h_slider = slider
        elif i == 1: red_lower_s_slider = slider
        else: red_lower_v_slider = slider

    # Upper bound sliders
    upper_bound_frame = ctk.CTkFrame(red_mask_frame)
    upper_bound_frame.pack(pady=5)
    ctk.CTkLabel(upper_bound_frame, text="Upper Bound").pack()

    for i, label in enumerate("HSV"):
        frame = ctk.CTkFrame(upper_bound_frame)
        frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(frame, text=label, width=10).pack(side='left')
        slider = ctk.CTkSlider(frame, from_=0, to=255, command=update_plot)
        slider.set(HSV_RANGES['red'][0]['upper'][i])
        slider.pack(fill='x', expand=True, side='left', padx=5)
        if i == 0: red_upper_h_slider = slider
        elif i == 1: red_upper_s_slider = slider
        else: red_upper_v_slider = slider

    # White mask sliders
    white_mask_frame = ctk.CTkFrame(sliders_frame)
    white_mask_frame.pack(pady=10)
    ctk.CTkLabel(white_mask_frame, text="Non-Tissue Mask Settings").pack()

    # Lower bound sliders
    white_lower_bound_frame = ctk.CTkFrame(white_mask_frame)
    white_lower_bound_frame.pack(pady=5)
    ctk.CTkLabel(white_lower_bound_frame, text="Lower Bound").pack()
    
    for i, label in enumerate("HSV"):
        frame = ctk.CTkFrame(white_lower_bound_frame)
        frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(frame, text=label, width=10).pack(side='left')
        slider = ctk.CTkSlider(frame, from_=0, to=255, command=update_plot)
        slider.set(HSV_RANGES['white'][0]['lower'][i])
        slider.pack(fill='x', expand=True, side='left', padx=5)
        if i == 0: white_lower_h_slider = slider
        elif i == 1: white_lower_s_slider = slider
        else: white_lower_v_slider = slider

    # Upper bound sliders
    white_upper_bound_frame = ctk.CTkFrame(white_mask_frame)
    white_upper_bound_frame.pack(pady=5)
    ctk.CTkLabel(white_upper_bound_frame, text="Upper Bound").pack()

    for i, label in enumerate("HSV"):
        frame = ctk.CTkFrame(white_upper_bound_frame)
        frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(frame, text=label, width=10).pack(side='left')
        slider = ctk.CTkSlider(frame, from_=0, to=255, command=update_plot)
        slider.set(HSV_RANGES['white'][0]['upper'][i])
        slider.pack(fill='x', expand=True, side='left', padx=5)
        if i == 0: white_upper_h_slider = slider
        elif i == 1: white_upper_s_slider = slider
        else: white_upper_v_slider = slider

    update_plot()
    root.mainloop()


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the image")
args = vars(ap.parse_args())

setup_window(args["image"])
