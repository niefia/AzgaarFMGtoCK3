import bookmark
import modFiles
import religion
import spreadsheets
import rasterMaps
import BFS
import hextorgb
import os
import modFiles
import openpyxl
import pandas as pd
import xlwt
import culture
import sys
import character
import localization
import uictk
import customtkinter

scaling_method = 2
scaling_factor = 35
modpath = ("")
modname = ("")
mapfilldir = ("")
installdir = ("")
CharGen_response = ("")


#print("Scaling Method 1 = Manual Scaling            Scaling Method 2 = Auto-Scaling")

#scaling_method = int(input("Scaling Method: "))

#if scaling_method == 1:
    #print("Manual Scaling Method Selected")
    #scaling_factor == input("Enter Scaling Factor: ")
#elif scaling_method ==2:
    #print("Auto-Scaling Selected")
#else:
    #print("Invalid Scaling Method")
    #exit()


#print("Scaling Factor Determines map size, Try 50 to start with")
#scaling_factor = float(input("Enter Scaling Factor: "))
#print("")

def runGen():
    try:
        print("Please make sure the Azgaar json is in the Mod Directory as input.json, and the Azgaar Cells Geojson is in the Mod Directory as input.geojson")
        print("For example C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod/input.json")
        print("")

        # Get output directory path from user input
        print("Example Mod Directory: C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod - the mod at the end should not be changed to your mods name, this is the CK3 mods folder")
        modpath = input("Enter the CK3 Mod directory : ")
        print("")

        print( "Mod Name")
        # Get output directory path from user input
        modname = input("Enter your desired mod name: ")
        print("")

        mapfilldir = input("Enter the Map Filler Directory : ")
        print("")

        installdir = input("Enter the CK3 install Directory : ")

        print("Do you want to generate characters to hold the state level titles? This feature is not finished yet and the characters should only be considered as placeholder to have Kingdoms exist at game start")
        CharGen_response = input("Enter 'yes' or 'no': ")

        # set gamedir to be the game subfolder of installdir
        gamedir = os.path.join(installdir, 'game')


        output_dir = os.path.join(modpath,modname)

        print(gamedir)
        # Create output directory if it doesn't exist

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        modFiles.modFile(modname, output_dir, modpath)

        # Create "map_data" subfolder
        map_data_dir = os.path.join(output_dir, "map_data")
        if not os.path.exists(map_data_dir):
            os.makedirs(map_data_dir)

        # Create "map_data" subfolder
        map_data_dir = os.path.join(output_dir, "_mapFiller")
        if not os.path.exists(map_data_dir):
                os.makedirs(map_data_dir)

        # Create "gfx/map/terrain/" subfolder
        map_data_dir = os.path.join(output_dir, "gfx/map/terrain/")
        if not os.path.exists(map_data_dir):
                os.makedirs(map_data_dir)

            # Create "gfx/map/terrain/" subfolder
        map_data_dir = os.path.join(output_dir, "gfx/map/terrain/")
        if not os.path.exists(map_data_dir):
            os.makedirs(map_data_dir)

        #Run spreadsheets generators

        # Remove emoji from JSON file
        spreadsheets.remove_emoji_from_json(os.path.join(modpath, "input.json"),
                                            os.path.join(output_dir, "noemoji.json"))
        print("Emoji data removed from json")


        # Assign colors to Baronies in GeoJSON file
        spreadsheets.colorRandom(os.path.join(modpath, "input.geojson"), os.path.join(output_dir, "output.geojson"))
        print("Colors Assigned to Baronies for Cells method")

        # Convert JSON to Excel spreadsheet
        spreadsheets.json_to_sheet(os.path.join(output_dir, "noemoji.json"), os.path.join(output_dir, "combined_data.xlsx"))
        print("Json extracted")

        # Convert GeoJSON to Excel spreadsheet
        spreadsheets.cells_geojson_to_sheet(os.path.join(output_dir, "output.geojson"),
                                            os.path.join(output_dir, "cellsData.xlsx"))
        print("Geojson extracted")

        # Correct cell names in Excel spreadsheet
        spreadsheets.nameCorrector(os.path.join(output_dir, "cellsData.xlsx"),
                                   os.path.join(output_dir, "combined_data.xlsx"),
                                   os.path.join(output_dir, "updated_file.xlsx"))
        print("Geojson data updated with Json names")

        # Generate ProvinceDef.xlsx file for Cells
        spreadsheets.provinceDefCells(os.path.join(output_dir, "updated_file.xlsx"),
                                      os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))
        print("Generate ProvinceDef.xlsx file for Cells")

        #Runs data to Rasterised Image


        #heightmap scaling methods
        if scaling_method == 1:
            rasterMaps.heightmap(os.path.join(output_dir, "output.geojson"),
                                 os.path.join(output_dir, "map_data", "heightmap.png"), scaling_factor)
            print("Generating Heightmap")
        elif scaling_method == 2:
            rasterMaps.heightmapAutoScaledfunc(os.path.join(output_dir, "output.geojson"),
                                           os.path.join(output_dir, "map_data", "heightmap.png"))
            print("Generating Auto-Scaled Heightmap")
        else:
            print("Invalid scaling method")





        # Generate provinces image
        rasterMaps.provincesCells(os.path.join(output_dir, "output.geojson"),
                                  os.path.join(output_dir, "map_data", "provinces.png"), scaling_factor)
        print("Generating Cells provinces")



        # Generate biomes images

        if scaling_method == 1:
            rasterMaps.biomes(os.path.join(output_dir, "output.geojson"), os.path.join(output_dir, "gfx", "map", "terrain"),
                          scaling_factor)
            print("Generated Biomes")
        elif scaling_method == 2:
            rasterMaps.biomesAutoScaled(os.path.join(output_dir, "output.geojson"),
                              os.path.join(output_dir, "gfx", "map", "terrain"))
            print("Generated Auto-Scaled Biomes")
        else:
            print("Invalid scaling method")








        #Rename biome files to CK3 texture names using the json data
        modFiles.biomeWrite(os.path.join(output_dir, 'noemoji.json'),
                   os.path.join(output_dir, 'biomes.xlsx'),
                   os.path.join(output_dir, 'gfx/map/terrain'))


        input_zip_file = os.path.join(modpath, "tcs.zip")
        # Call the extract_zip_file function
        modFiles.extract_zip_file(input_zip_file, output_dir)



        #Runs Religion Generator

        religion.familyGen(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, "common/religion/religion_families"))
        religion.religionChildren(os.path.join(output_dir, "combined_data.xlsx"),
                                  os.path.join(output_dir, "religionChildren.xlsx"))
        religion.relGenChil(os.path.join(output_dir, "religionChildren.xlsx"),
                            os.path.join(output_dir, "religionChildren_cName.xlsx"))
        religion.religionGen(os.path.join(output_dir, "religionChildren_cName.xlsx"),
                             os.path.join(output_dir, "common/religion/religions"))

        #Runs Culture Generator

        culture.heritage_gen(os.path.join(output_dir, 'combined_data.xlsx'), os.path.join(output_dir, 'common/culture/pillars'))

        culture.culture_gen(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, 'common/culture/cultures'))


        #BFS Functions
        print("Breadth First search started, this generates Baronies from cells and may take some time to run")
        # Run Breadth First search to generate Baronies
        BFS.bfs_distance(os.path.join(output_dir, "combined_data.xlsx"), os.path.join(output_dir, "cellsData.xlsx"),
                         os.path.join(output_dir, "BFSoutput.xlsx"))
        print("")
        print("Breadth First search Complete")

        # Assign unique color to Baronies
        BFS.colorRandomBFS(os.path.join(output_dir, "BFSoutput.xlsx"))
        print("Assigning unique color to Baronies")




        if scaling_method == 1:
            # Generate BFS provinces image
            BFS.provinceMapBFS(os.path.join(output_dir, "BFSoutput.xlsx"), scaling_factor,
                           os.path.join(output_dir, "map_data", "provinces.png"))
            print("Generating BFS provinces")
        elif scaling_method == 2:
            rasterMaps.provinceMapBFSAutoScaled(os.path.join(output_dir, "BFSoutput.xlsx"),
                               os.path.join(output_dir, "map_data", "provinces.png"))








        #BFSProvDef

        BFS.extractBFS(os.path.join(output_dir, "BFSoutput.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))

        BFS.BaronyId(os.path.join(output_dir, "combined_data.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))
        BFS.ProvData(os.path.join(output_dir,"updated_file.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))
        BFS.cOrder(os.path.join(output_dir,"_mapFiller/provinceDef.xlsx"))
        BFS.finalorder(os.path.join(output_dir,"_mapFiller/provinceDef.xlsx"))
        BFS.convert_xlsx_to_xls(os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xls"))

        # Get output directory path from user input
        print("Automatic Map Filler Running")
        config_file_path = os.path.join(mapfilldir, "config.properties")
        print(config_file_path)
        moddir = output_dir

        modFiles.modify_config(moddir, gamedir, config_file_path)

        jar_path = os.path.join(mapfilldir, "CK3Tools.jar")
        cwd = mapfilldir
        modFiles.run_jar(jar_path, cwd)

        localization.religionLoc(output_dir)


        if CharGen_response.lower() == "yes":
            print("Character Generation running:")
            character.rulerGenXL(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, "characters.xlsx"))
            character.rulerWrite(os.path.join(output_dir, "characters.xlsx"),os.path.join(output_dir, "history/characters/"))
            character.modHistory(os.path.join(output_dir, "characters.xlsx"),os.path.join(output_dir, "history/titles/"))
            bookmark.bm_groups(output_dir)
            bookmark.bm_generator(output_dir, 3)


        elif CharGen_response.lower() == "no":
            print("Shattered World Mode.")
        else:
            print("Invalid response. Please enter 'yes' or 'no'.")





    except Exception as e:
        print(f"An error occurred: {e}")
        # Wait for user input before closing
        input("Press Enter to exit...")
        sys.exit(1)  # exit with an error code




#runGen()
import bookmark
import modFiles
import religion
import spreadsheets
import rasterMaps
import BFS
import hextorgb
import os
import modFiles
import openpyxl
import pandas as pd
import xlwt
import culture
import sys
import character
import localization
import uictk
import customtkinter
import sys
sys.stdout = open("log.txt", "w")

if __name__ == "__main__":
    root = customtkinter.CTk
    app = uictk.App()
    app.mainloop()
    sys.stdout.close()





# Wait for user input before closing
#input("Press Enter to exit...")