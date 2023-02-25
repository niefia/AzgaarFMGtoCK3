import modFiles
import religion
import spreadsheets
import rasterMaps
import BFS
import hextorgb
import os
import modFiles


print("Scaling Factor Determines map size, Try 50 to start with")
scaling_factor = float(input("Enter Scaling Factor: "))
print("")

def runGen():

    print("Please make sure the Azgaar json is in the Mod Directory as input.json, and the Azgaar Cells Geojson is in the Mod Directory as input.geojson")
    print("For example C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod/input.json")
    print("")

    # Get output directory path from user input
    print("Example Mod Directory: C:/Users/USERNAME/Documents/Paradox Interactive/Crusader Kings III/mod")
    modpath = input("Enter the CK3 Mod directory : ")
    print("")

    print( "Mod Name")
    # Get output directory path from user input
    modname = input("Enter your desired mod name: ")
    print("")

    output_dir = os.path.join(modpath,modname)

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
    print("Generate ProvinceDef.xlsx file for Cells, must be manually converted to XLS for Map Filler tool")

    #Runs data to Rasterised Image

    rasterMaps.heightmap(os.path.join(output_dir, "output.geojson"),
                         os.path.join(output_dir, "map_data", "heightmap.png"), scaling_factor)
    print("Generating Heightmap")

    # Generate provinces image
    rasterMaps.provincesCells(os.path.join(output_dir, "output.geojson"),
                              os.path.join(output_dir, "map_data", "provinces.png"), scaling_factor)
    print("Generating Cells provinces")

    # Generate biomes images
    rasterMaps.biomes(os.path.join(output_dir, "output.geojson"), os.path.join(output_dir, "gfx", "map", "terrain"),
                      scaling_factor)
    print("Generated Biomes")



    #Runs Religion Generator

    religion.familyGen(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, "common/religion/religion_families"))
    religion.religionChildren(os.path.join(output_dir, "combined_data.xlsx"),
                              os.path.join(output_dir, "religionChildren.xlsx"))
    religion.relGenChil(os.path.join(output_dir, "religionChildren.xlsx"),
                        os.path.join(output_dir, "religionChildren_cName.xlsx"))
    religion.religionGen(os.path.join(output_dir, "religionChildren_cName.xlsx"),
                         os.path.join(output_dir, "common/religion/religions"))


    #BFS Functions
    print("Breadth First search started")
    # Run Breadth First search to generate Baronies
    BFS.bfs_distance(os.path.join(output_dir, "combined_data.xlsx"), os.path.join(output_dir, "cellsData.xlsx"),
                     os.path.join(output_dir, "BFSoutput.xlsx"))
    print("Breadth First search Complete")

    # Assign unique color to Baronies
    BFS.colorRandomBFS(os.path.join(output_dir, "BFSoutput.xlsx"))
    print("Assigning unique color to Baronies")

    # Generate BFS provinces image
    BFS.provinceMapBFS(os.path.join(output_dir, "BFSoutput.xlsx"), scaling_factor,
                       os.path.join(output_dir, "map_data", "provinces.png"))
    print("Generating BFS provinces")


    #BFSProvDef

    BFS.extractBFS(os.path.join(output_dir, "BFSoutput.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))

    BFS.BaronyId(os.path.join(output_dir, "combined_data.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))
    BFS.ProvData(os.path.join(output_dir,"updated_file.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))
    BFS.cOrder(os.path.join(output_dir,"_mapFiller/provinceDef.xlsx"))

runGen()
