import time
import numpy as np
import pandas as pd
import ast
import BFS
from collections import Counter

# import collections
# import os
# from queue import Queue
# import openpyxl
# from openpyxl import Workbook
# from openpyxl.styles import PatternFill
# import random
# import hextorgb
# from PIL import Image, ImageDraw
# import re
# import xlwt

MAX_RUNS = 2500

def myLogging(message):
    print(time.ctime(), message)

maxBaronySize = 5   # number of Cells in a Barony
maxCountySize = 3   # number of Baronies in a County
maxDuchySize = 5    # number of Counties in a Duchy
maxKingdomSize = 7  # number of Duchies in a Kingdom

dir = "../ck3_map_gen_data/_2ndMap/data/"
cells_data_file = dir + "cellsData.xlsx"
updated_file = dir + "updated_file.xlsx"
bfs_distance_file = dir + "bfs_distance_file.xlsx"
def_baronies_file = dir + "def_baronies_file.xlsx"
def_counties_file = dir + "def_counties_file.xlsx"
def_duchies_file = dir + "def_duchies_file.xlsx"
def_kingdoms_file = dir + "def_kingdoms_file.xlsx"

output_png = dir + "provinces.png"
provinceDef_file = dir + "provinceDef.xlsx"
final_file = dir + "final_file.xlsx"


def getNeighbors(dfProvinces: pd.DataFrame, id):
    return dfProvinces.loc[dfProvinces['id'] == id, 'neighbors'].tolist()[0]
def getRealmIds(dfProvinces: pd.DataFrame, id):
    realmIds = dfProvinces.loc[dfProvinces['id'] == id, 'realmIds'].tolist()[0]
    return realmIds
def getProvinceIdFromRealmIds(dfProvinces: pd.DataFrame, id):
    # return if a cell id is in a realm >> return id of county / duchy / kingdom / empire
    realmDict = dict(zip(dfProvinces['id'], dfProvinces['realmIds']))
    for provinceId, realm_ids in realmDict.items():
        if id in realm_ids:
            return provinceId
# def getProvinceIdFromRealmIds(dfProvinces: pd.DataFrame, id):
#     # return if a cell id is in a realm >> return id of county / duchy / kingdom / empire
#     realmDict = dict(zip(dfProvinces['id'], dfProvinces['realmIds']))
#     for provinceId, realm_ids in realmDict.items():
#         if id in realm_ids:
#             return provinceId

# def cleanNeighbors(dfProvinces: pd.DataFrame, id):
#     neighbors = ast.literal_eval(dfProvinces.loc[dfProvinces['id'] == id, 'neighbors'].tolist()[0])
#     realmIds = ast.literal_eval(dfProvinces.loc[dfProvinces['id'] == id, 'realmIds'].tolist()[0])
#     newNb = []
#     for nb in neighbors:
#         if nb not in realmIds:
#             newNb.append(nb)
#     dfProvinces.loc[dfProvinces['id'] == id, 'neighbors'].tolist()[0] = newNb
#     return dfProvinces

def removeNeighborsThatAreRealm():
    print("ok")


