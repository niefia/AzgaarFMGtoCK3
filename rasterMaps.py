import json
import itertools
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import hextorgb
import os
import pandas as pd
import ast
from PIL import Image
import numpy as np
import random
import riverGen

# Declare global variables
scale_factor = None
min_x = None
max_x = None
min_y = None
max_y = None
x_offset = None
y_offset = None


def calculate_scaling_variables(geojson_file):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset, min_height, max_height

    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]

    # Determine the maximum and minimum values of x and y coordinates
    min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)

    # Determine the width and height of the image
    img_width = 8192
    img_height = 4096

    # Calculate the scaling factor to fit the polygons in the output image
    scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)
    print("scalefactor:", scale_factor)

    # Calculate the x and y offsets to center the polygons in the output image
    x_offset = (img_width - (max_x - min_x) / scale_factor) / 2
    y_offset = (img_height - (max_y - min_y) / scale_factor) / 2

def rivermap(output_dir):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset
    scalee_factor = 35


    riverGen.generate_river_files(output_dir,scalee_factor, min_x, max_x, min_y, max_y, x_offset, y_offset)




def heightmapAutoScaledfunc(geojson_file, output_file):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset

    # Calculate scaling variables if not already calculated
    if scale_factor is None:
        calculate_scaling_variables(geojson_file)

    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]

    # Create an L mode image for the L version of the heightmap
    img_l = Image.new("L", (8192, 4096))
    draw_l = ImageDraw.Draw(img_l)

    img = Image.new("I;16", (8192, 4096))
    draw = ImageDraw.Draw(img)

    heights = [poly["properties"]["height"] for poly in polygs]
    min_height = min(heights)
    max_height = max(heights)

    for poly in polygs:
        height = poly["properties"]["height"]
        if height < 0:
            color = 0
        else:
            normalized_height = (height - min_height) * 255 / (max_height - min_height)
            color = int(normalized_height)

            # Clamp the color to the valid range for an L mode image
            color = max(min(color, 255), 0)

        for coords in poly["geometry"]["coordinates"]:
            # Scale the coordinates based on the size of the image and center them
            coords = [[(coord[0] - min_x) / scale_factor + x_offset,
                       (coord[1] - min_y) / scale_factor + y_offset] for coord in coords]
            draw.polygon(list(itertools.chain(*coords)), fill=color)

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

#heightmapAutoScaledfunc("output.geojson",  "heightmap.png")

def heightmap_blur_and_noise(output_dir,blur_amount):
    import numpy as np
    from scipy.ndimage import gaussian_filter
    from PIL import Image, ImageFilter
    if blur_amount == 0:
        return  # skip the function if no blur chosen

    # Define Perlin noise function
    def noise(x, y):
        n = int(x + y * 57)
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)


    # Load the image
    heightmap_file = os.path.join(output_dir, "map_data/heightmap.png")
    img = Image.open(heightmap_file)
    output_file_for_papermap= os.path.join(output_dir, "map_data/heightmap_for_paper.png")
    img.save(output_file_for_papermap, "PNG")
    # Convert the image to a numpy array
    arr = np.array(img, dtype=np.float32)

    # Apply Gaussian blur to the array
    arr = gaussian_filter(arr, sigma=blur_amount)

    # Add Perlin noise to the array
    for i in range(arr.shape[0]):
        print(i)
        for j in range(arr.shape[1]):
            arr[i][j] += 0.10 * noise(i/50.0, j/50.0)
            #10% opacity noise layer

    # Convert the array back to an image
    img = Image.fromarray(arr.astype(np.uint16))

    # Save the blurred image with Perlin noise to output file
    output_file = os.path.join(output_dir, "map_data/heightmap.png")
    img.save(output_file, "PNG")



#heightmap_blur_and_noise()


