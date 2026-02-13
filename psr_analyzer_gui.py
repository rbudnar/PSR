from analyzer import RED_MASK, RED_MASK_COUNT, WHITE_MASK, WHITE_MASK_COUNT, ORIGINAL, HSV, get_pixel_count, generate_plot
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from analyzer import run as run_analyzer
import customtkinter as ctk
import matplotlib
import json
from tkinter import filedialog, messagebox
import threading
import queue
import os
from multiprocessing import Manager
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


def setup_window(image_path=None):
    HSV_RANGES = {
        'red': [],
        'white': []
    }
    
    images = {}
    last_clicked_rgb = None
    last_clicked_hsv = None
    img = None
    current_image_path = None

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Pixel Counter")
    root.geometry("1200x800")

    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    fig = plt.figure(figsize=(7, 7), dpi=100)

    canvas_frame = ctk.CTkFrame(root)
    canvas_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)

    figure_canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    figure_canvas.draw()
    figure_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def initialize_with_image(path):
        nonlocal img, images, current_image_path
        current_image_path = path
        img = cv2.imread(path)
        update_plot()

    def load_image():
        image_path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Image files", "*.jpg *.jpeg *.png *.tif *.tiff")])
        if image_path:
            initialize_with_image(image_path)

    # Load image button
    load_image_frame = ctk.CTkFrame(canvas_frame)
    load_image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    load_image_button = ctk.CTkButton(load_image_frame, text="Load Image", command=load_image)
    load_image_button.grid(row=0, column=0, sticky="ew")

    # Navigation toolbar for zooming
    toolbar = NavigationToolbar2Tk(figure_canvas, canvas_frame, pack_toolbar=False)
    toolbar.update()
    toolbar.grid(row=2, column=0, sticky="ew")

    sliders_frame = ctk.CTkFrame(root, width=300)
    sliders_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


    def on_click(event):
        nonlocal last_clicked_rgb, last_clicked_hsv
        if event.inaxes and event.inaxes.get_title() in ["Original image", "HSV image"]:
            x, y = int(event.xdata), int(event.ydata)
            
            # Store RGB for the swatch
            rgb_img = images[ORIGINAL]
            r, g, b = rgb_img[y, x]
            last_clicked_rgb = (r,g,b)
            
            # Store HSV for range calculation
            hsv_img = images[HSV]
            h, s, v = hsv_img[y, x]
            last_clicked_hsv = (int(h), int(s), int(v))

            # Update the color swatch
            color_swatch.configure(fg_color=f'#{r:02x}{g:02x}{b:02x}')
            
            print(f"Clicked pixel HSV: {last_clicked_hsv}")

    fig.canvas.mpl_connect('button_press_event', on_click)

    def update_plot():
        nonlocal images
        if img is None:
            fig.clear()
            figure_canvas.draw()
            return
        images = count_pixels_and_plot(current_image_path, fig, HSV_RANGES, img)
        figure_canvas.draw()

    def add_color_to_mask():
        if last_clicked_hsv is None:
            return

        mask_type = mask_selection.get()
        
        if mask_type == 'red':
            h_tolerance = int(red_h_tolerance_slider.get())
            s_tolerance = int(red_s_tolerance_slider.get())
            v_tolerance = int(red_v_tolerance_slider.get())
        else:
            h_tolerance = int(white_h_tolerance_slider.get())
            s_tolerance = int(white_s_tolerance_slider.get())
            v_tolerance = int(white_v_tolerance_slider.get())
            
        h, s, v = last_clicked_hsv
        
        lower = np.array([max(0, h - h_tolerance), max(0, s - s_tolerance), max(0, v - v_tolerance)])
        upper = np.array([min(255, h + h_tolerance), min(255, s + s_tolerance), min(255, v + v_tolerance)])
        
        color_range = {'lower': lower, 'upper': upper, 'rgb': last_clicked_rgb}
        HSV_RANGES[mask_type].append(color_range)
        
        update_color_list_ui()
        update_plot()

    def remove_color_from_mask(mask_type, color_range, frame):
        for i, cr in enumerate(HSV_RANGES[mask_type]):
            if np.array_equal(cr['lower'], color_range['lower']) and np.array_equal(cr['upper'], color_range['upper']):
                HSV_RANGES[mask_type].pop(i)
                break
        frame.destroy()
        update_plot()

    def update_color_list_ui():
        for widget in red_colors_frame.winfo_children():
            if widget not in [red_colors_label]:
                widget.destroy()
        for widget in white_colors_frame.winfo_children():
            if widget not in [white_colors_label]:
                widget.destroy()

        for color_range in HSV_RANGES['red']:
            add_color_frame(red_colors_frame, color_range, 'red')
        for color_range in HSV_RANGES['white']:
            add_color_frame(white_colors_frame, color_range, 'white')

    def add_color_frame(parent_frame, color_range, mask_type):
        frame = ctk.CTkFrame(parent_frame)
        frame.pack(fill='x', padx=5, pady=2)
        
        r, g, b = color_range['rgb']
        ctk.CTkFrame(frame, width=20, height=20, fg_color=f'#{r:02x}{g:02x}{b:02x}', border_width=1).pack(side='left', padx=5)
        
        remove_button = ctk.CTkButton(frame, text="Remove", width=50, command=lambda: remove_color_from_mask(mask_type, color_range, frame))
        remove_button.pack(side='right', padx=5)

    # Color selection
    selection_frame = ctk.CTkFrame(sliders_frame)
    selection_frame.pack(pady=10, padx=10, fill='x')
    ctk.CTkLabel(selection_frame, text="Selected Color:").pack(side='left')
    color_swatch = ctk.CTkFrame(selection_frame, width=50, height=20, fg_color='black', border_width=1)
    color_swatch.pack(side='left', padx=5)
    
    add_color_button = ctk.CTkButton(selection_frame, text="Add Color", command=add_color_to_mask)
    add_color_button.pack(side='right')

    # Mask selection
    mask_selection_frame = ctk.CTkFrame(sliders_frame)
    mask_selection_frame.pack(pady=10)
    ctk.CTkLabel(mask_selection_frame, text="Add to Mask:").pack()
    mask_selection = ctk.StringVar(value="red")
    ctk.CTkRadioButton(mask_selection_frame, text="Red Mask", variable=mask_selection, value="red").pack(anchor="w")
    ctk.CTkRadioButton(mask_selection_frame, text="Non-Tissue Mask", variable=mask_selection, value="white").pack(anchor="w")

    # Tolerance sliders
    red_tolerance_frame = ctk.CTkFrame(sliders_frame)
    red_tolerance_frame.pack(pady=10, padx=10)
    ctk.CTkLabel(red_tolerance_frame, text="Red Mask Tolerances").pack()
    
    red_h_frame = ctk.CTkFrame(red_tolerance_frame)
    red_h_frame.pack(fill='x', padx=5, pady=2)
    ctk.CTkLabel(red_h_frame, text="H", width=10).pack(side='left')
    red_h_tolerance_slider = ctk.CTkSlider(red_h_frame, from_=0, to=100)
    red_h_tolerance_slider.set(10)
    red_h_tolerance_slider.pack(fill='x', expand=True, side='left', padx=5)

    red_s_frame = ctk.CTkFrame(red_tolerance_frame)
    red_s_frame.pack(fill='x', padx=5, pady=2)
    ctk.CTkLabel(red_s_frame, text="S", width=10).pack(side='left')
    red_s_tolerance_slider = ctk.CTkSlider(red_s_frame, from_=0, to=100)
    red_s_tolerance_slider.set(40)
    red_s_tolerance_slider.pack(fill='x', expand=True, side='left', padx=5)

    red_v_frame = ctk.CTkFrame(red_tolerance_frame)
    red_v_frame.pack(fill='x', padx=5, pady=2)
    ctk.CTkLabel(red_v_frame, text="V", width=10).pack(side='left')
    red_v_tolerance_slider = ctk.CTkSlider(red_v_frame, from_=0, to=100)
    red_v_tolerance_slider.set(40)
    red_v_tolerance_slider.pack(fill='x', expand=True, side='left', padx=5)

    white_tolerance_frame = ctk.CTkFrame(sliders_frame)
    white_tolerance_frame.pack(pady=10, padx=10)
    ctk.CTkLabel(white_tolerance_frame, text="Non-Tissue Mask Tolerances").pack()

    white_h_frame = ctk.CTkFrame(white_tolerance_frame)
    white_h_frame.pack(fill='x', padx=5, pady=2)
    ctk.CTkLabel(white_h_frame, text="H", width=10).pack(side='left')
    white_h_tolerance_slider = ctk.CTkSlider(white_h_frame, from_=0, to=100)
    white_h_tolerance_slider.set(10)
    white_h_tolerance_slider.pack(fill='x', expand=True, side='left', padx=5)

    white_s_frame = ctk.CTkFrame(white_tolerance_frame)
    white_s_frame.pack(fill='x', padx=5, pady=2)
    ctk.CTkLabel(white_s_frame, text="S", width=10).pack(side='left')
    white_s_tolerance_slider = ctk.CTkSlider(white_s_frame, from_=0, to=100)
    white_s_tolerance_slider.set(40)
    white_s_tolerance_slider.pack(fill='x', expand=True, side='left', padx=5)

    white_v_frame = ctk.CTkFrame(white_tolerance_frame)
    white_v_frame.pack(fill='x', padx=5, pady=2)
    ctk.CTkLabel(white_v_frame, text="V", width=10).pack(side='left')
    white_v_tolerance_slider = ctk.CTkSlider(white_v_frame, from_=0, to=100)
    white_v_tolerance_slider.set(40)
    white_v_tolerance_slider.pack(fill='x', expand=True, side='left', padx=5)

    # Color list frames
    red_colors_frame = ctk.CTkFrame(sliders_frame)
    red_colors_frame.pack(pady=10, padx=10, fill='x')
    red_colors_label = ctk.CTkLabel(red_colors_frame, text="Red Mask Colors")
    red_colors_label.pack()

    white_colors_frame = ctk.CTkFrame(sliders_frame)
    white_colors_frame.pack(pady=10, padx=10, fill='x')
    white_colors_label = ctk.CTkLabel(white_colors_frame, text="Non-Tissue Mask Colors")
    white_colors_label.pack()

    def save_settings():
        settings_file = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not settings_file:
            return

        settings = {
            'red_tolerances': {
                'h': red_h_tolerance_slider.get(),
                's': red_s_tolerance_slider.get(),
                'v': red_v_tolerance_slider.get()
            },
            'white_tolerances': {
                'h': white_h_tolerance_slider.get(),
                's': white_s_tolerance_slider.get(),
                'v': white_v_tolerance_slider.get()
            },
            'hsv_ranges': {
                'red': [{'lower': r['lower'].tolist(), 'upper': r['upper'].tolist(), 'rgb': [int(c) for c in r['rgb']]} for r in HSV_RANGES['red']],
                'white': [{'lower': w['lower'].tolist(), 'upper': w['upper'].tolist(), 'rgb': [int(c) for c in w['rgb']]} for w in HSV_RANGES['white']]
            }
        }

        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"Settings saved to {settings_file}")

    def load_settings():
        settings_file = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("JSON files", "*.json")])
        if not settings_file:
            return

        with open(settings_file, 'r') as f:
            settings = json.load(f)

        red_h_tolerance_slider.set(settings['red_tolerances']['h'])
        red_s_tolerance_slider.set(settings['red_tolerances']['s'])
        red_v_tolerance_slider.set(settings['red_tolerances']['v'])
        white_h_tolerance_slider.set(settings['white_tolerances']['h'])
        white_s_tolerance_slider.set(settings['white_tolerances']['s'])
        white_v_tolerance_slider.set(settings['white_tolerances']['v'])

        HSV_RANGES['red'] = [{'lower': np.array(r['lower']), 'upper': np.array(r['upper']), 'rgb': tuple(r['rgb'])} for r in settings['hsv_ranges']['red']]
        HSV_RANGES['white'] = [{'lower': np.array(w['lower']), 'upper': np.array(w['upper']), 'rgb': tuple(w['rgb'])} for w in settings['hsv_ranges']['white']]

        update_color_list_ui()
        update_plot()
        print(f"Settings loaded from {settings_file}")

    # Save/Load buttons
    save_load_frame = ctk.CTkFrame(sliders_frame)
    save_load_frame.pack(pady=10, padx=10, fill='x')
    save_button = ctk.CTkButton(save_load_frame, text="Save Settings", command=save_settings)
    save_button.pack(side='left', padx=5)
    load_button = ctk.CTkButton(save_load_frame, text="Load Settings", command=load_settings)
    load_button.pack(side='right', padx=5)

    def batch_process():
        input_dir = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Input Folder with Images")
        if not input_dir:
            return
        output_dir = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Destination Folder for Results")
        if not output_dir:
            return

        settings = {
            'red_tolerances': {
                'h': red_h_tolerance_slider.get(),
                's': red_s_tolerance_slider.get(),
                'v': red_v_tolerance_slider.get()
            },
            'white_tolerances': {
                'h': white_h_tolerance_slider.get(),
                's': white_s_tolerance_slider.get(),
                'v': white_v_tolerance_slider.get()
            },
            'hsv_ranges': {
                'red': [{'lower': r['lower'].tolist(), 'upper': r['upper'].tolist(), 'rgb': [int(c) for c in r['rgb']]} for r in HSV_RANGES['red']],
                'white': [{'lower': w['lower'].tolist(), 'upper': w['upper'].tolist(), 'rgb': [int(c) for c in w['rgb']]} for w in HSV_RANGES['white']]
            }
        }
        with open(f"{output_dir}/image_settings.json", 'w') as f:
            json.dump(settings, f, indent=4)

        image_files = [f for f in os.listdir(input_dir) if f.endswith('.jpg')]
        file_count = len(image_files)
        
        if file_count == 0:
            messagebox.showwarning("Batch Processing", "No .jpg files found in the input folder.")
            return

        manager = Manager()
        progress_queue = manager.Queue()

        thread = threading.Thread(target=run_analyzer, args=(input_dir, ".jpg", True, output_dir, HSV_RANGES, progress_queue))
        thread.daemon = True
        thread.start()

        def check_queue():
            progress = progress_queue.qsize() / file_count
            progress_bar.set(progress)
            progress_label.configure(text=f"{int(progress * 100)}%")
            if progress < 1:
                root.after(100, check_queue)
            else:
                progress_bar.set(0) # Reset after completion
                progress_label.configure(text="0%")
                messagebox.showinfo("Batch Processing", "Batch processing complete!")
        
        check_queue()

    def on_closing():
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Batch process
    batch_frame = ctk.CTkFrame(sliders_frame)
    batch_frame.pack(pady=10, padx=10, fill='x')
    batch_button = ctk.CTkButton(batch_frame, text="Batch Process", command=batch_process)
    batch_button.pack(fill='x', pady=5)
    
    progress_frame = ctk.CTkFrame(batch_frame)
    progress_frame.pack(fill='x', pady=5)
    progress_bar = ctk.CTkProgressBar(progress_frame)
    progress_bar.set(0)
    progress_bar.pack(side='left', fill='x', expand=True)
    progress_label = ctk.CTkLabel(progress_frame, text="0%")
    progress_label.pack(side='right')

    if image_path:
        initialize_with_image(image_path)
    
    root.mainloop()


if __name__ == '__main__':
    setup_window()