def calculateBaronies(maxBaronySize, cells_data_file, bfs_distance_file, def_baronies_file):
    # This function tries to combine connected cells to a Barony. The "maxBaronySize" is a measure to be used as indicator. 
    myLogging("Calculation started")
    myLogging("Reading file...")
    cells_data = pd.read_excel(cells_data_file)
    cells_data['neighbors'] = cells_data['neighbors'].apply(lambda x: [int(n) for n in x.strip('[]').split(',')])
    cells_data['processed'] = cells_data['id'].apply(lambda x: False)       # add an indicator whether the cell has been processed

    myLogging("Create new DataFrame...")
    dfDistance = pd.DataFrame(columns=['id', 'distance', 'nearest_town', 'tId', 'coordinates', 'neighbors'])
    dfProvinces = pd.DataFrame(columns=['id', 'Barony', 'size', 'realmIds', 'Biome', 'Coordinates', 'neighbors'])
    
    counter = 0

    # loop over cell list once
    for id in cells_data['id'].tolist():
        isProcessedCell = cells_data.loc[cells_data['id'] == id, 'processed'].tolist()[0]
        if isProcessedCell == False:
            # print("Result is NaN >> Cell was not processed before")
            # only allow to work when the cell was not processed by another cell already
            # only relevant when not ocean or lake >> we might want to check for connected islands later
            cellType = cells_data.loc[cells_data['id'] == id, 'type'].tolist()[0]
            if cellType == 'ocean' or cellType == 'lake':                
                cells_data.loc[cells_data['id'] == id, 'processed'] = True            
            if (cellType != 'ocean' and cellType != 'lake'):
                counter += 1
                myLogging(f"Processing started for Id {id}")
                newId = id
                barony = cells_data.loc[cells_data['id'] == id, 'Barony'].tolist()[0]
                # check if name already exists
                barnonyNameExists = dfProvinces.loc[dfProvinces['Barony'] == barony, 'id'].tolist()
                if len(barnonyNameExists) > 0:
                    # create a new name
                    barony = barony + '-1'
                size = 1
                biome = [cells_data.loc[cells_data['id'] == id, 'biome'].tolist()[0]]
                coordinates = cells_data.loc[cells_data['id'] == id, 'coordinates'].tolist()[0]
                neighbors = cells_data.loc[cells_data['id'] == id, 'neighbors'].tolist()[0]
                realmIds = [id]

                # add Entry to Distance file
                newEntryDistance = [id, 0, barony, id, coordinates, str(neighbors)]
                dfDistance.loc[len(dfDistance)] = newEntryDistance
                
                # create a joined list for all neighboring cells - including neighbors of those neighbors that will be integrated into a baronies realm
                joinedlistNeighbors = neighbors
                
                # loop neighbours
                for nb in neighbors:
                    if size <= maxBaronySize:
                        #     myLogging(f"Ignoring neighbor with Id {nb}")
                        # else:
                        if (cells_data.loc[cells_data['id'] == nb, 'processed'].tolist()[0] == False):
                            # Check if neighbor is water
                            nbCellType = cells_data.loc[cells_data['id'] == nb, 'type'].tolist()[0]
                            if nbCellType == 'ocean' or nbCellType == 'lake':                
                                cells_data.loc[cells_data['id'] == nb, 'processed'] = True
                            else:
                                # Add neighbor to id
                                size += 1
                                nbBiome = cells_data.loc[cells_data['id'] == nb, 'biome'].tolist()[0]
                                biome.append(nbBiome)
                                realmIds.append(nb)
                                # write to Distance as well
                                nbCoords = cells_data.loc[cells_data['id'] == nb, 'coordinates'].tolist()[0]
                                nbNeighbors = cells_data.loc[cells_data['id'] == nb, 'neighbors'].tolist()[0]
                                newEntryDistance = [nb, 1, barony, id, nbCoords, str(nbNeighbors)]
                                dfDistance.loc[len(dfDistance)] = newEntryDistance

                                if type(coordinates) == list:
                                    coordinates.append(nbCoords)
                                else:
                                    coordinates = [coordinates, nbCoords]
                                for nbnb in nbNeighbors:
                                    if nbnb not in joinedlistNeighbors and nbnb not in realmIds:
                                        joinedlistNeighbors.append(nbnb)
                                neighbors = list(set(joinedlistNeighbors))
                                neighbors = sorted(neighbors)
                                # clean up neighbors if required
                                newNb = []
                                for joinedNb in joinedlistNeighbors:
                                    if joinedNb not in realmIds:
                                        newNb.append(joinedNb)
                                joinedlistNeighbors = newNb
                                cells_data.loc[cells_data['id'] == nb, 'processed'] = True                                
            
                maxDistance = 5
                d = 0
                while d <= maxDistance:                    
                    d += 1
                    if size <= maxBaronySize:
                        # check the neighbors of level 1
                        nb_lvl_d = dfDistance.loc[(dfDistance['tId'] == id) & (dfDistance['distance'] == d), 'neighbors'].tolist()
                        for strhNeighborList in nb_lvl_d:
                            eachNeighborList = ast.literal_eval(strhNeighborList)
                            for nb in eachNeighborList:
                                if size > maxBaronySize:
                                    break
                            else:
                                # Continue if the inner loop wasn't broken.
                                if (cells_data.loc[cells_data['id'] == nb, 'processed'].tolist()[0] == False):
                                    # Check if neighbor is water
                                    nbCellType = cells_data.loc[cells_data['id'] == nb, 'type'].tolist()[0]
                                    if nbCellType == 'ocean' or nbCellType == 'lake':                
                                        cells_data.loc[cells_data['id'] == nb, 'processed'] = True
                                    else:
                                        # Add neighbor to id
                                        size += 1
                                        biome.append(cells_data.loc[cells_data['id'] == nb, 'biome'].tolist()[0])
                                        realmIds.append(nb)
                                        # write to Distance as well
                                        nbCoords = cells_data.loc[cells_data['id'] == nb, 'coordinates'].tolist()[0]
                                        coordinates.append(nbCoords)
                                        nbNeighbors = cells_data.loc[cells_data['id'] == nb, 'neighbors'].tolist()[0]
                                        newEntryDistance = [nb, d+1, barony, id, nbCoords, str(nbNeighbors)]
                                        dfDistance.loc[len(dfDistance)] = newEntryDistance
                                        
                                        for nbnb in nbNeighbors:
                                            if nbnb not in joinedlistNeighbors and nbnb not in realmIds:
                                                joinedlistNeighbors.append(nbnb)
                                        neighbors = list(set(joinedlistNeighbors))
                                        neighbors = sorted(neighbors)        
                                        # clean up neighbors if required
                                        newNb = []
                                        for joinedNb in joinedlistNeighbors:
                                            if joinedNb not in realmIds:
                                                newNb.append(joinedNb)
                                        joinedlistNeighbors = newNb
                                        cells_data.loc[cells_data['id'] == nb, 'processed'] = True
                            if size > maxBaronySize:
                                # myLogging("I stop now - outer loop")
                                break
                        # return

                # if size <= maxBaronySize:
                    # myLogging(f"still not full {id} after {maxBaronySize} runs with an allowed distance of {maxDistance}")        
                    # myLogging("check for island")

                # Write entry to list
                realmIds = list(set(realmIds))
                realmIds = sorted(realmIds)
                newEntryProvinces = [newId, barony, size, str(realmIds), str(biome), str(coordinates), str(neighbors)]
                dfProvinces.loc[len(dfProvinces)] = newEntryProvinces
                cells_data.loc[cells_data['id'] == id, 'processed'] = True
                # if counter >= MAX_RUNS:
                #     break
    


    # Clean up Provinces
    myLogging("Clean up Provinces")
    for id in dfProvinces['id'].tolist():
        id_clean = False
        # check if a nb is already in the dfProvinces
        if dfProvinces.loc[dfProvinces['id'] == id, 'size'].tolist()[0] == 1:
            # Or look for neighbors to append to
            realmDict = dict(zip(dfProvinces['id'], dfProvinces['realmIds']))
            neighborList = dfDistance.loc[dfDistance['id'] == id, 'neighbors'].tolist()[0]
            neighborList= ast.literal_eval(neighborList)
            for nb in neighborList:
                if id_clean == False:
                    for province_id, realm_ids in realmDict.items():
                        realm_ids = ast.literal_eval(realm_ids)
                        if nb in realm_ids:
                            # Found a match, return the province id
                            # get a lot of values
                            index_to_drop = dfProvinces.loc[dfProvinces['id'] == id].index
                            oldBiome = cells_data.loc[cells_data['id'] == id, 'biome'].tolist()[0]
                            oldCoordinates = [cells_data.loc[cells_data['id'] == id, 'coordinates'].tolist()[0]]
                            oldNeighbors = cells_data.loc[cells_data['id'] == id, 'neighbors'].tolist()[0]
                            dfProvinces = dfProvinces.drop(index_to_drop)
                            myLogging(f"{province_id} has the province to add {id}")
                            
                            index_to_add = dfProvinces.loc[dfProvinces['id'] == province_id].index
                            provId = dfProvinces.loc[dfProvinces['id'] == province_id, 'id'].tolist()[0]
                            provSize = dfProvinces.loc[dfProvinces['id'] == province_id, 'size'].tolist()[0]
                            provRealmIds = dfProvinces.loc[dfProvinces['id'] == province_id, 'realmIds'].tolist()[0]
                            provBiome = dfProvinces.loc[dfProvinces['id'] == province_id, 'Biome'].tolist()[0]
                            provCoordinates = dfProvinces.loc[dfProvinces['id'] == province_id, 'Coordinates'].tolist()[0]
                            provNeighbors = dfProvinces.loc[dfProvinces['id'] == province_id, 'neighbors'].tolist()[0]

                            # Change in dfProvinces
                            provSize += 1
                            dfProvinces.loc[dfProvinces['id'] == province_id, 'size'] = provSize

                            provRealmIds = ast.literal_eval(provRealmIds)
                            provRealmIds.append(id)
                            dfProvinces.loc[dfProvinces['id'] == province_id, 'realmIds'] = str(provRealmIds)

                            provBiome = ast.literal_eval(provBiome)
                            provBiome.append(oldBiome)
                            dfProvinces.loc[dfProvinces['id'] == province_id, 'Biome'] = str(provBiome)

                            provCoordinates = ast.literal_eval(provCoordinates)
                            provCoordinates += oldCoordinates
                            dfProvinces.loc[dfProvinces['id'] == province_id, 'Coordinates'] = str(provCoordinates)

                            provNeighbors = ast.literal_eval(provNeighbors)
                            for nbnb in oldNeighbors:
                                    if nbnb not in provNeighbors and nbnb not in provRealmIds:
                                        provNeighbors.append(nbnb)
                            provNeighbors = sorted(provNeighbors)
                            dfProvinces.loc[dfProvinces['id'] == province_id, 'neighbors'] = str(provNeighbors)
                            
                            # Change in Distance as well
                            provTown = dfDistance.loc[dfDistance['id'] == province_id, 'nearest_town'].tolist()[0]
                            provTownId = dfDistance.loc[dfDistance['id'] == province_id, 'tId'].tolist()[0]
                            dfDistance.loc[dfDistance['id'] == id, 'nearest_town'] = provTown
                            dfDistance.loc[dfDistance['id'] == id, 'tId'] = provTownId
                            dfDistance.loc[dfDistance['id'] == id, 'distance'] = 99

                            id_clean = True

    # Delete the remaining provinces with size == 1
    myLogging("Delete the remaining provinces with size == 1")
    for id in dfProvinces['id'].tolist():
        # check if a nb is already in the dfProvinces
        if dfProvinces.loc[dfProvinces['id'] == id, 'size'].tolist()[0] == 1:
            index_to_drop = dfProvinces.loc[dfProvinces['id'] == id].index
            dfProvinces = dfProvinces.drop(index_to_drop)
            index_to_drop = dfDistance.loc[dfDistance['id'] == id].index
            dfDistance = dfDistance.drop(index_to_drop)

    # # Check for twins which might be close by >> TODO > move this up - 2 pieces should try to eat 2 pieces or 1 piece baronies
    # myLogging("Check for twins which might be close by")
    # for id in dfProvinces['id'].tolist():
    #     if dfProvinces.loc[dfProvinces['id'] == id, 'size'].tolist()[0] == 2:
    #         # refresh realm dict
    #         realmDict = dict(zip(dfProvinces['id'], dfProvinces['realmIds']))
    #         # loop neighbors of each realm and 
    #         realmIds = dfProvinces.loc[dfProvinces['id'] == id, 'realmIds'].tolist()[0]
    #         realmIds = ast.literal_eval(realmIds)
    #         for rId in realmIds:
    #             # get neighbors
    #             neighborList = dfDistance.loc[dfDistance['id'] == rId, 'neighbors'].tolist()[0]
    #             neighborList= ast.literal_eval(neighborList)
    #             # loop neighbors
    #             for nb in neighborList:
    #                 # loop over dict
    #                 for province_id, realm_ids in realmDict.items():
    #                     realm_ids = ast.literal_eval(realm_ids)
    #                     if nb in realm_ids:
    #                         # CONTINUE HERE
    #                         provSize = dfProvinces.loc[dfProvinces['id'] == province_id, 'size'].tolist()[0]
    #                         # return
    #             # # check if neighbour has neighboruing realm
    #             # getRealmOfNeighbor = dfProvinces.loc[dfProvinces['id'] == id, 'realmIds'].tolist()

    # TODO: if barony still has only 1, move to neighbor

    # Check Provinces for too large > TODO
    for id in dfProvinces['id'].tolist():
        if dfProvinces.loc[dfProvinces['id'] == id, 'size'].tolist()[0] > maxBaronySize * 2:
            # Split the province
            print("split the province")

    # Clean Neighbors and group Biomes
    myLogging("Clean Neighbors and group Biomes")
    print(dfProvinces)
    dfProvinces['neighbors'] = dfProvinces['neighbors'].apply(ast.literal_eval) #convert to list type
    dfProvinces['Biome'] = dfProvinces['Biome'].apply(ast.literal_eval) #convert to list type
    biomesDict = dict()    
    for id in dfProvinces['id'].tolist():
        # Clean Neighbors first
        nbList = getNeighbors(dfProvinces, id)
        newNeighbors = []
        realmIds = dfProvinces.loc[dfProvinces['id'] == id, 'realmIds'].tolist()[0]
        realmIds = ast.literal_eval(realmIds)
        for nId in nbList:
            if nId not in realmIds:
                newNeighbors.append(nId)
        dfProvinces.loc[dfProvinces['id'] == id, 'neighbors'] = str(newNeighbors)        
        # Group Biomes
        biomesList = dfProvinces.loc[dfProvinces['id'] == id, 'Biome'].tolist()[0]
        if isinstance(biomesList, int):
            biomesDict[id] = biomesList
        else:
            # biomesList = ast.literal_eval(biomesList)
            biomesOccurence = Counter(biomesList)   # Counter will create an ordered list of biomes items
            myBiomesId = 0
            for key, value in biomesOccurence.items():
                myBiomesId = key
                break   # after first item, we can exit
            biomesDict[id] = myBiomesId
    dfProvinces["Biome"] = dfProvinces["id"].apply(lambda x: biomesDict.get(x))        

    myLogging("Finished - saving now...")
    # print(dfDistance)
    dfDistance.to_excel(bfs_distance_file, index=False)
    # print(dfProvinces)
    dfProvinces.to_excel(def_baronies_file, index=False)
    myLogging("ok")