#Uses curve and theshold to generate biome masks from the heightmap
def heightmap_to_mountain_biome(output_dir):
    for i, curve_value in enumerate([2.0, 2.2, 3.0, 0.5, 0.5, 1.5,4.0]):#numbers are curve values for each mask, these essentially define the "intensity" of the texture mask
        # Load the image
        heightmap_file = os.path.join(output_dir, "map_data/heightmap.png")
        img = Image.open(heightmap_file)
        # Convert the image to a NumPy array
        arr = np.array(img)
        # Set the upper and lower thresholds based on the terrain type
        if i == 0:  # hills rocky
            lower_threshold = 0.32
            upper_threshold = 0.75
        elif i == 1:  # mountains
            lower_threshold = 0.4
            upper_threshold = 1.0
        elif i == 2: #snow mountains
            lower_threshold = 0.7
            upper_threshold = 1.0
        elif i == 3: #beach
            # Invert the array for the beach mask
            # Array must be inverted to allow the sea to be textured, as generating using threshold where sea would have been included still left sea values as black, not white
            arr = 65535 - arr
            lower_threshold = 0.0
            upper_threshold = 1.0
            lower_threshold2 = 0.89
            upper_threshold2 = 1.0
        elif i == 4: #coastline cliff
            lower_threshold = 0.0
            upper_threshold = 0.1
        elif i == 5: #hills green
            lower_threshold = 0.2
            upper_threshold = 0.40
        elif i == 6: #snow
            lower_threshold = 0.99
            upper_threshold = 1.0

        # Apply the lower and upper thresholds
        arr[arr < lower_threshold * 65535] = 0
        arr[arr > upper_threshold * 65535] = 0

        if i == 3:
            arr[arr < lower_threshold2 * 65535] = 0
            arr[arr > upper_threshold2 * 65535] = 0

        # Apply a curve filter with the current curve value
        arr = (arr / 65535) ** curve_value * 65535

        # Rescale the pixel values to the range of 0-255
        arr = (arr / 256).astype(np.uint8)

        # Convert the NumPy array back to an image
        img = Image.fromarray(arr)

        # Save the image with a different name for each iteration
        output_folder = os.path.join(output_dir,"gfx/map/terrain")

        if not os.path.exists(output_folder):   
            os.makedirs(output_folder)

        img.save(os.path.join(output_folder,f"{'hills_01_rocks' if i == 0 else 'mountain_02' if i == 1 else 'mountain_02_c_snow' if i == 2 else 'beach_02' if i == 3 else 'coastline_cliff_grey' if i == 4 else 'hills_01' if i == 5 else 'snow'}_mask.png"))


#heightmap_to_mountain_biome()






def gradient_map(output_dir):

    # Load the heightmap image as a NumPy array
    heightmap_file = os.path.join(output_dir, "map_data/heightmap.png")

    # Compute the gradient map using NumPy's gradient function
    gx, gy = np.gradient(heightmap)
    gradient = np.sqrt(gx**2 + gy**2)

    # Normalize the gradient map to the range [0, 255]
    gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min()) * 255
    gradient = gradient.astype(np.uint8)

    # Save the gradient map as an image

    Image.fromarray(gradient).save(os.path.join(output_dir,'gradient.png'))


#gradient_map()


def mountain_multiply_by_gradient ():
    # Load the heightmap image as a NumPy array
    heightmap = np.array(Image.open('heightmap.png'))

    # Compute the gradient map using NumPy's gradient function
    gx, gy = np.gradient(heightmap)
    gradient = np.sqrt(gx**2 + gy**2)

    # Normalize the gradient map to the range [0, 65535]
    gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min()) * 65535
    gradient = gradient.astype(np.uint16)

    # Load the mountains mask image as a NumPy array and scale it to the range [0, 1]
    mountain_mask = np.array(Image.open('mountain_02_mask.png').convert('L'))
    mountain_mask = mountain_mask / 255

    # Multiply the gradient map by the mountains mask image
    result = gradient * mountain_mask
    result = (result / 65535 * 255).astype(np.uint8)

    # Increase the brightness of the result by a factor of 1.5
    result = np.clip(result * 3.5, 0, 255).astype(np.uint8)

    # Save the result as an image
    Image.fromarray(result).save('result.png')




