import tkinter as tk
import customtkinter
import shutil
import subprocess
import PIL
from PIL import Image, ImageOps, ImageTk, ImageFilter
from tkinter import filedialog
from tkinter import *
import simulation
from PIL import Image
import sys
from split_image import split_image
import cv2

global path_argv_sim
path_argv_sim = sys.argv[0]



scaling_factor = 0

def select_geojson_file():
    global file_path
    file_path = filedialog.askopenfilename(initialdir="/", title="Select Cells Geojson file",
                                           filetypes=(("geojson files", "*.geojson"), ("all files", "*.*")))

    print(file_path)

def select_riversgeojson_file():
    global rivers_file_path
    rivers_file_path = filedialog.askopenfilename(initialdir="/", title="Select Rivers Geojson file",
                                           filetypes=(("geojson files", "*.geojson"), ("all files", "*.*")))
    print(rivers_file_path)


def select_json_file():
    global json_file_path
    json_file_path = filedialog.askopenfilename(initialdir="/", title="Select JSON file",
                                                filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
    print(json_file_path)

def select_output_folder():
    global folder_path
    folder_path = filedialog.askdirectory(initialdir="/", title="Select output folder")
    print(folder_path)
    shutil.copy(file_path, folder_path + "/input.geojson")
    shutil.copy(json_file_path, folder_path + "/emoji.json")
    shutil.copy(rivers_file_path, folder_path + "/rivers.geojson")

    print("scaling_factor:", scaling_factor)

def run_generator():
    subprocess.run(["python", "colorrandom.py"], cwd=folder_path)
    subprocess.run(["python", "provinces.py", str(scaling_factor)], cwd=folder_path)
    subprocess.run(["python", "heightmap.py", str(scaling_factor)], cwd=folder_path)
    subprocess.run(["python", "biomes.py", str(scaling_factor)], cwd=folder_path)
    subprocess.run(["python", "jsonread.py"], cwd=folder_path)
    subprocess.run(["python", "xlsoutput.py"], cwd=folder_path)
    subprocess.run(["python", "jsontoxlsxprovinces.py"], cwd=folder_path)
    subprocess.run(["python", "namecorrector.py"], cwd=folder_path)
    subprocess.run(["python", "provdefcolumns.py"], cwd=folder_path)
    subprocess.run(["python", "religionfamilygen.py"], cwd=folder_path)
    subprocess.run(["python", "religionChildren.py"], cwd=folder_path)
    subprocess.run(["python", "relGenChil.py"], cwd=folder_path)
    subprocess.run(["python", "religionGen.py"], cwd=folder_path)
    subprocess.run(["python", "riverGen.py", str(scaling_factor)], cwd=folder_path)
    refresh_image()


def store_scaling_factor(value):
    global scaling_factor
    scaling_factor = int(value)

def select_scaling_factor():
    global scaling_factor
    scaling_factor = float(scaling_factor_entry.get())
    print("Scaling factor:", scaling_factor)


def store_tile_number(value):
    global scaling_factor
    scaling_factor = int(value)

def select_tile_number():
    global scaling_factor
    scaling_factor = float(tile_number_entry.get())
    print("Tile Number:", scaling_factor)

def add_image():
    global image_file_path
    image_file_path = "map_data/heightmap.png"
    image = Image.open(image_file_path)
    width, height = int(image.width / 4), int(image.height / 4)
    image = image.resize((width, height),Image.BILINEAR )
    canvas.config(width=image.width, height=image.height)
    image = ImageTk.PhotoImage(image)
    canvas.image = image
    canvas.create_image(0, 0, image=image, anchor="nw")

def refresh_image():
    global image_file_path

    # Re-open the image and resize it
    image = Image.open(image_file_path)
    width, height = int(image.width / 4), int(image.height / 4)
    image = image.resize((width, height))

    # Update the canvas size and image
    canvas.config(width=image.width, height=image.height)
    image = ImageTk.PhotoImage(image)
    canvas.image = image
    canvas.create_image(0, 0, image=image, anchor="nw")


def erodeSim():

    image = Image.open("map_data/heightmap.png")
    final_iter = int(e_iter.get())

    # Crop the center of the image
    width, height = image.size
    left = (width - 4096) / 2
    top = (height - 4096) / 2
    right = (width + 4096) / 2
    bottom = (height + 4096) / 2
    cropped_image = image.crop((left, top, right, bottom))
    print(cropped_image.mode)

    # Resize the image to 1024x1024
    resized_image = cropped_image.resize((1024, 1024),Image.NEAREST)

    # Save the resized image to the output path
    resized_image.save("map_data/heightmapCrop.png", mode="L", bits=8)

    # Load the 16-bit depth grayscale image
    img_16bit = cv2.imread('map_data/heightmapCrop.png', cv2.IMREAD_GRAYSCALE)

    # Normalize the image to the 0-255 range
    cv2.normalize(img_16bit, img_16bit, 0, 255, cv2.NORM_MINMAX)

    # Convert the 16-bit depth grayscale image to an 8-bit depth grayscale image
    img_8bit = cv2.convertScaleAbs(img_16bit)

    # Save the 8-bit depth grayscale image
    cv2.imwrite('map_data/heightmap8.png', img_8bit)



    global path_argv_sim
    path_argv_sim = sys.argv[0]
    print("WIP")
    print(final_iter)
    simulation.simulate("map_data/heightmap8.png", final_iter, "map_data", path_argv_sim)


customtkinter.set_appearance_mode("dark")
root = customtkinter.CTk()
root.title("Azgaar to CK3")
root.geometry("1200x700")

frame = customtkinter.CTkFrame(master=root, width = 200, height =600)
frame.pack(side="left", fill="y")

canvas = tk.Canvas(root, width=1366, height=1024)
canvas.pack(pady=15)

    # Create label for scaling factor
scaling_factor_label = customtkinter.CTkLabel(frame, text="Enter scaling factor:")
scaling_factor_label.pack()

# Create entry for scaling factor
scaling_factor_entry = customtkinter.CTkEntry(frame)
scaling_factor_entry.pack()

# Create button to select scaling factor
scaling_factor_button = customtkinter.CTkButton(frame,text="Enter scaling factor", command=select_scaling_factor)
scaling_factor_button.pack(padx=20, pady=10)

select_geojson_file_button = customtkinter.CTkButton(frame, text="Select Cells geojson file", command=select_geojson_file)
select_geojson_file_button.pack(padx=20, pady=10)


select_riversgeojson_file_button = customtkinter.CTkButton(frame,text="Select Rivers geojson file", command=select_riversgeojson_file)
select_riversgeojson_file_button.pack(padx=20, pady=10)


select_json_file_button = customtkinter.CTkButton(frame,text="Select JSON file", command=select_json_file)
select_json_file_button.pack(padx=20, pady=10)

select_output_folder_button = customtkinter.CTkButton(frame,text="Select output folder", command=select_output_folder)
select_output_folder_button.pack(padx=20, pady=10)

generate_button = customtkinter.CTkButton(frame,text="Generate maps", command=run_generator)
generate_button.pack(padx=20, pady=10)

label = customtkinter.CTkLabel(frame, text="Output folder must be same folder as the .exe and .py files")
label.pack(padx=20, pady=10)



image_button = customtkinter.CTkButton(frame,text="View Heightmap Image", command=add_image)
image_button.pack(padx=20, pady=10)


label = customtkinter.CTkLabel(frame, text="Heightmap Erosion Tool")
label.pack(padx=20, pady=10)

scaling_factor_label = customtkinter.CTkLabel(frame, text="Tile Number:")
scaling_factor_label.pack()


global tNum
tNum = customtkinter.CTkEntry(frame)
tNum.insert(0,"4")
tNum.pack()
tNumber = int(tNum.get())


scaling_factor_label = customtkinter.CTkLabel(frame, text="Enter Iterations:")
scaling_factor_label.pack()

global e_iter
e_iter = customtkinter.CTkEntry(frame)
e_iter.insert(0,"128")
e_iter.pack()





generate_button = customtkinter.CTkButton(frame,text="Run Erosion", command=erodeSim)
generate_button.pack(padx=20, pady=10)


label = customtkinter.CTkLabel(frame, text="The Erosion process is slow and runs at the speed of ((NxN)^3)*T")
label.pack()
label = customtkinter.CTkLabel(frame, text="where N is resolution and T is Number of Tiles")
label.pack()


root.mainloop()

if __name__ == '__main__':
    main(sys.argv)