def calculateCounties(maxCountySize, def_baronies_file, def_counties_file):
    myLogging("Calculating Counties...")
    dfBaronies = pd.read_excel(def_baronies_file)
    dfBaronies['realmIds'] = dfBaronies['realmIds'].apply(ast.literal_eval) #convert to list type
    dfBaronies['neighbors'] = dfBaronies['neighbors'].apply(ast.literal_eval) #convert to list type    
    dfBaronies['processed'] = dfBaronies['id'].apply(lambda x: False)       # add an indicator whether the cell has been processed    

    dfCounties = pd.DataFrame(columns=['id', 'County', 'countySize', 'realmIds', 'neighbors'])
    # dfCounties = pd.DataFrame(columns=['countyId', 'countyName', 'countySize'])

    # Loop over Barony Ids
    for id in dfBaronies['id'].tolist():
        # check if cell has been processed already (e.g. as a neighbor)
        isProcessedCell = dfBaronies.loc[dfBaronies['id'] == id, 'processed'].tolist()[0]
        if isProcessedCell == False:
            # not processed yet - create new County
            myLogging(f"County Processing started for Id {id}")
            # get Data from barony
            newId = id
            countyName = dfBaronies.loc[dfBaronies['id'] == id, 'Barony'].tolist()[0]
            countyName = "C_" + countyName
            # check if name already exists
            cNameExists = dfCounties.loc[dfCounties['County'] == countyName, 'id'].tolist()
            if len(cNameExists) > 0:
                # create a new name
                countyName = countyName + '-1'
            countySize = 1            
            realmIds = getRealmIds(dfBaronies, id)
            neighbors = getNeighbors(dfBaronies, id)
            newEntryCounties = [newId, countyName, countySize, str(realmIds), str(neighbors)]
            dfCounties.loc[len(dfCounties)] = newEntryCounties
            # TODO: add Religion from cellsData ?
            
            # get neighbors
            for nId in neighbors:                
                # check max size
                if countySize < maxCountySize:                    
                    # check if neighboring cell is part of another realm
                    neighborBaronyId = getProvinceIdFromRealmIds(dfBaronies, nId)
                    if not neighborBaronyId is None and neighborBaronyId != id:
                        # check if neighbor is already used
                        neighborProcessed = dfBaronies.loc[dfBaronies['id'] == neighborBaronyId, 'processed'].tolist()[0]
                        if neighborProcessed == False:
                            # now 
                            countySize += 1
                            dfCounties.loc[dfCounties['id'] == id, 'countySize'] = countySize

                            newRealm = getRealmIds(dfBaronies, neighborBaronyId)
                            for rId in newRealm:
                                if rId not in realmIds:
                                    realmIds.append(rId)
                            realmIds = sorted(realmIds)
                            dfCounties.loc[dfCounties['id'] == id, 'realmIds'] = str(realmIds)

                            nbOfNeighbor = getNeighbors(dfBaronies, neighborBaronyId)
                            currentNeighbors = getNeighbors(dfBaronies, id)
                            for nbnb in nbOfNeighbor:
                                if nbnb not in currentNeighbors:
                                    currentNeighbors.append(nbnb)
                            currentNeighbors = sorted(currentNeighbors)
                            dfCounties.loc[dfCounties['id'] == id, 'neighbors'] = str(currentNeighbors)
                            # Neighbor processed
                            dfBaronies.loc[dfBaronies['id'] == neighborBaronyId, 'processed'] = True

            dfBaronies.loc[dfBaronies['id'] == id, 'processed'] = True
    
    # Loop finished once
    # Clean neighbors
    myLogging("Clean neighbors Counties...")
    dfCounties['neighbors'] = dfCounties['neighbors'].apply(ast.literal_eval) #convert to list type
    for id in dfCounties['id'].tolist():
        # Clean Neighbors first
        nbList = getNeighbors(dfCounties, id)
        newNeighbors = []
        realmIds = dfCounties.loc[dfCounties['id'] == id, 'realmIds'].tolist()[0]
        realmIds = ast.literal_eval(realmIds)
        for idx, nId in enumerate(nbList):
            if nId not in realmIds:
                newNeighbors.append(nId)
        dfCounties.loc[dfCounties['id'] == id, 'neighbors'] = str(newNeighbors) 

    # Check if County 

    # print(dfBaronies)
    dfCounties.to_excel(def_counties_file, index=False)


