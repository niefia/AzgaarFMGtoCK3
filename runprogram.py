import tkinter as tk
import shutil
import subprocess
from tkinter import filedialog


def select_file_and_folder():
    global file_path
    global folder_path
    file_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                           filetypes=(("geojson files", "*.geojson"), ("all files", "*.*")))
    print(file_path)

    folder_path = filedialog.askdirectory(initialdir="/", title="Select output folder")
    print(folder_path)
    shutil.move(file_path, folder_path + "/input.geojson")

    subprocess.run(["python", "colorrandom.py"], cwd=folder_path)
    subprocess.run(["python", "provinces.py"], cwd=folder_path)
    subprocess.run(["python", "heightmap.py"], cwd=folder_path)
    subprocess.run(["python", "biomes.py"], cwd=folder_path)


root = tk.Tk()
root.title("Azgaar to CK3")

select_file_and_folder_button = tk.Button(text="Select file and folder and generate maps", command=select_file_and_folder)
select_file_and_folder_button.pack()

label = tk.Label(root, text="Output folder must be same folder as the .exe and .py files")
label.pack()

root.mainloop()

