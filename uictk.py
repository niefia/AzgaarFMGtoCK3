import customtkinter
import tkinter as tk
from tkinter import filedialog
import tkinter
from tkinter import messagebox
import os
import generate
import time
import threading
import sys
from PIL import Image

if not os.path.exists('language.txt'):
    with open('language.txt', 'w') as f:
        f.write('')


if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, use the bundle directory as the current directory
    current_dir = os.path.dirname(sys.executable)
else:
    # If the application is run as a script, use the directory containing the script as the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

# All CustomTkinter Code
class App(customtkinter.CTk):



    def __init__(self):
        super().__init__()
        self.title("AzgaarFMG-to-CK3 Map Converter")
        self.geometry(f"980x580")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        def test():
            print("test")

        ENGLISH = {
            "mod_dir": "Crusader Kings III Mod Directory:",
            "map_filler_dir": "Map Filler Directory:",
            "install_dir": "Crusader Kings III Install Directory:",
            "scaling_factor_label": "Enter Scaling Factor (only used for Manual Scaling):",
            "mod_name": "Mod Name",
            "charGen": "Generate characters to hold the state level titles?",
            "runConverter": "Run Converter",
            "scaling_method": "Select Scaling Method",
            "manualScaling": "Manual Scaling",
            "autoScaling": "Auto Scaling",
            "yes": "yes",
            "no": "no",
            "conversion": "Conversion",
            "home": "Home",
            "setup_frame_label" : "Pathing & Setup",
            "setup":"Setup",
            "Options":"Options",
            "Guide":"Guide",
            "FAQ":"FAQ",
            "PH_Installdir":"C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III",
            "PH_Modfolder": "C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod",
            "PH_MapFiller": "The Folder you've installed Map Filler Tool into",
            "Select Scaling Method": "Select Scaling Method",
            "Start Conversion": "Start Conversion",
            "Save Paths":"Save Paths",
            "Load Paths":"Load Paths",
            "Generate Characters":"Generate Characters",
            "DontGenerate":"Don't Generate Characters",
            "Restart to update":"Restart to update"
        }
        FRANÇAIS = {
            "mod_dir": "Crusader Kings III Répertoire des Mods:",
            "map_filler_dir": "Map Filler Répertoire:",
            "install_dir": "Répertoire d'installation de Crusader Kings III:",
            "scaling_factor_label": "Entrer le facteur d'échelle (utilisé uniquement pour la mise à l'échelle manuelle):",
            "mod_name": "Nom du Mod",
            "charGen": "Générer des personnages pour détenir les titres au niveau de l'État?",
            "runConverter": "Exécuter le convertisseur",
            "scaling_method": "Sélectionner la méthode de mise à l'échelle",
            "manualScaling": "Mise à l'échelle manuelle",
            "autoScaling": "Mise à l'échelle automatique",
            "yes": "oui",
            "no": "non",
            "conversion": "Conversion",
            "setup_frame_label" : "Tracé et mise en place",
            "setup":"Mise en place",
            "Options":"Options",
            "Guide":"Guide",
            "FAQ":"FAQ",
            "PH_Installdir":"Le répertoire d'installation de CK3 est trouvé par Steam>CK3>Propriétés>Fichiers Locaux>Parcourir",
            "PH_Modfolder": "C:/Utilisateurs/(Nom d'utilisateur)/Documents/Paradox Interactive/Crusader Kings III/mod",
            "PH_MapFiller": "Le dossier dans lequel vous avez installé Map Filler Tool",
            "Select Scaling Method": "Sélectionner la méthode de mise à l'échelle",
            "Start Conversion": "Démarrer la conversion",
            "Save Paths":"Sauvegarder les chemins",
            "Load Paths": "Chemins de charge",
            "Generate Characters":"Générer des personnages",
            "DontGenerate":"Ne pas générer de caractères",
            "Restart to update": "Redémarrer pour mettre à jour"

        }
        DEUTSCH = {
            "mod_dir": "Crusader Kings III Mod-Verzeichnis:",
            "map_filler_dir": "Map Filler-Verzeichnis:",
            "install_dir": "Crusader Kings III Installationsverzeichnis:",
            "scaling_factor_label": "Eingabe des Skalierungsfaktors (nur bei manueller Skalierung verwenden):",
            "mod_name": "Mod-Name",
            "charGen": "Möchten Sie Charaktere generieren, die Titel des jeweiligen Landes tragen?",
            "runConverter": "Converter ausführen",
            "scaling_method": "Skalierungsmethode auswählen",
            "manualScaling": "Manuelle Skalierung",
            "autoScaling": "Automatische Skalierung",
            "yes": "Ja",
            "no": "Nein",
            "conversion": "Konvertieren der Karte",
            "home": "Startseite",
            "setup_frame_label": "Dateiadressen und Einrichtung",
            "setup": "Einrichtung",
            "Options": "Optionen",
            "Guide": "Guide",
            "FAQ": "Häufig gestellte Fragen",
            "PH_Installdir": "Das CK3-Installationsverzeichnis finden Sie über Steam>CK3>Eigenschaften>Lokale Dateien>Durchsuchen",
            "PH_Modfolder": "C:/Benutzer/(Name)/Dokumente/Paradox Interactive/Crusader Kings III/mod",
            "PH_MapFiller": "Der Ordner, in dem Sie das Map-Filler Tool installiert haben",
            "Select Scaling Method": "Skalierungsmethode auswählen",
            "Start Conversion": "Konvertierung starten",
            "Save Paths": "Dateiadressen speichern",
            "Load Paths": "Pfade laden",
            "Generate Characters": "Charaktere generieren",
            "DontGenerate": "Keine Charaktere generieren",
            "Restart to update":"Neustart zur Aktualisierung",


        }
        HUNGARIAN = {
            "mod_dir": "Crusader Kings III Modok mappa:",
            "map_filler_dir": "Térképfeltöltő mappa:",
            "install_dir": "Crusader Kings III Telepítési mappa:",
            "scaling_factor_label": "Írja be a méretezési egységet (Csak Manuális Méretezéshez):",
            "mod_name": "Mod Neve",
            "charGen": "Legyenek Karakterek generálva az állami szintekre?",
            "runConverter": "Konverter futtatása",
            "scaling_method": "Méretezési folyamatot",
            "manualScaling": "Manuális Méretezés",
            "autoScaling": "Automatikus Méretezés",
            "yes": "Igen",
            "no": "Nem",
            "conversion": "Konvertálás",
            "home": "Kezdőképernyő",
            "setup_frame_label": "Útvonalak és Konfiguráció",
            "setup": "Konfiguráció",
            "Options": "Beállítások",
            "Guide": "Útmutató",
            "FAQ": "GYIK",
            "PH_Installdir": "Talált CK3 telepítési mappa: Steam>CK3>Properties>Local Files>Browse",
            "PH_Modfolder": "C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod",
            "PH_MapFiller": "Térképfeltöltő program mappája",
            "Select Scaling Method": "Válassza ki a méretezési folyamatot",
            "Start Conversion": "Konvertálás megkezdése",
            "Save Paths": "Útvonalak Mentése",
            "Load Paths": "Útvonalak Betöltése",
            "Generate Characters": "Generáljon Karaktereket",
            "DontGenerate": "Ne Generáljon Karaktereket",
            "Restart to update": "Frissítéshez indítsa újra a programot!"
        }
        POLISH = {
            "mod_dir": "Folder z modami gry Crusader Kings III:",
            "map_filler_dir": "Folder z wypełniaczem mapy (Map Filler Folder):",
            "install_dir": "Pliki lokalne gry Crusader Kings III:",
            "scaling_factor_label": "Wprowadź współczynik skalowania (Tylko dla skalowania manualnego):",
            "mod_name": "Nazwa Moda",
            "charGen": "Wygenerować postacie królewskie?",
            "runConverter": "Włącz konwerter",
            "scaling_method": "Wybierz metodę skalowania",
            "manualScaling": "Skalowanie manualne",
            "autoScaling": "Saklowanie automatyczne",
            "yes": "tak",
            "no": "nie",
            "conversion": "Konwersja",
            "home": "Strona główna",
            "setup_frame_label": "Ścieżki i Konfiguracja",
            "setup": "Konfiguracja",
            "Options": "Opcje",
            "Guide": "Poradnik",
            "FAQ": "FAQ",
            "PH_Installdir": "Ścieżkę instalacyjną Ck3 znajdziesz w: Steam>CK3>Properties>Local Files>Browse",
            "PH_Modfolder": "C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod",
            "PH_MapFiller": "Folderm, w którym zainstalowałeś wypełniacz mpay (Map Filler Tool)",
            "Select Scaling Method": "Wybierz metodę skalowania",
            "Start Conversion": "Rozpocznij konwersję",
            "Save Paths": "Zapisz ścieżki",
            "Load Paths": "Wczytaj ścieżki",
            "Generate Characters": "Generuj Postacie",
            "DontGenerate": "Nie genreuj postaci",
            "Restart to update": "Zrestartuj dla aktualizacji",

        }
        SPANISH = {
            "mod_dir": "Directorio del Mod de Crusader Kings III:",
            "map_filler_dir": "Directorio del relleno del mapa:",
            "install_dir": "Directorio de instalación de Crusader Kings III:",
            "scaling_factor_label": "Ingresar factor de escala (utilizado unicamente para el escalado manual):",
            "mod_name": "Nombre del Mod",
            "charGen": "Generar personajes que sostengan el nivel del titulo de estado?",
            "runConverter": "Ejecutar Conversor",
            "scaling_method": "Seleccionar el metodo de escalado",
            "manualScaling": "Escalado manual",
            "autoScaling": "Escalado automatico",
            "yes": "si",
            "no": "no",
            "conversion": "Conversion",
            "home": "Inicio",
            "setup_frame_label": "Caminos y configuración",
            "setup": "Configuración",
            "Options": "Opciones",
            "Guide": "Guia",
            "FAQ": "FAQ",
            "PH_Installdir": "El directorio de instalación de CK3 se encuentra en Steam>CK3>Propiedades>Archivos Locales>Navegar",
            "PH_Modfolder": "C:/Usarios/USUARIO/Documentos/Paradox Interactive/Crusader Kings III/mod",
            "PH_MapFiller": "La carpeta donde has instalado la herramienta de llenado de mapa (Map Filler Tool)",
            "Select Scaling Method": "Seleccionar metodo de escala",
            "Start Conversion": "Comenzar conversion",
            "Save Paths": "Guardar Caminos",
            "Load Paths": "Cargar Caminos",
            "Generate Characters": "Generar Personajes",
            "DontGenerate": "No Generar Personajes",
            "Restart to update": "Reiniciar para actualizar",

        }



        LANGUAGE = ENGLISH

        # Open the file and read the content
        with open('language.txt', 'r') as f:
            language = f.read().strip()

        # Check the value of the LANGUAGE variable
        if language == 'ENGLISH':
            print('Language set to ENGLISH from language.txt')
            LANGUAGE = ENGLISH
        elif language == 'FRANÇAIS':
            print('Language set to FRANÇAIS from language.txt')
            LANGUAGE = FRANÇAIS
        elif language == 'DEUTSCH':
            print("Language set to DEUTSCH from language.txt")
            LANGUAGE = DEUTSCH
        elif language == 'HUNGARIAN':
            print("Langauge set to HUNGARIAN")
            LANGUAGE = HUNGARIAN
        elif language == 'POLISH':
            print("Language set to POLISH")
            LANGUAGE = POLISH
        elif language == 'SPANISH':
            print("Language set to SPANISH")
            LANGUAGE = SPANISH
        else:
            print('No language found, setting to English as backup')
            LANGUAGE = ENGLISH


        def update_language(option):
            global LANGUAGE
            # Update the value of the LANGUAGE variable
            LANGUAGE = option
            print(f"Language updated to {LANGUAGE}")

            # Write the selected language to the language file
            if not os.path.exists('language.txt'):
                with open('language.txt', 'w') as f:
                    f.write('')
            with open('language.txt', 'w') as f:
                f.write(LANGUAGE)



        def run_converter():
            self.Conversion_button.grid_forget()
            self.loading_wheel.grid(row=4, column=0, padx=20, pady=20, sticky="n")
            self.Conversion_button.configure(state="disabled")
            self.Conversion_progress_bar.set(0.1)
            modpath = self.CK3_Mod_Path_Entry.get()
            mapfilldir = self.CK3_Map_Filler_Tool_Path_Entry.get()
            installdir = self.CK3_Game_Path_Entry.get()
            scaling_method_str = self.Options_Scaling_Menu.get()
            modname = self.Mod_Name_Entry.get()
            generate_characters = self.Generate_Characters_Menu.get()
            CharGen_response = generate_characters.lower()
            try:
                blur_amount = int(self.blur_heightmap_entry.get())
            except ValueError:
                messagebox.showinfo("Error",
                                    "Invalid value for Blur Radius, setting to 100k default of 7")
                blur_amount = 7

            if scaling_method_str == "Manual Scaling":
                scaling_method = 1
                scaling_factor = self.Manual_Scaling_Entry.get()
                scaling_factor = int(scaling_factor)

            else:
                scaling_method = 2
                scaling_factor = 50
                scaling_factor = int(scaling_factor)

            if generate_characters == "Generate Characters":
                CharGen_response = "yes"
            else:
                CharGen_response = "no"

            gamedir = os.path.join(installdir, 'game')
            output_dir = os.path.join(modpath, modname)
            try:
                generate.printValues(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                     CharGen_response, gamedir, output_dir)
                # Update the progress bar
                self.Conversion_progress_bar.set(0.12)
                self.status_label.configure(text="Extracting JSON & Geojson to spreadsheet")

                generate.runGenExcel(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                     CharGen_response, gamedir, output_dir)
                self.status_label.configure(text="Spreadsheets Complete")
                self.status_label.configure(text="Producing Map Rasters")
                self.Conversion_progress_bar.set(0.3)
                generate.runGenRaster(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                      CharGen_response, gamedir, output_dir,blur_amount)
                self.Conversion_progress_bar.set(0.35)
                self.status_label.configure(text="Generating Rivers")
                generate.GenerateRivers(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                               CharGen_response, gamedir, output_dir)
                self.Conversion_progress_bar.set(0.37)
                self.status_label.configure(text="Generating Religions Data")
                generate.runGenRelCult(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                       CharGen_response, gamedir, output_dir)
                self.Conversion_progress_bar.set(0.4)
                self.status_label.configure(text="Running BFS for Barony Generation from Cells")
                generate.runGenBFS(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                   CharGen_response, gamedir, output_dir)
                self.Conversion_progress_bar.set(0.7)
                self.status_label.configure(text="Running Map Filler tool")
                generate.runMapFill(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                    CharGen_response, gamedir, output_dir)
                self.Conversion_progress_bar.set(0.9)
                self.status_label.configure(text="Generating Paper Map")
                generate.runGenPaper(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                    CharGen_response, gamedir, output_dir)
                self.Conversion_progress_bar.set(0.95)
                generate.Terrains(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                    CharGen_response, gamedir, output_dir)

                #self.status_label.configure(text="Generating Rivers")
                #generate.GenerateRivers(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,CharGen_response, gamedir, output_dir)
                self.Conversion_progress_bar.set(0.97)
                self.status_label.configure(text="Generating Character + Bookmark if selected")
                generate.runCharBook(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname,
                                     CharGen_response, gamedir, output_dir)
                self.status_label.configure(text="Done")
                self.Conversion_progress_bar.set(1.0)
            except Exception as e:
                print(f"An error occurred, please report the log.txt file if this error is unexpected: {e}")
                label_text = self.status_label.cget("text")
                self.status_label.configure(
                    text="Failed when " + label_text + f"\n{e}\nPlease report the log.txt file if this error is unexpected!")
                self.get_dirs_button.configure(state="normal")
                messagebox.showinfo("Error",
                                    "An error occurred, Please check the log.txt file if this error is unexpected!")
                # Wait for user input before closing
                input("Press Enter to exit...")
                sys.exit(1)  # exit with an error code

            messagebox.showinfo("Conversion Complete", "The conversion process is complete!")
            self.Conversion_button.configure(state="normal")
            self.loading_wheel.grid_forget()
            self.Conversion_button.grid(row=4, column=0, padx=20, pady=20, sticky="n")


            print(installdir,modpath,mapfilldir,scaling_factor,scaling_method_str,modname,generate_characters,CharGen_response,scaling_method_str)  # or return game_path

        def run_conv_thread():
            # Create a new thread to run the function
            thread = threading.Thread(target=run_converter)
            thread.start()


        def openModFolder():
            modpath = self.CK3_Mod_Path_Entry.get()
            modname = self.Mod_Name_Entry.get()
            output_dir = os.path.join(modpath, modname)
            os.startfile(output_dir)

        def browse_directory(entry_widget):

            # Open the directory browser
            directory = filedialog.askdirectory()
            # If the user selected a directory, set the entry widget to the directory.
            # Since we have entry widgets for multiple paths, every time you open the directory browser, it will set the entry widget to the directory you selected.

            if directory:
                entry_widget.delete(0, "end")
                entry_widget.insert(0, directory)

        # Opens the Guide in a default browser
        def open_guide():
            url = "https://github.com/niefia/AzgaarFMGtoCK3/wiki/Azgaar-to-CK3-Converter-Guide"
            # Open URL in default browser
            os.system(f"start {url}")

        def open_FAQ():
            url = "https://github.com/niefia/AzgaarFMGtoCK3/wiki/FAQ"

            # Open URL in default browser
            os.system(f"start {url}")

        def open_convrules():
            url = "https://github.com/niefia/AzgaarFMGtoCK3/wiki/Conversion-rules-reference"

            # Open URL in default browser
            os.system(f"start {url}")

        # Creates a Entry for Manual Scaling Factor if you choose Manual Scaling and destoryes it if you choose Automatic Scaling.
        def optionmenu_callback(choice):

            if choice == "Manual Scaling":

                self.Manual_Scaling_Label = customtkinter.CTkLabel(self.third_frame,
                                                                   text="Enter Manual Scaling Factor:",
                                                                   font=customtkinter.CTkFont(size=20, weight="bold"))
                self.Manual_Scaling_Label.grid(row=3, column=0, padx=20, pady=20, sticky="n")
                self.Manual_Scaling_Entry = customtkinter.CTkEntry(self.third_frame, fg_color="transparent", )
                self.Manual_Scaling_Entry.grid(row=4, column=0, padx=20, pady=20, sticky="n")
            elif choice == "Automatic Scaling":
                #removed from grid insetad of deleted to prevent issues
                self.Manual_Scaling_Label.grid_remove()
                self.Manual_Scaling_Entry.grid_remove()



           # Saves the paths to a file

        def save_paths():
            Entry1_value = self.CK3_Game_Path_Entry.get()
            Entry2_value = self.CK3_Mod_Path_Entry.get()
            Entry3_value = self.CK3_Map_Filler_Tool_Path_Entry.get()

            # Get the filename to save the data
            filename = filedialog.asksaveasfilename(initialdir=current_dir, defaultextension='.txt', initialfile='paths.txt')
            if filename:
                # Save the values to the file
                with open(filename, 'w') as f:
                    f.write(f'{Entry1_value}, {Entry2_value}, {Entry3_value}')



        # Loads the paths from a file
        def load_paths():
            # Get the filename to load the data
            filename = filedialog.askopenfilename(initialdir=current_dir, initialfile='paths.txt')

            if filename:
                # Read the saved values from the file
                with open(filename, 'r') as f:
                    data = f.read().split(', ')
                    Entry1_value, Entry2_value, Entry3_value = data

                # Display the loaded values in the entry widgets
                self.CK3_Game_Path_Entry.delete(0, tk.END)
                self.CK3_Mod_Path_Entry.delete(0, tk.END)
                self.CK3_Map_Filler_Tool_Path_Entry.delete(0, tk.END)

                self.CK3_Game_Path_Entry.insert(0, Entry1_value)
                self.CK3_Mod_Path_Entry.insert(0, Entry2_value)
                self.CK3_Map_Filler_Tool_Path_Entry.insert(0, Entry3_value)


        # Light and Dark mode Color Templates

        text_color_template = ("gray10", "gray90")
        hover_color_template = ("gray70", "gray30")

        # Load Images
        # Images are loaded from the Image_Assets folder
        image_path = "Image_Assets/"
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_light.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 size=(20, 20))
        self.setup_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "paths_light.png")),
                                                  dark_image=Image.open(os.path.join(image_path, "paths_dark.png")),
                                                  size=(20, 20))
        self.options_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "options-light.png")),
            dark_image=Image.open(os.path.join(image_path, "options-dark.png")), size=(20, 20))

        self.browse_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "browse_light.png")),
                                                   dark_image=Image.open(os.path.join(image_path, "browse_dark.png")),
                                                   size=(30, 30))
        self.General_Setup_Download_Image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "download_light.png")),
            dark_image=Image.open(os.path.join(image_path, "download_dark.png")), size=(50, 50))

        self.Start_Button_Image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "start_light.png")),
            dark_image=Image.open(os.path.join(image_path, "start_dark.png")), size=(50, 50))

        self.next_button_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "next_light.png")),
            dark_image=Image.open(os.path.join(image_path, "next_dark.png")), size=(30, 30))

        self.guide_button_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "guide_light.png")),
            dark_image=Image.open(os.path.join(image_path, "guide_dark.png")), size=(30, 30))

        self.FAQ_Image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "FAQ_light.png")),
            dark_image=Image.open(os.path.join(image_path, "FAQ_dark.png")), size=(30, 30))

        self.Save_Paths_Image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "save_light.png")),
            dark_image=Image.open(os.path.join(image_path, "save_dark.png")), size=(30, 30))

        # Navigation Frame and its Widgets
        # Contains All the Buttons for the different Frames but not the commands for the buttons
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="CK3 Map Converter",
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=text_color_template,
                                                   hover_color=hover_color_template,
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.setup_frame_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                          border_spacing=10, text="Setup",
                                                          fg_color="transparent", text_color=text_color_template,
                                                          hover_color=hover_color_template,
                                                          image=self.setup_image, anchor="w",
                                                          command=self.setup_frame_button_event)
        self.setup_frame_button.grid(row=2, column=0, sticky="ew")

        self.settings_frame_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                             border_spacing=10, text=LANGUAGE["Options"],
                                                             fg_color="transparent", text_color=text_color_template,
                                                             hover_color=hover_color_template,
                                                             image=self.options_image, anchor="w",
                                                             command=self.settings_frame_button_event)
        self.settings_frame_button.grid(row=3, column=0, sticky="ew")

        self.conversion_frame_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                               border_spacing=10, text="Conversion",
                                                               fg_color="transparent", text_color=text_color_template,
                                                               hover_color=hover_color_template,
                                                               image=self.options_image, anchor="w",
                                                               command=self.conversion_frame_button_event)
        self.conversion_frame_button.grid(row=4, column=0, sticky="ew")

        self.language_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                         values=["ENGLISH", "FRANÇAIS","DEUTSCH","HUNGARIAN",'POLISH','SPANISH'],
                                                         command=update_language,
                                                         fg_color="#191919", button_color="#191919")

        self.language_menu.grid(row=6, column=0, padx=20, pady=8, sticky="s")

        self.language_menu.set(language)

        self.language_updatelabel = customtkinter.CTkLabel(self.navigation_frame, text = LANGUAGE["Restart to update"])
        self.language_updatelabel.grid(row=5, column=0, padx=20, pady=0, sticky="s")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                                values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event,
                                                                fg_color="#191919", button_color="#191919")
        self.appearance_mode_menu.grid(row=7, column=0, padx=20, pady=12, sticky="s")


        # Home Frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.Guide_website_button = customtkinter.CTkButton(self.home_frame, corner_radius=0, height=40,
                                                            border_spacing=10,
                                                            text=LANGUAGE["Guide"],
                                                            font=customtkinter.CTkFont(size=20, weight="bold"),
                                                            fg_color="transparent", text_color=text_color_template,
                                                            hover_color=hover_color_template,
                                                            anchor="w",
                                                            image=self.guide_button_image,
                                                            command=open_guide)
        self.Guide_website_button.grid(row=0, column=0, sticky="ew")

        self.FAQ_website_button = customtkinter.CTkButton(self.home_frame, corner_radius=0, height=40,
                                                          border_spacing=10,
                                                          text=LANGUAGE["FAQ"],
                                                          font=customtkinter.CTkFont(size=20, weight="bold"),
                                                          fg_color="transparent", text_color=text_color_template,
                                                          hover_color=hover_color_template,
                                                          anchor="w",
                                                          image=self.FAQ_Image,
                                                          command=open_FAQ)
        self.FAQ_website_button.grid(row=1, column=0, sticky="ew")


        self.rules_website_button = customtkinter.CTkButton(self.home_frame, corner_radius=0, height=40,
                                                          border_spacing=10,
                                                          text="Conversion Rules",
                                                          font=customtkinter.CTkFont(size=20, weight="bold"),
                                                          fg_color="transparent", text_color=text_color_template,
                                                          hover_color=hover_color_template,
                                                          anchor="w",
                                                          image=self.FAQ_Image,
                                                          command=open_convrules)
        self.rules_website_button.grid(row=2, column=0, sticky="ew")


        # Setup Frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(0, weight=1)

        self.setup_frame_label = customtkinter.CTkLabel(self.second_frame, text=LANGUAGE["setup_frame_label"],
                                                        font=customtkinter.CTkFont(size=30, weight="bold"))
        self.setup_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Paths all the Paths go the same way  We write the Label then the Entry then the Browse Button

        # CK3 Game Path

        self.CK3_Game_Path_Label = customtkinter.CTkLabel(self.second_frame, text=LANGUAGE["install_dir"],
                                                          font=customtkinter.CTkFont(size=20, weight="bold"))
        self.CK3_Game_Path_Label.grid(row=1, column=0, padx=20, pady=20, sticky="w")

        self.CK3_Game_Path_Entry = customtkinter.CTkEntry(self.second_frame, width=600, fg_color="transparent",
                                                          placeholder_text=LANGUAGE["PH_Installdir"])
        self.CK3_Game_Path_Entry.grid(row=2, column=0, padx=20, pady=20, sticky="nw")

        self.CK3_Game_Path_Browse_Button = customtkinter.CTkButton(self.second_frame, corner_radius=0, height=20,
                                                                   border_spacing=1,
                                                                   fg_color="transparent",
                                                                   text_color=text_color_template,
                                                                   hover="false", text="", image=self.browse_image,
                                                                   border_color="gray", anchor="nw",
                                                                   command=lambda: browse_directory(
                                                                       self.CK3_Game_Path_Entry))
        self.CK3_Game_Path_Browse_Button.grid(row=2, column=0, padx=10, pady=15, sticky="ne")

        # CK3 Mod Folder Path

        self.CK3_Mod_Path_Label = customtkinter.CTkLabel(self.second_frame, text=LANGUAGE["mod_dir"],
                                                         font=customtkinter.CTkFont(size=20, weight="bold"))
        self.CK3_Mod_Path_Label.grid(row=3, column=0, padx=20, pady=20, sticky="w")

        self.CK3_Mod_Path_Entry = customtkinter.CTkEntry(self.second_frame, width=600, fg_color="transparent",
                                                         placeholder_text=LANGUAGE["PH_Modfolder"], )
        self.CK3_Mod_Path_Entry.grid(row=4, column=0, padx=20, pady=20, sticky="nw")

        self.CK3_Mod_Path_Browse_Button = customtkinter.CTkButton(self.second_frame, corner_radius=0, height=20,
                                                                  border_spacing=1,
                                                                  fg_color="transparent",
                                                                  text_color=text_color_template,
                                                                  hover="false", text="", image=self.browse_image,
                                                                  border_color="gray", anchor="nw",
                                                                  command=lambda: browse_directory(
                                                                      self.CK3_Mod_Path_Entry))
        self.CK3_Mod_Path_Browse_Button.grid(row=4, column=0, padx=10, pady=15, sticky="ne")

        # Map Filler Tool Path

        self.CK3_Map_Filler_Tool_Path_Label = customtkinter.CTkLabel(self.second_frame,
                                                                     text=LANGUAGE["map_filler_dir"],
                                                                     font=customtkinter.CTkFont(size=20, weight="bold"))
        self.CK3_Map_Filler_Tool_Path_Label.grid(row=5, column=0, padx=20, pady=20, sticky="w")

        self.CK3_Map_Filler_Tool_Path_Entry = customtkinter.CTkEntry(self.second_frame, width=600,
                                                                     fg_color="transparent",
                                                                     placeholder_text=LANGUAGE["PH_MapFiller"], )
        self.CK3_Map_Filler_Tool_Path_Entry.grid(row=6, column=0, padx=20, pady=20, sticky="nw")

        self.CK3_Map_Filler_Tool_Path_Browse_Button = customtkinter.CTkButton(self.second_frame, corner_radius=0,
                                                                              height=20,
                                                                              border_spacing=1,
                                                                              fg_color="transparent",
                                                                              text_color=text_color_template,
                                                                              hover="false", text="",
                                                                              image=self.browse_image,
                                                                              border_color="gray", anchor="nw",
                                                                              command=lambda: browse_directory(
                                                                                  self.CK3_Map_Filler_Tool_Path_Entry))
        self.CK3_Map_Filler_Tool_Path_Browse_Button.grid(row=6, column=0, padx=10, pady=15, sticky="ne")

        # Button for Saving Paths

        self.Save_Paths_Button = customtkinter.CTkButton(self.second_frame, corner_radius=0, height=20,
                                                         border_spacing=1,
                                                         fg_color="transparent",
                                                         text_color=text_color_template,
                                                         hover="false", text=LANGUAGE["Save Paths"],
                                                         font=customtkinter.CTkFont(size=20, weight="bold"),
                                                         image=self.Save_Paths_Image,
                                                         border_color="gray", anchor="se",
                                                         command=save_paths, )
        self.Save_Paths_Button.grid(row=7, column=0, padx=10, pady=15, sticky="se")

        self.Load_Paths_Button = customtkinter.CTkButton(self.second_frame, corner_radius=0, height=20,
                                                         border_spacing=1,
                                                         fg_color="transparent",
                                                         text_color=text_color_template,
                                                         hover="false", text=LANGUAGE["Load Paths"],
                                                         font=customtkinter.CTkFont(size=20, weight="bold"),
                                                         image=self.Save_Paths_Image,
                                                         border_color="gray", anchor="se",
                                                         command=load_paths,)
        self.Load_Paths_Button.grid(row=7, column=0, padx=10, pady=15, sticky="sw")

        # Options Frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame.grid_columnconfigure(0, weight=1)

        self.Options_Label = customtkinter.CTkLabel(self.third_frame, text=LANGUAGE["Options"],
                                                    font=customtkinter.CTkFont(size=30, weight="bold"))
        self.Options_Label.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        self.Options_Scaling_Label = customtkinter.CTkLabel(self.third_frame, text=LANGUAGE["Select Scaling Method"],
                                                            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.Options_Scaling_Label.grid(row=1, column=0, padx=20, pady=20, sticky="n")

        # To show the default value of optionmenu that don't cause issues
        Scaling_var = customtkinter.StringVar(value="Automatic Scaling")
        Charactergen_var = customtkinter.StringVar(value="Don't Generate Characters")

        self.Options_Scaling_Menu = customtkinter.CTkOptionMenu(self.third_frame, variable=Scaling_var,
                                                                values=["Manual Scaling", "Automatic Scaling"],
                                                                fg_color="#4F4F4F", button_color="gray",
                                                                command=optionmenu_callback)
        self.Options_Scaling_Menu.grid(row=2, column=0, padx=20, pady=20, sticky="n")

        self.Generate_Characters_Label = customtkinter.CTkLabel(self.third_frame,
                                                                text=LANGUAGE["charGen"],
                                                                font=customtkinter.CTkFont(size=20, weight="bold"))
        self.Generate_Characters_Label.grid(row=5, column=0, padx=20, pady=20, sticky="n")

        self.Generate_Characters_Menu = customtkinter.CTkOptionMenu(self.third_frame, variable=Charactergen_var,
                                                                    values=["Generate Characters",
                                                                            "Don't Generate Characters"],
                                                                    fg_color="#4F4F4F", button_color="gray",
                                                                    command=optionmenu_callback)
        self.Generate_Characters_Menu.grid(row=6, column=0, padx=20, pady=20, sticky="n")

        self.Generate_blur_radius_label = customtkinter.CTkLabel(self.third_frame,
                                                                text="Blur Radius",
                                                                font=customtkinter.CTkFont(size=20, weight="bold"))
        self.Generate_blur_radius_label.grid(row=7, column=0, padx=20, pady=20, sticky="n")


        self.blur_heightmap_entry= customtkinter.CTkEntry(self.third_frame, width=284,
                                                                     fg_color="transparent",
                                                                     placeholder_text="7 for 100k, larger values for lower points number", )
        self.blur_heightmap_entry.grid(row=8, column=0, padx=20, pady=20, sticky="n")



        # Conversion Frame

        self.fourth_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fourth_frame.grid_columnconfigure(0, weight=1)

        self.Conversion_Label = customtkinter.CTkLabel(self.fourth_frame, text="Conversion",
                                                       font=customtkinter.CTkFont(size=30, weight="bold"))
        self.Conversion_Label.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        self.Mod_Name_Label = customtkinter.CTkLabel(self.fourth_frame, text=LANGUAGE["mod_name"],
                                                     font=customtkinter.CTkFont(size=20, weight="bold"))
        self.Mod_Name_Label.grid(row=1, column=0, padx=20, pady=20, sticky="n")

        self.Mod_Name_Entry = customtkinter.CTkEntry(self.fourth_frame, fg_color="transparent", )
        self.Mod_Name_Entry.grid(row=2, column=0, padx=20, pady=20, sticky="n")

        self.start_conversion_label = customtkinter.CTkLabel(self.fourth_frame, text=LANGUAGE["Start Conversion"],
                                                             font=customtkinter.CTkFont(size=20, weight="bold"))
        self.start_conversion_label.grid(row=3, column=0, padx=20, pady=20, sticky="n")

        self.Conversion_button = customtkinter.CTkButton(self.fourth_frame, corner_radius=0, height=20,
                                                         border_spacing=1, fg_color="transparent",
                                                         text_color=text_color_template,
                                                         hover_color=hover_color_template, text="",
                                                         border_color="gray"
                                                         , command=run_conv_thread, image=self.Start_Button_Image, anchor="n",
                                                         )
        self.Conversion_button.grid(row=4, column=0, padx=20, pady=20, sticky="n")

        self.Conversion_progress_bar = customtkinter.CTkProgressBar(self.fourth_frame, )
        self.Conversion_progress_bar.grid(row=5, column=0, padx=20, pady=20, sticky="n")
        self.Conversion_progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self.fourth_frame, text="Status",
                                                             font=customtkinter.CTkFont(size=20, weight="bold"))
        self.status_label.grid(row=6, column=0, padx=20, pady=20, sticky="n")

        self.loading_wheel = LoadingWheel(self.fourth_frame,size=50, bg_color="#EBEBEB", arc_color="#1a1a1a")



        self.openModFolder = customtkinter.CTkButton(self.fourth_frame, corner_radius=0, height=20,
                                                         border_spacing=1, fg_color="transparent",
                                                         text_color=text_color_template,
                                                         hover_color=hover_color_template, text="Open Output folder",
                                                         border_color="gray"
                                                         , command=openModFolder, image=self.browse_image,
                                                         anchor="n",
                                                         )
        self.openModFolder.grid(row=7, column=0, padx=20, pady=20, sticky="sw")



        # General Frame Settings
        # Contain Commands for all buttons to open Frames
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):

        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.setup_frame_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.settings_frame_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
        self.conversion_frame_button.configure(fg_color=("gray75", "gray25") if name == "frame_4" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

        if name == "frame_4":
            self.fourth_frame.grid(row=0, column=1, sticky="nsew")
        else:

            self.fourth_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def setup_frame_button_event(self):
        self.select_frame_by_name("frame_2")

    def settings_frame_button_event(self):
        self.select_frame_by_name("frame_3")

    def conversion_frame_button_event(self):
        self.select_frame_by_name("frame_4")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode == "Dark":
            self.loading_wheel.redraw(bg_color="#242424", arc_color="#dce4ee")
            print("Changed wheel to dark")
        elif new_appearance_mode =="Light":
            self.loading_wheel.redraw(bg_color="#ebebeb", arc_color="#1a1a1a")
            print("Changed wheel to light")


class LoadingWheel(tk.Canvas):
    def __init__(self, parent, size=50, bg_color="#EBEBEB", arc_color="#1a1a1a", width=5, speed=10):
        tk.Canvas.__init__(self, parent, width=size, height=size, highlightthickness=0)
        self.parent = parent
        self.bg_color = bg_color
        self.arc_color = arc_color
        self.width = width
        self.speed = speed
        self.arc = None
        self.start_angle = 0
        self.after_id = None  # store the id of the 'after' call
        self.draw_wheel()

    def draw_wheel(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)  # cancel previous 'after' call if it exists
        self.arc = self.create_arc(
            self.width, self.width, self.winfo_width() - self.width,
            self.winfo_height() - self.width, start=self.start_angle,
            extent=50, width=self.width, style=tk.ARC, outline=self.arc_color
        )
        self.after_id = self.after(self.speed, self.animate)  # store the id of the new 'after' call
        self.configure(background=self.bg_color)

    def animate(self):
        self.start_angle = (self.start_angle - 10) % 360
        self.delete(self.arc)
        self.draw_wheel()

    def redraw(self, bg_color=None, arc_color=None):
        if bg_color:
            self.bg_color = bg_color
            self.configure(background=self.bg_color)
        if arc_color:
            self.arc_color = arc_color
            self.delete(self.arc)
            self.draw_wheel()

#app = App()
#app.mainloop()