def calculateDuchies(maxDuchySize, def_counties_file, def_duchies_file):
    myLogging("Calculating Duchies...")
    dfCounties = pd.read_excel(def_counties_file)
    dfCounties['realmIds'] = dfCounties['realmIds'].apply(ast.literal_eval) #convert to list type
    dfCounties['neighbors'] = dfCounties['neighbors'].apply(ast.literal_eval) #convert to list type    
    dfCounties['processed'] = dfCounties['id'].apply(lambda x: False)       # add an indicator whether the cell has been processed    

    dfDuchies = pd.DataFrame(columns=['id', 'Duchy', 'duchySize', 'realmIds', 'neighbors'])
    # dfDuchies = pd.DataFrame(columns=['countyId', 'countyName', 'countySize'])

    # Loop over County Ids
    for id in dfCounties['id'].tolist():
        # check if cell has been processed already (e.g. as a neighbor)
        isProcessedCell = dfCounties.loc[dfCounties['id'] == id, 'processed'].tolist()[0]
        if isProcessedCell == False:
            # not processed yet - create new duchy
            myLogging(f"Duchy Processing started for Id {id}")
            # get Data from barony
            newId = id
            duchyName = dfCounties.loc[dfCounties['id'] == id, 'County'].tolist()[0]
            duchyName = "D_" + duchyName
            # check if name already exists
            dNameExists = dfDuchies.loc[dfDuchies['Duchy'] == duchyName, 'id'].tolist()
            if len(dNameExists) > 0:
                # create a new name
                duchyName = duchyName + '-1'
            duchyySize = 1            
            realmIds = getRealmIds(dfCounties, id)
            neighbors = getNeighbors(dfCounties, id)
            newEntryCounties = [newId, duchyName, duchyySize, str(realmIds), str(neighbors)]
            dfDuchies.loc[len(dfDuchies)] = newEntryCounties
            # get neighbors
            for nId in neighbors:                
                # check max size
                if duchyySize < maxDuchySize:                    
                    # check if neighboring cell is part of another realm
                    neighborCountyId = getProvinceIdFromRealmIds(dfCounties, nId)
                    if not neighborCountyId is None and neighborCountyId != id:
                        # check if neighbor is already used
                        neighborProcessed = dfCounties.loc[dfCounties['id'] == neighborCountyId, 'processed'].tolist()[0]
                        if neighborProcessed == False:
                            # now 
                            duchyySize += 1
                            dfDuchies.loc[dfDuchies['id'] == id, 'duchySize'] = duchyySize

                            newRealm = getRealmIds(dfCounties, neighborCountyId)
                            for rId in newRealm:
                                if rId not in realmIds:
                                    realmIds.append(rId)
                            realmIds = sorted(realmIds)
                            dfDuchies.loc[dfDuchies['id'] == id, 'realmIds'] = str(realmIds)
                            
                            nbOfNeighbor = getNeighbors(dfCounties, neighborCountyId)
                            currentNeighbors = getNeighbors(dfCounties, id)
                            for nbnb in nbOfNeighbor:
                                if nbnb not in currentNeighbors:
                                    currentNeighbors.append(nbnb)
                            currentNeighbors = sorted(currentNeighbors)
                            dfDuchies.loc[dfDuchies['id'] == id, 'neighbors'] = str(currentNeighbors)
                            # Neighbor processed
                            dfCounties.loc[dfCounties['id'] == neighborCountyId, 'processed'] = True

            dfCounties.loc[dfCounties['id'] == id, 'processed'] = True
    # Loop finished once
    # Clean neighbors
    myLogging("Clean neighbors Duchies...")
    dfDuchies['neighbors'] = dfDuchies['neighbors'].apply(ast.literal_eval) #convert to list type
    for id in dfDuchies['id'].tolist():
        # Clean Neighbors first
        nbList = getNeighbors(dfDuchies, id)
        newNeighbors = []
        realmIds = dfDuchies.loc[dfDuchies['id'] == id, 'realmIds'].tolist()[0]
        realmIds = ast.literal_eval(realmIds)
        for idx, nId in enumerate(nbList):
            if nId not in realmIds:
                newNeighbors.append(nId)
        dfDuchies.loc[dfDuchies['id'] == id, 'neighbors'] = str(newNeighbors) 

    # Dump to Excel
    dfDuchies.to_excel(def_duchies_file, index=False)