def generate_tree_mask_from_biome_mask_with_perlin_noise():
    #this functions slow :( could use pregenerated noise?
    from noise import snoise2  # Perlin noise function

    # Load forest texture mask
    forest_mask = np.array(Image.open('forest_pine_01_mask.png').convert('L'))

    # Define noise parameters
    scale = 200  # determines the roughness of the noise
    octaves = 8  # determines the level of detail in the noise
    persistence = 0.3  # determines how much each octave contributes to the overall shape
    lacunarity = 2.5  # determines how quickly the frequency increases with each octave

    # Generate Perlin noise map
    tree_density_map = np.zeros_like(forest_mask)
    height, width = tree_density_map.shape
    for y in range(height):
        for x in range(width):
            noise_val = snoise2(x/scale, y/scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
            tree_density_map[y, x] = forest_mask[y, x] * (1 + noise_val) / 2

    # Apply a curve filter with the current curve value
    tree_density_map = (tree_density_map / 255) ** 4 * 255

    # Save tree density map as an image
    tree_density_map = tree_density_map.astype(np.uint8)
    Image.fromarray(tree_density_map).save('tree_density_map.png')


















def provinceMapBFSAutoScaled(file_path, output_folder):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset
    # read the Excel file
    df = pd.read_excel(file_path)

    # extract coordinates and colors
    coords_str = df['coordinates'].values
    colors_str = df['color'].values
    coords = []
    colors = []
    for coord_str, color_str in zip(coords_str, colors_str):
        coord_list = ast.literal_eval(coord_str)
        coord_list = [[float(x), float(y)] for x, y in coord_list[0]]
        coords.append(coord_list)
        colors.append(color_str)

    # Determine the width and height of the image
    img_width = 8192
    img_height = 4096

    # set up image
    img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # draw each polygon with scaling factor applied
    for coord, color in zip(coords, colors):

        # calculate the pixel value for each coordinate, with scaling factor applied and centered at the center_px
        coord_px = [(int((x - min_x) / scale_factor + x_offset),
                     int((y - min_y) / scale_factor + y_offset)) for x, y in coord]

        # draw polygon
        rgbcolor = hextorgb.bfs_hex_to_rgb(color)
        draw.polygon(coord_px, fill=rgbcolor, outline=None)

    # save image
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_folder)











#provinceMapBFSAutoScaled('BFSoutput.xlsx', 'provincesAS.png')





def heightmap(geojson_file, output_file, scaling_factor):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    img = Image.new("I;16", (img_width, img_height))
    draw = ImageDraw.Draw(img)

    heights = [poly["properties"]["height"] for poly in polygs]
    min_height = min(heights)
    max_height = max(heights)

    for poly in polygs:
        height = poly["properties"]["height"]
        if height < 0:
            color = 0
        else:
            normalized_height = (height - min_height) * 255 / (max_height - min_height)
            color = int(normalized_height)
        for coords in poly["geometry"]["coordinates"]:
            coords = [[(coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2)] for coord in coords]
            draw.polygon(list(itertools.chain(*coords)), fill=color)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

#AutoScaled Version of Heightmap
def heightmapAutoScaled(geojson_file, output_file):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]

    # Determine the maximum and minimum values of x and y coordinates
    min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)

    # Determine the width and height of the image
    img_width = 8192
    img_height = 4096

    # Calculate the scaling factor to fit the polygons in the output image
    scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)
    print("scalefactor:", scale_factor)

    # Calculate the x and y offsets to center the polygons in the output image
    x_offset = (img_width - (max_x - min_x) / scale_factor) / 2
    y_offset = (img_height - (max_y - min_y) / scale_factor) / 2

    img = Image.new("I;16", (img_width, img_height))
    draw = ImageDraw.Draw(img)

    heights = [poly["properties"]["height"] for poly in polygs]
    min_height = min(heights)
    max_height = max(heights)

    for poly in polygs:
        height = poly["properties"]["height"]
        if height < 0:
            color = 0
        else:
            normalized_height = (height - min_height) * 255 / (max_height - min_height)
            color = int(normalized_height)
        for coords in poly["geometry"]["coordinates"]:
            # Scale the coordinates based on the size of the image and center them
            coords = [[(coord[0] - min_x) / scale_factor + x_offset,
                       (coord[1] - min_y) / scale_factor + y_offset] for coord in coords]
            draw.polygon(list(itertools.chain(*coords)), fill=color)

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")


