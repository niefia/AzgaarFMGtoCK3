import os
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog

output_dir = ""  # Variable to store the selected output folder path
heightmap_file = ""  # Variable to store the selected heightmap file path

mask_info = [
    {
        "title": "hills_01_rocks",
        "curve": 2.0,
        "lower_threshold": 0.32,
        "upper_threshold": 0.75
    },
    {
        "title": "mountain_02",
        "curve": 2.4,
        "lower_threshold": 0.7,
        "upper_threshold": 1.0
    },
    {
        "title": "mountain_02_c_snow",
        "curve": 3.0,
        "lower_threshold": 0.9,
        "upper_threshold": 1.0
    },
    {
        "title": "beach_02",
        "curve": 0.5,
        "lower_threshold": 0.0,
        "upper_threshold": 1.0,
        "lower_threshold2": 0.89,
        "upper_threshold2": 1.0
    },
    {
        "title": "coastline_cliff_grey",
        "curve": 0.5,
        "lower_threshold": 0.0,
        "upper_threshold": 0.1
    },
    {
        "title": "hills_01",
        "curve": 1.5,
        "lower_threshold": 0.2,
        "upper_threshold": 0.40
    },
    {
        "title": "Snow",
        "curve": 4.0,
        "lower_threshold": 0.99,
        "upper_threshold": 1.0
    }
]

# Function to handle the "Select Heightmap" button click event
def select_heightmap():
    global heightmap_file
    heightmap_file = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
    heightmap_label.configure(text=heightmap_file)

# Function to handle the "Select Output Folder" button click event
def select_output_folder():
    global output_dir
    output_dir = filedialog.askdirectory()
    output_folder_label.configure(text=output_dir)

# Create the Tkinter application window
window = tk.Tk()
window.title("Heightmap to Texture Tool")


# Create a button to select the heightmap file
select_button = ttk.Button(window, text="Select Heightmap", command=select_heightmap)
select_button.pack(pady=10)

# Create a label to display the selected heightmap file path
heightmap_label = tk.Label(window, text="")
heightmap_label.pack()

# Create a button to select the output folder
select_output_folder_button = ttk.Button(window, text="Select Output Folder", command=select_output_folder)
select_output_folder_button.pack(pady=10)

# Create a label to display the selected output folder path
output_folder_label = tk.Label(window, text="")

output_folder_label.pack()

# Create a preview window for the generated mask
preview_window = tk.Toplevel(window)
preview_window.title("Mask Preview")

# Create a label for the mask preview
preview_label = tk.Label(preview_window)
preview_label.pack()

# Define a global variable to store the reference to the image
preview_photo = None



def generate_mask(mask):
    title = mask["title"]
    curve_value = mask["curve"]
    lower_threshold = mask["lower_threshold"]
    upper_threshold = mask["upper_threshold"]

    # Load the image
    heightmap_file = os.path.join(output_dir, "map_data/heightmap.png")
    img = Image.open(heightmap_file)
    # Convert the image to a NumPy array
    arr = np.array(img)

    # Set the upper and lower thresholds based on the terrain type
    if "lower_threshold2" in mask and "upper_threshold2" in mask:
        lower_threshold2 = mask["lower_threshold2"]
        upper_threshold2 = mask["upper_threshold2"]
        # Invert the array for the beach mask
        # Array must be inverted to allow the sea to be textured, as generating using threshold where sea would have been included still left sea values as black, not white
        arr = 65535 - arr
        arr[arr < lower_threshold2 * 65535] = 0
        arr[arr > upper_threshold2 * 65535] = 0

    # Apply the lower and upper thresholds
    arr[arr < lower_threshold * 65535] = 0
    arr[arr > upper_threshold * 65535] = 0

    # Apply a curve filter with the current curve value
    arr = (arr / 65535) ** curve_value * 65535

    # Rescale the pixel values to the range of 0-255
    arr = (arr / 256).astype(np.uint8)

    # Convert the NumPy array back to an image
    img = Image.fromarray(arr)

    # Resize the image to be 8 times smaller
    resized_img = img.resize((img.width // 8, img.height // 8))

    # Update the preview image
    global preview_photo
    preview_photo = ImageTk.PhotoImage(resized_img)
    preview_label.configure(image=preview_photo)
    preview_label.image = preview_photo
    preview_window.update()

    # Save the image with the mask title
    output_folder = os.path.join(output_dir, "gfx/map/terrain")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img.save(os.path.join(output_folder, f"{title.lower().replace(' ', '_')}_mask.png"))


# Create sliders and generate buttons for curve values, upper thresholds, and lower thresholds for each mask
for mask in mask_info:
    title = mask["title"]

    frame = ttk.Frame(window)
    frame.pack(pady=10)

    label = tk.Label(frame, text=title)
    label.pack(side="left")

    curve_slider = tk.Scale(frame, from_=0.0, to=5.0, resolution=0.1, label="Curve Value",
                            orient=tk.HORIZONTAL)
    curve_slider.set(mask["curve"])
    curve_slider.pack(side="left", padx=10)

    lower_threshold_slider = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, label="Lower Threshold",
                                      orient=tk.HORIZONTAL)
    lower_threshold_slider.set(mask["lower_threshold"])
    lower_threshold_slider.pack(side="left", padx=10)

    upper_threshold_slider = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, label="Upper Threshold",
                                      orient=tk.HORIZONTAL)
    upper_threshold_slider.set(mask["upper_threshold"])
    upper_threshold_slider.pack(side="left", padx=10)

    generate_button = ttk.Button(frame, text="Generate", command=lambda mask=mask: generate_mask(mask))
    generate_button.pack(side="left", padx=10)

    if "lower_threshold2" in mask and "upper_threshold2" in mask:
        lower_threshold2_slider = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, label="Lower Threshold 2",
                                           orient=tk.HORIZONTAL)
        lower_threshold2_slider.set(mask["lower_threshold2"])
        lower_threshold2_slider.pack(side="left", padx=10)

        upper_threshold2_slider = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, label="Upper Threshold 2",
                                           orient=tk.HORIZONTAL)
        upper_threshold2_slider.set(mask["upper_threshold2"])
        upper_threshold2_slider.pack(side="left", padx=10)

# Start the Tkinter event loop
window.mainloop()