def calculateKingdoms(maxKingdomSize, def_duchies_file, def_kingdoms_file):
    myLogging("Calculating Kingdoms...")
    dfDuchies = pd.read_excel(def_duchies_file)
    dfDuchies['realmIds'] = dfDuchies['realmIds'].apply(ast.literal_eval) #convert to list type
    dfDuchies['neighbors'] = dfDuchies['neighbors'].apply(ast.literal_eval) #convert to list type    
    dfDuchies['processed'] = dfDuchies['id'].apply(lambda x: False)       # add an indicator whether the cell has been processed    

    dfKingdoms = pd.DataFrame(columns=['id', 'Kingdom', 'kingdomSize', 'realmIds', 'neighbors'])

    # Loop over County Ids
    for id in dfDuchies['id'].tolist():
        # check if cell has been processed already (e.g. as a neighbor)
        isProcessedCell = dfDuchies.loc[dfDuchies['id'] == id, 'processed'].tolist()[0]
        if isProcessedCell == False:
            # not processed yet - create new Kingdom
            myLogging(f"Kingdom Processing started for Id {id}")
            # get Data from barony
            newId = id
            kingdomName = dfDuchies.loc[dfDuchies['id'] == id, 'Duchy'].tolist()[0]
            kingdomName = "K_" + kingdomName
            # check if name already exists
            kNameExists = dfKingdoms.loc[dfKingdoms['Kingdom'] == kingdomName, 'id'].tolist()
            if len(kNameExists) > 0:
                # create a new name
                kingdomName = kingdomName + '-1'
            kingdomSize = 1            
            realmIds = getRealmIds(dfDuchies, id)
            neighbors = getNeighbors(dfDuchies, id)
            newEntryKingdoms = [newId, kingdomName, kingdomSize, str(realmIds), str(neighbors)]
            dfKingdoms.loc[len(dfKingdoms)] = newEntryKingdoms
            # get neighbors
            for nId in neighbors:                
                # check max size
                if kingdomSize < maxKingdomSize:                    
                    # check if neighboring cell is part of another realm
                    neighborDuchyId = getProvinceIdFromRealmIds(dfDuchies, nId)
                    if not neighborDuchyId is None and neighborDuchyId != id:                        
                        # check if neighbor is already used
                        neighborProcessed = dfDuchies.loc[dfDuchies['id'] == neighborDuchyId, 'processed'].tolist()[0]
                        if neighborProcessed == False:
                            # now 
                            kingdomSize += 1
                            dfKingdoms.loc[dfKingdoms['id'] == id, 'kingdomSize'] = kingdomSize
                            
                            newRealm = getRealmIds(dfDuchies, neighborDuchyId)
                            for rId in newRealm:
                                if rId not in realmIds:
                                    realmIds.append(rId)
                            realmIds = sorted(realmIds)
                            dfKingdoms.loc[dfKingdoms['id'] == id, 'realmIds'] = str(realmIds)
                            
                            nbOfNeighbor = getNeighbors(dfDuchies, neighborDuchyId)
                            currentNeighbors = getNeighbors(dfDuchies, id)
                            for nbnb in nbOfNeighbor:
                                if nbnb not in currentNeighbors:
                                    currentNeighbors.append(nbnb)
                            currentNeighbors = sorted(currentNeighbors)
                            dfKingdoms.loc[dfKingdoms['id'] == id, 'neighbors'] = str(currentNeighbors)
                            # Neighbor processed
                            dfDuchies.loc[dfDuchies['id'] == neighborDuchyId, 'processed'] = True

            dfDuchies.loc[dfDuchies['id'] == id, 'processed'] = True
    # Loop finished once
    # Clean neighbors
    myLogging("Clean neighbors Kingdoms...")
    dfKingdoms['neighbors'] = dfKingdoms['neighbors'].apply(ast.literal_eval) #convert to list type
    for id in dfKingdoms['id'].tolist():
        # Clean Neighbors first
        nbList = getNeighbors(dfKingdoms, id)
        newNeighbors = []
        realmIds = dfKingdoms.loc[dfKingdoms['id'] == id, 'realmIds'].tolist()[0]
        realmIds = ast.literal_eval(realmIds)
        for idx, nId in enumerate(nbList):
            if nId not in realmIds:
                newNeighbors.append(nId)
        dfKingdoms.loc[dfKingdoms['id'] == id, 'neighbors'] = str(newNeighbors) 
    # Dump to Excel
    dfKingdoms.to_excel(def_kingdoms_file, index=False)

