import tkinter as tk
import shutil
import subprocess
from tkinter import filedialog, Entry, Label


scaling_factor = 0

def select_geojson_file():
    global file_path
    file_path = filedialog.askopenfilename(initialdir="/", title="Select Cells Geojson file",
                                           filetypes=(("geojson files", "*.geojson"), ("all files", "*.*")))
    selected_directory_textbox.delete(1.0, tk.END)
    selected_directory_textbox.insert(1.0, file_path)

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


def store_scaling_factor(value):
    global scaling_factor
    scaling_factor = int(value)

def select_scaling_factor():
    global scaling_factor
    scaling_factor = float(scaling_factor_entry.get())
    print("Scaling factor:", scaling_factor)

root = tk.Tk()
root.title("Azgaar to CK3")



scaling_factor_label = tk.Label(root, text="Enter scaling factor:")
scaling_factor_label.pack()

scaling_factor_entry = tk.Entry(root)
scaling_factor_entry.pack()

scaling_factor_button = tk.Button(text="Enter scaling factor", command=select_scaling_factor)
scaling_factor_button.pack()

select_geojson_file_button = tk.Button(text="Select Cells geojson file", command=select_geojson_file)
select_geojson_file_button.pack()



select_riversgeojson_file_button = tk.Button(text="Select Rivers geojson file", command=select_riversgeojson_file)
select_riversgeojson_file_button.pack()


select_json_file_button = tk.Button(text="Select JSON file", command=select_json_file)
select_json_file_button.pack()

select_output_folder_button = tk.Button(text="Select output folder and generate maps", command=select_output_folder)
select_output_folder_button.pack()

label = tk.Label(root, text="Output folder must be same folder as the .exe and .py files")
label.pack()

root.mainloop()