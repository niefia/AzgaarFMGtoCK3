import customtkinter
import tkinter as tk
from tkinter import filedialog
import tkinter
import generate
from tkinter import messagebox
import os
import time
import threading
import sys

class MyTabView(customtkinter.CTkTabview):


    def run_converter(self):
        self.progressbar.set(0.1)
        self.get_dirs_button.configure(state="disabled")

        # Call the generator function here
        modpath = self.path_text_boxes[0].get()
        mapfilldir = self.path_text_boxes[1].get()
        installdir = self.path_text_boxes[2].get()
        scaling_method_str = self.scaling_method_combobox.get()
        scaling_factor = self.scaling_factor_entry.get()
        modname = self.modname_entry.get()
        generate_characters = self.chargen_combobox.get()
        CharGen_response = generate_characters.lower()

        scaling_factor = int(scaling_factor)
        if scaling_method_str == "Manual Scaling":
            scaling_method = 1
        else:
            scaling_method = 2


        gamedir = os.path.join(installdir, 'game')
        output_dir = os.path.join(modpath, modname)
        try:

            generate.printValues(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)
            # Update the progress bar
            self.progressbar.set(0.12)
            generate.runGenExcel(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)

            self.progressbar.set(0.3)
            generate.runGenRaster(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)
            self.progressbar.set(0.35)
            time.sleep(1)
            generate.runGenRelCult(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)
            self.progressbar.set(0.4)
            time.sleep(1)
            generate.runGenBFS(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)
            self.progressbar.set(0.7)
            generate.runMapFill(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)
            self.progressbar.set(0.9)
            generate.runCharBook(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir)
            self.progressbar.set(1.0)
        except Exception as e:
            print(f"An error occurred, please report the log.txt file if this error is unexpected: {e}")
            self.get_dirs_button.configure(state="normal")
            messagebox.showinfo("Error", "An error occurred, Please check the log.txt file if this error is unexpected!")
            # Wait for user input before closing
            input("Press Enter to exit...")
            sys.exit(1)  # exit with an error code


        messagebox.showinfo("Conversion Complete", "The conversion process is complete!")
        self.get_dirs_button.configure(state="normal")


    def run_conv_thread(self):
        # Create a new thread to run the function
        thread = threading.Thread(target=self.run_converter)
        thread.start()


    def browse_directory(self, row):
        # Get the text box associated with the browse button
        text_box = self.path_text_boxes[row]

        # Open the directory selection dialog
        directory = filedialog.askdirectory()

        # If a directory was selected, update the text box
        if directory:
            text_box.delete(0, tk.END)
            text_box.insert(0, directory)



    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("Paths")
        self.add("Options")
        self.add("Convert")

        # add widgets on tabs
        self.label = customtkinter.CTkLabel(master=self.tab("Paths"), text="hello")
        self.label.grid(row=0, column=0, padx=20, pady=10,sticky=tkinter.E)

        ### DIRECTORIES ###

        self.path_labels = ["Crusader Kings III Mod Directory:", "Map Filler Directory:",
                            "Crusader Kings III Install Directory:"]
        self.path_text_boxes = []
        self.browse_buttons = []

        for row, label in enumerate(self.path_labels):
            # Create the label
            label_widget = customtkinter.CTkLabel(master=self.tab("Paths"), text=label)
            label_widget.grid(row=row, column=0, sticky="w", padx=5, pady=5)

            # Create the text box
            text_box_widget = customtkinter.CTkEntry(master=self.tab("Paths"), width=600)
            text_box_widget.grid(row=row, column=1, sticky="we", padx=5, pady=5)
            self.path_text_boxes.append(text_box_widget)

            # Create the browse button
            browse_button_widget = customtkinter.CTkButton(master=self.tab("Paths"), text="Browse",
                                                           command=lambda row=row: self.browse_directory(row))
            browse_button_widget.grid(row=row, column=2, sticky="e", padx=5, pady=5)
            self.browse_buttons.append(browse_button_widget)



        # Options tab


        self.scaling_method_label = customtkinter.CTkLabel(master=self.tab("Options"), text="Select scaling method:")
        self.scaling_method_label.grid(row=0, column=0, padx=20, pady=10)
        self.scaling_method_label.pack()



        self.scaling_method_options = ["Manual Scaling", "Auto-Scaling"]
        self.scaling_method_combobox = customtkinter.CTkComboBox(master=self.tab("Options"), values=self.scaling_method_options)
        self.scaling_method_combobox.pack()

        self.scaling_factor_label = customtkinter.CTkLabel(master=self.tab("Options"),text="Enter Scaling Factor (only used for Manual Scaling):")
        self.scaling_factor_label.pack()


        self.scaling_factor_entry = customtkinter.CTkEntry(master=self.tab("Options"))
        self.scaling_factor_entry.insert(0, "50")
        self.scaling_factor_entry.pack()

        self.modname_label = customtkinter.CTkLabel(master=self.tab("Options"), text="Mod Name:")
        self.modname_label.pack()

        self.modname_entry = customtkinter.CTkEntry(master=self.tab("Options"))
        self.modname_entry.insert(0, "Conversion")
        self.modname_entry.pack()

        self.chargen_label = customtkinter.CTkLabel(master=self.tab("Options"), text="Generate characters to hold the state level titles?")
        self.chargen_label.pack()

        self.chargen_var = tk.StringVar(value="No")
        self.chargen_options = ["Yes", "No"]
        self.chargen_combobox = customtkinter.CTkComboBox(master=self.tab("Options"), values=self.chargen_options)
        self.chargen_combobox.pack()


        #options c1
        #self.labelc1 = customtkinter.CTkLabel(master=self.tab("Options"), text="hello")
        #self.labelc1.grid(row=0, column=1, padx=20, pady=10)



        #CONVERT TAB

        # Create the set values button
        self.get_dirs_button = customtkinter.CTkButton(master=self.tab("Convert"), text="Run Converter", command=self.run_conv_thread)
        self.get_dirs_button.pack()

        self.progressbar = customtkinter.CTkProgressBar(master=self.tab("Convert"))
        self.progressbar.pack(padx=20, pady=10)
        self.progressbar.set(0.0)



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("dark")
        self.minsize(1100, 400)
        self.title("CK3 Map Generation Tool")
        self.tab_view = MyTabView(master=self,width = 1200, height = 400)

        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tab_view.grid_rowconfigure(3, weight=1)


#app = App()
#app.mainloop()