def createFinalOutput(provinceDef_file, def_counties_file, def_duchies_file, def_kingdoms_file, updated_file, final_file):
    myLogging("Create final output...")
    dfProvOutput = pd.read_excel(provinceDef_file)
    # rename columns
    dfProvOutput.columns.values[0] = '0'
    dfProvOutput.columns.values[1] = 'id'
    dfProvOutput['id'] = dfProvOutput['Cell ID']
    dfProvOutput.drop([6])
    # dfProvOutput.columns.values[6] = 'empty'
    dfProvOutput['population'] = ""
    dfProvOutput['Empire'] = dfProvOutput['Nearest Town'].apply(lambda x: False)       # add an indicator whether the cell has been processed    
    dfProvOutput['Kingdom'] = dfProvOutput['Nearest Town'].apply(lambda x: False)       # add an indicator whether the cell has been processed    
    dfProvOutput['Duchy'] = dfProvOutput['Nearest Town'].apply(lambda x: False)       # add an indicator whether the cell has been processed    
    dfProvOutput['County'] = dfProvOutput['Nearest Town'].apply(lambda x: False)       # add an indicator whether the cell has been processed    
    dfProvOutput['Culture'] = dfProvOutput['Nearest Town'].apply(lambda x: False)       # add an indicator whether the cell has been processed    
    dfProvOutput['Religion'] = dfProvOutput['Nearest Town'].apply(lambda x: False)       # add an indicator whether the cell has been processed   
    # dfProvOutput['Religion'] = dfProvOutput['id'].apply(lambda x: dfReligion.loc[dfReligion['id'] == x, 'Religion'])
    # columns created

    # Get County, Duchy and Kingdoms Data
    dfBarnonies = pd.read_excel(def_counties_file)
    dfBarnonies['realmIds'] = dfBarnonies['realmIds'].apply(ast.literal_eval) #convert to list type
    dfCounties = pd.read_excel(def_counties_file)
    dfCounties['realmIds'] = dfCounties['realmIds'].apply(ast.literal_eval) #convert to list type
    dfDuchies = pd.read_excel(def_duchies_file)
    dfDuchies['realmIds'] = dfDuchies['realmIds'].apply(ast.literal_eval) #convert to list type
    dfKingdoms = pd.read_excel(def_kingdoms_file)
    dfKingdoms['realmIds'] = dfKingdoms['realmIds'].apply(ast.literal_eval) #convert to list type
    dfReligion = pd.read_excel(updated_file)
    
    print(dfProvOutput)
    print(dfCounties)
    print(dfDuchies)
    print(dfKingdoms)
    # Loop through output once
    for id in dfProvOutput['id'].tolist():
        countyId = None
        duchyId = None
        kingdomId = None

        myLogging(f"Finalising {id}")
        countyId = getProvinceIdFromRealmIds(dfCounties, id)
        if not countyId is None:
            myLogging(f"{id} has County {countyId}")
            countyName = dfCounties.loc[dfCounties['id'] == countyId, 'County'].tolist()[0]
            dfProvOutput.loc[dfProvOutput['id'] == id, 'County'] = countyName

        duchyId = getProvinceIdFromRealmIds(dfDuchies, id)
        if not duchyId is None:
            duchyName = dfDuchies.loc[dfDuchies['id'] == duchyId, 'Duchy'].tolist()[0]
            dfProvOutput.loc[dfProvOutput['id'] == id, 'Duchy'] = duchyName
        
        myLogging(f"{id} has County {countyId}")
        kingdomId = getProvinceIdFromRealmIds(dfKingdoms, id)
        if not kingdomId is None:
            kingdomName = dfKingdoms.loc[dfKingdoms['id'] == kingdomId, 'Kingdom'].tolist()[0]
            dfProvOutput.loc[dfProvOutput['id'] == id, 'Kingdom'] = kingdomName


    dfProvOutput['Empire'] = dfProvOutput['Kingdom']
    dfProvOutput['Culture'] = dfProvOutput['Kingdom']
    dfProvOutput['Religion'] = dfProvOutput['Kingdom']
    # print(dfProvOutput)
    dfProvOutput.to_excel(final_file, index=False)