#heightmapAutoScaled("output.geojson",  "heightmap.png")





def provincesCells(input_file, output_file, scaling_factor):
    with open(input_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    img = Image.new("RGB", (img_width, img_height))
    draw = ImageDraw.Draw(img)
    for poly in polygs:
        color = hextorgb.hex_to_rgb(poly["properties"]["color"])
        for coords in poly["geometry"]["coordinates"]:
            coords = [ [ (coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2) ] for coord in coords ]
            draw.polygon(list(itertools.chain(*coords)), fill=color + (255,))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    img.save(output_file, "PNG")







def biomes(geojson_file, output_dir, scaling_factor):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    all_biomes = set([poly["properties"]["biome"] for poly in polygs])

    for biome in all_biomes:
        img = Image.new("L", (img_width, img_height), 0)
        draw = ImageDraw.Draw(img)

        for poly in polygs:
            if poly["properties"]["biome"] == biome:
                for coords in poly["geometry"]["coordinates"]:
                    coords = [[(coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2)] for coord in coords]
                    draw.polygon(list(itertools.chain(*coords)), fill=255)

        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.save(f"{output_dir}/biome_{biome}.png", "PNG")

def biomesAutoScaled(geojson_file, output_dir):
    # Load the GeoJSON file
    with open(geojson_file, "r") as f:
        data = json.load(f)

    # Extract the polygons from the GeoJSON file
    polygs = data["features"]

    # Define the dimensions of the output image
    img_width, img_height = 8192, 4096

    # Determine the maximum and minimum values of x and y coordinates
    min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)

    # Calculate the scaling factor to fit the polygons in the output image
    scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)

    # Calculate the x and y offsets to center the polygons in the output image
    x_offset = (img_width - (max_x - min_x) / scale_factor) / 2
    y_offset = (img_height - (max_y - min_y) / scale_factor) / 2

    # Loop over all biomes in the data and create a separate image for each biome
    all_biomes = set([poly["properties"]["biome"] for poly in polygs])
    for biome in all_biomes:
        # Create a new image for this biome
        img = Image.new("L", (img_width, img_height), 0)
        draw = ImageDraw.Draw(img)

        # Loop over all polygons in the data and draw the ones that belong to this biome
        for poly in polygs:
            if poly["properties"]["biome"] == biome:
                for coords in poly["geometry"]["coordinates"]:
                    # Scale the coordinates based on the size of the image and center them
                    coords = [[(coord[0] - min_x) / scale_factor + x_offset,
                               (coord[1] - min_y) / scale_factor + y_offset] for coord in coords]
                    # Draw the polygon on the image
                    draw.polygon(list(itertools.chain(*coords)), fill=255)

        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # Apply a Gaussian blur to the image
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        # Save the biome image with the same filename as the heightmap image
        img.save(f"{output_dir}/biome_{biome}.png", "PNG")




def paint_land_sea_mask(heightmap_file, output_file):
    """Takes in a heightmap file, paints land white and sea magenta, outputs a PIL image object."""

    img = Image.open(heightmap_file)
    img = img.convert('RGB')

    # converting to numpy array for faster processing
    color_array = np.array(img)
    red, green, blue = color_array.T  # Temporarily unpack the bands for readability

    # Replace sea with magenta, land with white
    sea_pixels = ((red == 0) & (blue == 0) & (green == 0)).T
    color_array[sea_pixels] = (0, 0, 0)  # replacing sea pixels
    color_array[~sea_pixels] = (255, 255, 255)  # replacing "not-sea" pixels

    img = Image.fromarray(color_array)
    img.save(output_file, "PNG")






