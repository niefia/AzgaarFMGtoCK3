import bookmark
import religion
import spreadsheets
import rasterMaps
import BFS
import os
import modFiles
import culture
import sys
import character
import localization
import openpyxl
import pandas as pd
import xlwt
import hextorgb
import modFiles






def runGenExcel(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):


        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        modFiles.modFile(modname, output_dir, modpath)
        #CREATES DIRECTORIES

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


        #RUN SPREADSHEET GENERATORS

        # Remove emoji from JSON file
        spreadsheets.remove_emoji_from_json(os.path.join(modpath, "input.json"),
                                            os.path.join(output_dir, "noemoji.json"))
        print("Emoji data removed from json")

        # Convert JSON to Excel spreadsheet
        spreadsheets.json_to_sheet(os.path.join(output_dir, "noemoji.json"), os.path.join(output_dir, "combined_data.xlsx"))
        print("Json extracted")
        # Comment from snibbo: moved this here, since this is related to / next step after "noemoji.json"


        # Assign colors to Baronies in GeoJSON file
        spreadsheets.colorRandom(os.path.join(modpath, "input.geojson"), os.path.join(output_dir, "output.geojson"))
        print("Colors Assigned to Baronies for Cells method")

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






def runGenRaster(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):


        #DATA TO RASTERIZED IMAGE


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

        rasterMaps.heightmap_to_mountain_biome(output_dir)
        rasterMaps.heightmap_blur_and_noise(output_dir)
        rasterMaps.gradient_map(output_dir)


def runGenPaper(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):

    print(output_dir)
    print("Paper Map Generating...")
    rasterMaps.paint_land_sea_mask(os.path.join(output_dir,"map_data/heightmap_for_paper.png"),os.path.join(output_dir,"masksea.png"))


    rasterMaps.create_masked_image(os.path.join(output_dir, 'sea_image.png'), os.path.join(output_dir, 'land_image.png'),os.path.join(output_dir, 'masksea.png'), os.path.join(output_dir, 'flatmap1.dds'))


    rasterMaps.produce_outline(os.path.join(output_dir,'masksea.png'), os.path.join(output_dir, 'flatmapBorder.png'))

    rasterMaps.overlay_png_on_dds(os.path.join(output_dir,'flatmapBorder.png'), os.path.join(output_dir,'flatmap1.dds'), os.path.join(output_dir,'gfx/map/terrain/flatmap.dds'))
    print("Paper Map Generated")






def runGenRelCult(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):


        print("Extracting tcs.zip")
        input_zip_file = os.path.join(modpath, "tcs.zip")
        # Call the extract_zip_file function
        modFiles.extract_zip_file(input_zip_file, output_dir)
        print("Finished extracting tcs.zip")



        #Runs Religion Generator
        print("Running religion family gen")
        religion.familyGen(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, "common/religion/religion_families"))
        print("Running religion children gen")
        religion.religionChildren(os.path.join(output_dir, "combined_data.xlsx"),
                                  os.path.join(output_dir, "religionChildren.xlsx"))
        print("running religion genchil")
        religion.relGenChil(os.path.join(output_dir, "religionChildren.xlsx"),
                            os.path.join(output_dir, "religionChildren_cName.xlsx"))
        print("running ")
        religion.religionGen(os.path.join(output_dir, "religionChildren_cName.xlsx"),
                             os.path.join(output_dir, "common/religion/religions"))

        #Runs Culture Generator

        culture.heritage_gen(os.path.join(output_dir, 'combined_data.xlsx'), os.path.join(output_dir, 'common/culture/pillars'))

        culture.culture_gen(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, 'common/culture/cultures'))







def runGenBFS(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):


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
        spreadsheets.combined_data_empires(os.path.join(output_dir, "combined_data.xlsx"))
        print("Applied Vassal/Suzerain relationships to combined data")

        spreadsheets.combined_data_empires_id_to_name(os.path.join(output_dir, "combined_data.xlsx"))
        print("Applied Name to Vassal/Suzerain ID relationships to combined data")
        spreadsheets.update_provincedef_empires_vassalsuzerain(os.path.join(output_dir, "combined_data.xlsx"),
                                                               os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"))

        BFS.convert_xlsx_to_xls(os.path.join(output_dir, "_mapFiller/provinceDef.xlsx"), os.path.join(output_dir, "_mapFiller/provinceDef.xls"))


def runMapFill(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):

        # Get output directory path from user input
        print("Automatic Map Filler Running")
        config_file_path = os.path.join(mapfilldir, "config.properties")
        print(config_file_path)
        moddir = output_dir

        modFiles.modify_config(moddir, gamedir, config_file_path)

        jar_path = os.path.join(mapfilldir, "CK3Tools.jar")
        cwd = mapfilldir
        modFiles.run_jar(jar_path, cwd)

        print("Map Filler Complete")

        localization.religionLoc(output_dir)


def Terrains(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):
    BFS.BaronyIdBiomes(os.path.join(output_dir, "combined_data.xlsx"),os.path.join(output_dir, "cellsData.xlsx"),os.path.join(output_dir, "townBiomes.csv"))
    spreadsheets.terrainGenIdtoName(os.path.join(output_dir, 'townBiomes.csv'), os.path.join(output_dir, 'biomes.xlsx'))
    spreadsheets.terrainGenRGB(os.path.join(output_dir, 'townBiomes.csv'), (os.path.join(output_dir, '_mapFiller/provinceDef.xlsx')))
    spreadsheets.terrainGen(os.path.join(output_dir, 'townBiomes.csv'), (os.path.join(output_dir, 'common/province_terrain/00_province_terrain.txt')))



def runCharBook(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response, gamedir,output_dir):


        localization.religionLoc(output_dir)

        if CharGen_response.lower() == "yes":
            print("Character Generation running:")
            character.rulerGenXL(os.path.join(output_dir, "combined_data.xlsx"),
                                 os.path.join(output_dir, "characters.xlsx"))
            character.rulerWrite(os.path.join(output_dir, "characters.xlsx"),
                                 os.path.join(output_dir, "history/characters/"))
            character.modHistory(os.path.join(output_dir, "characters.xlsx"),
                                 os.path.join(output_dir, "history/titles/"))
            bookmark.bm_groups(output_dir)
            bookmark.bm_generator(output_dir, 3)


        elif CharGen_response.lower() == "no":
            print("Shattered World Mode.")
        else:
            print("Invalid response. Please enter 'yes' or 'no'.")










def printValues(modpath, mapfilldir, installdir, scaling_method, scaling_factor, modname, CharGen_response,gamedir,output_dir):
    print("Modpath: ", modpath)
    print("mapfilldir: ", mapfilldir)
    print("installdir: ", installdir)
    print("scaling_method: ", scaling_method)
    print("scaling_factor: ", scaling_factor)
    print("modname: ", modname)
    print("CharGen_response: ", CharGen_response)
    print("Gamedir:",gamedir)
    print("output_dir:",output_dir)
