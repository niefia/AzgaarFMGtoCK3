import tkinter as tk
import customtkinter
import shutil
import subprocess
import sys
from tkinter import filedialog, Entry, Label
import PIL
from PIL import Image, ImageOps, ImageTk, ImageFilter

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

def add_image():
    global image_file_path
    image_file_path = filedialog.askopenfilename()
    image = Image.open(image_file_path)
    width, height = int(image.width / 8), int(image.height / 8)
    image = image.resize((width, height))
    canvas.config(width=image.width, height=image.height)
    image = ImageTk.PhotoImage(image)
    canvas.image = image
    canvas.create_image(0, 0, image=image, anchor="nw")

def refresh_image():
    global image_file_path

    # Re-open the image and resize it
    image = Image.open(image_file_path)
    width, height = int(image.width / 8), int(image.height / 8)
    image = image.resize((width, height))

    # Update the canvas size and image
    canvas.config(width=image.width, height=image.height)
    image = ImageTk.PhotoImage(image)
    canvas.image = image
    canvas.create_image(0, 0, image=image, anchor="nw")


customtkinter.set_appearance_mode("dark")
root = customtkinter.CTk()
root.title("Azgaar to CK3")
root.geometry("1200x512")
frame = customtkinter.CTkFrame(master=root, width = 200, height =600)
frame.pack(side="left", fill="y")

canvas = tk.Canvas(root, width=750, height=600)
canvas.pack()

image_button = tk.Button(frame, text="Add Image", command=add_image, bg="white")
image_button.pack(pady=15)

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


root.mainloop()