# calculateBaronies(maxBaronySize, cells_data_file, bfs_distance_file, def_baronies_file)
# calculateCounties(maxCountySize, def_baronies_file, def_counties_file)
# calculateDuchies(maxDuchySize, def_counties_file, def_duchies_file)
# calculateKingdoms(maxKingdomSize, def_duchies_file, def_kingdoms_file)

# BFS.colorRandomBFS(bfs_distance_file)
# BFS.provinceMapBFS(bfs_distance_file, 150, output_png) 

# BFS.extractBFS(bfs_distance_file, provinceDef_file)   # nothing changed

# createFinalOutput(provinceDef_file, def_counties_file, def_duchies_file, def_kingdoms_file, updated_file, final_file)



# BFS.BaronyId(combined_data_file, provinceDef_file)  # nothing changed
# BFS.bfs_calcType(biomes_file, cells_data_file, provinceDef_file)      # not finished yet

# BFS.bfs_putNeighborsToTowns(cells_data_file, bfs_distance_file_with_neighbors, provinceDef_file, provinceDef_file_transformed)

# BFS.ProvData(updated_file, provinceDef_file_transformed, provinceDef_file_transformed)  # nothing changed
# BFS.cOrder(provinceDef_file_transformed)    # adjusted

# BFS.assignEmpireAndDuchyId(provinceDef_file_transformed, duchyDef_file)

# TODO: maybe we have to delete columns to fit with INTERFACE to map gen
# TODO!!
# BFS.finalorder(duchyDef_file, final_file)