def create_masked_image(black_image_path, white_image_path, mask_image_path, output_image_path):
    # Load the black and white images
    black_image = np.array(Image.open(black_image_path))
    white_image = np.array(Image.open(white_image_path))

    # Load the mask image as a numpy array
    mask_image = np.array(Image.open(mask_image_path))

    # Create a new array for the output image
    output_image = np.zeros_like(mask_image, dtype=np.uint8)

    # Mask the black and white images using the mask
    black_masked = black_image.copy()
    black_masked[mask_image[:, :, 0] == 255] = 0
    black_masked = black_masked[:, :, :3]  # remove alpha channel
    white_masked = white_image.copy()
    white_masked[mask_image[:, :, 0] == 0] = 0
    white_masked = white_masked[:, :, :3]  # remove alpha channel

    # Add a brown border outline where the white and black of the mask image touch
    mask = mask_image[:, :, 0]
    mask_left = np.hstack([mask[:, 1:], np.zeros((mask.shape[0], 1), dtype=np.uint8)])
    mask_right = np.hstack([np.zeros((mask.shape[0], 1), dtype=np.uint8), mask[:, :-1]])
    mask_top = np.vstack([mask[1:, :], np.zeros((1, mask.shape[1]), dtype=np.uint8)])
    mask_bottom = np.vstack([np.zeros((1, mask.shape[1]), dtype=np.uint8), mask[:-1, :]])
    border_mask = (mask != mask_left) | (mask != mask_right) | (mask != mask_top) | (mask != mask_bottom)
    output_image[border_mask] = [150, 75, 0]

    # Combine the masked images to create the output image
    output_image = output_image + black_masked + white_masked

    # Save the output image
    Image.fromarray(output_image).save(output_image_path)


def produce_outline(mask_image_path, output_image_path):
    # Load the mask image as a numpy array
    mask_image = np.array(Image.open(mask_image_path))

    # Create a new array for the output image
    output_image = np.zeros_like(mask_image, dtype=np.uint8)

    # Add a brown border outline where the white and black of the mask image touch
    mask = mask_image[:, :, 0]
    mask_left = np.hstack([mask[:, 1:], np.zeros((mask.shape[0], 1), dtype=np.uint8)])
    mask_right = np.hstack([np.zeros((mask.shape[0], 1), dtype=np.uint8), mask[:, :-1]])
    mask_top = np.vstack([mask[1:, :], np.zeros((1, mask.shape[1]), dtype=np.uint8)])
    mask_bottom = np.vstack([np.zeros((1, mask.shape[1]), dtype=np.uint8), mask[:-1, :]])
    border_mask = (mask != mask_left) | (mask != mask_right) | (mask != mask_top) | (mask != mask_bottom)
    output_image[border_mask] = [77, 55, 41]

    # Save the output image
    Image.fromarray(output_image).save(output_image_path)


def overlay_png_on_dds(png_filename, dds_filename, output_filename):
    # Open the png image and extract its non-black pixels
    png_image = Image.open(png_filename)
    png_pixels = png_image.load()
    png_width, png_height = png_image.size
    non_black_pixels = []
    for y in range(png_height):
        for x in range(png_width):
            if png_pixels[x, y] != (0, 0, 0):
                non_black_pixels.append((x, y))

    # Open the dds image and create a new image to hold the overlay
    dds_image = Image.open(dds_filename)
    overlay_image = Image.new("RGBA", dds_image.size, (0, 0, 0, 0))

    # Place the non-black pixels on the overlay
    overlay_pixels = overlay_image.load()
    for pixel in non_black_pixels:
        overlay_pixels[pixel[0], pixel[1]] = png_pixels[pixel[0], pixel[1]] + (255,)

    # Combine the overlay with the dds image and save the result
    result_image = Image.alpha_composite(dds_image.convert("RGBA"), overlay_image)
    result_image.save(output_filename)



#create_masked_image('sea_image.png', 'land_image.png', 'masksea.png', 'flatmap1.dds')

#produce_outline('masksea.png','flatmapBorder.png')

#overlay_png_on_dds('flatmapBorder.png','flatmap1.dds','flatmap.dds')

#biomesAutoScaled("output.geojson",  "biomes")


#heightmap("output.geojson", "map_data/heightmap.png", scaling_factor)
#provincesCells("output.geojson", "map_data/provinces.png", scaling_factor)
#biomes("output.geojson", "gfx/map/terrain/", scaling_factor)