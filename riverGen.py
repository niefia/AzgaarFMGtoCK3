import json
from PIL import Image, ImageDraw
import numpy as np
import sys

# set scaling factor
scaling_factor = 30
#scaling_factor = float(sys.argv[1])
# print the scaling factor
print("Scaling factor used is: " + str(scaling_factor))

# Constants for blue, greeen and magenta
blue = (0, 0, 255)
green = (0, 255, 0)
magenta = (255,0,128)
white = (255, 255, 255)
red = (255, 0, 0)

# Declare a debug variable
debug = True


def paint_land_sea(heightmap_file, output_file):
    """Takes in a heightmap file, paints land white and sea magenta, outputs a PIL image object."""

    img = Image.open(heightmap_file)
    img = img.convert('RGB')

    # converting to numpy array for faster processing
    color_array = np.array(img)
    red, green, blue = color_array.T  # Temporarily unpack the bands for readability

    # Replace sea with magenta, land with white
    sea_pixels = ((red == 0) & (blue == 0) & (green == 0)).T
    color_array[sea_pixels] = magenta  # replacing sea pixels
    color_array[~sea_pixels] = white  # replacing "not-sea" pixels

    img = Image.fromarray(color_array)
    img.save(output_file, "PNG")


def draw_rivers(landsea_image, rivers_geojson, output_file):
    """Implements the river-drawing algorithm, taking in a land-sea painted image and a river geojson file."""

    # load the painted land sea map
    img = Image.open(landsea_image)
    # Flip top to bottom for right coordinate alignment
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    # get image width and height
    img_width, img_height = img.size
    # Create an ImageDraw object to draw on the image
    draw = ImageDraw.Draw(img)

    # When drawing any river, monitor the number of magenta pixels that was detexted at river position.
    # If the river ends on a magenta, remove all but a few (offshore_runoff_pixel_length) pixels from the river,
    # to avoid offshore river overlaps.
    finished_on_magenta = False
    offshore_runoff_pixel_length = 3

    with open(rivers_geojson, "r") as riverData:
        data = json.load(riverData)

    # get rivers
    rivers = data["features"]

    print("Number of rivers: " + str(len(rivers)))
    for river in rivers:
        # We will process all rivers
        if river["properties"]:


            # For debug so that we can easier undertand what is going on
            # get river name
            river_name = river["properties"]["name"]
            #Get river type
            river_type = river["properties"]["type"]
            #Get river parent
            river_parent = river["properties"]["parent"]
            # Print the river name, type and parent ID to the console.
            print("Drawing river: " + river_name + " of type " + river_type + " with parent ID " + str(river_parent))

            flat_coords = np.array([item * scaling_factor for sublist in river["geometry"]["coordinates"]
                                    for item in sublist])
            centred_coords = flat_coords + np.tile([img_width / 2, img_height / 2], int(flat_coords.size / 2))
            centred_coords = centred_coords.reshape(int(len(centred_coords) / 2), 2)  # reshaping into 2-column array
            draw_coords = np.floor(centred_coords[0]).reshape(1, 2)  # first coordinates to add

            # Find the pixel coordinates of the river line
            for row in range(1, centred_coords[1:].shape[0]):
                new_coords = np.floor(centred_coords[row]).reshape(1, 2) # This is the 2d Array that holds the coordinates of the river line.
                # Print the river coordinates to the console if debug is true
                try:
                    #NOTE: new_coords can be outside the image, so we need to check for that
                    print("River coordinates: " + str(new_coords) +
                            " Existing pixel colour: " + str(img.getpixel((new_coords[0][0], new_coords[0][1]))))

                    if (np.abs(new_coords - draw_coords[-1]).sum(axis=1) >= 2)[0]:  # if both x and y coordinates jump
                        jump_coord = np.argmin(np.abs(draw_coords[-1] - centred_coords[row]))  # the closest of x or y
                        new_coords[0, jump_coord] = draw_coords[-1, jump_coord]
                        draw_coords = np.append(draw_coords, new_coords, axis=0)
                    elif (np.abs(new_coords - draw_coords[-1]).sum(axis=1) == 1)[0]:  # at least one of x or y moves
                        draw_coords = np.append(draw_coords, new_coords, axis=0)
                except IndexError:
                    # If the pixel is outside the image, remove the coordinate from new_coords
                    print("River coordinates: " + str(new_coords),
                      "IndexError: pixel is outside image " + str(img.size) +
                      " so it was skipped")


            #Trim any pixels that are outside the image
            draw_coords = draw_coords[draw_coords[:, 0] < img_width]
            draw_coords = draw_coords[draw_coords[:, 1] < img_height]

            #Print the draw coordinates to the console if debug is true
        #    if debug:
        #        print("The river have been determined to exist in the pixels: " + str(draw_coords))
            # We have the river coloured in, but not saved to the map, so now we need to do some error checking first.

            # Check if the last pixel in the river matches a magenta pixel on the original
            # get the last pixel i the river

            #Check that the river is not empty
            if len(draw_coords) == 0:
                # Print out an error message and continue to the next river
                print("=============================================")
                print("River is empty, skipping to next river")
                print("=============================================")
                continue

            last_pixel = draw_coords[-1]   #This is the last pixel in the river
            print("Last pixel in river: " + str(last_pixel))
            #Print image size to the console
            print("Image size: " + str(img.size))
            # If last pixle is outside the image. Show the image
            if last_pixel[0] > img.size[0] or last_pixel[1] > img.size[1]:

                raise ValueError("Last pixel in river is outside the image")

            #is the last pixel in the river a magenta pixel?
            if img.getpixel((last_pixel[0], last_pixel[1])) == magenta:
                finished_on_magenta = True

                # Remove magenta pixels untill there are only a few left
                # get the number of magenta pixels in the river, starting at the end of the river
                magenta_pixel_count = 0
                for pixel in reversed(draw_coords):
                    if img.getpixel((pixel[0], pixel[1])) == magenta:
                        magenta_pixel_count += 1
                    else:
                        break
                # Remove all but a few magenta pixels from the end of the river
                if magenta_pixel_count > offshore_runoff_pixel_length:
                    draw_coords = draw_coords[:-magenta_pixel_count + offshore_runoff_pixel_length]
                    print("Removed " + str(magenta_pixel_count - offshore_runoff_pixel_length) + " magenta pixels from the end of the river.")

            else:
                finished_on_magenta = False
                print("The river did not end on a magenta pixel, no need to remove any pixels from the river.")




            # start_color = green  # beginning color is green for source river
            # Draw the river to the map
            try:
                draw.line(sum(draw_coords.tolist(), []), fill=blue)  # draw the river line
            except:
                print("Error: Pixel out of bounds")
            # draw.point(draw_coords[0].tolist(), fill=start_color)  # Recolours the starting point of the river
            # TODO: Error checking the area around the river to make sure all pixels are valid

    # Break after first river when debugging
        #break   # Break after first river when debugging


    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")
    #System open the image for debug purposes
    img.show()


# Checks for Specific error where Multiple Blue pixels are around Green Source, replaces with White automatically
def correct_rivermap(image_path, output_file):
    # Load the image
    with Image.open(image_path) as image:
        # Get the pixel data
        pixels = image.load()
        # Create a new image to write to
        new_image = Image.new(image.mode, image.size, color=(255, 255, 255))
        new_pixels = new_image.load()
        # Loop through the pixels
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                # Check if the pixel is green
                if pixels[x, y] == green:
                    # Count the adjacent blue pixels
                    count = 0
                    adj_blues = []
                    if x > 0 and pixels[x - 1, y] == blue:
                        count += 1
                        adj_blues.append((x - 1, y))
                    if x < image.size[0] - 1 and pixels[x + 1, y] == blue:
                        count += 1
                        adj_blues.append((x + 1, y))
                    if y > 0 and pixels[x, y - 1] == blue:
                        count += 1
                        adj_blues.append((x, y - 1))
                    if y < image.size[1] - 1 and pixels[x, y + 1] == blue:
                        count += 1
                        adj_blues.append((x, y + 1))
                    # Check if the green pixel has more than one adjacent blue pixel
                    if count > 1:
                        for bx, by in adj_blues:
                            # Check if the blue pixel has only one adjacent blue pixel
                            bcount = 0
                            if bx > 0 and pixels[bx - 1, by] == blue:
                                bcount += 1
                            if bx < image.size[0] - 1 and pixels[bx + 1, by] == blue:
                                bcount += 1
                            if by > 0 and pixels[bx, by - 1] == blue:
                                bcount += 1
                            if by < image.size[1] - 1 and pixels[bx, by + 1] == blue:
                                bcount += 1
                            if bcount == 0:
                                # Replace the blue pixel with white
                                new_pixels[bx, by] = white
                                break
                        else:
                            print("Error at ({}, {})".format(x, y))
                            # Copy the pixel from the original image
                            new_pixels[x, y] = pixels[x, y]
                    else:
                        # Copy the pixel from the original image
                        new_pixels[x, y] = pixels[x, y]
                else:
                    # Copy the pixel from the original image
                    new_pixels[x, y] = pixels[x, y]
        # Save the new image
        new_image.save(output_file)


# Use Landsea file as mask image as most Blue errors happen in sea, so can be masked anyway
def mask_landsea(image_path, mask_path, output_image_path):
    # Load the original image
    img = Image.open(image_path)

    # Load the mask image
    mask = Image.open(mask_path)

    # Convert the mask image to RGB
    mask = mask.convert('RGB')

    # Get the size of the mask
    width, height = mask.size

    # Iterate over all pixels in the mask image
    for x in range(width):
        print(x, "/8192")
        for y in range(height):
            # Get the color of the pixel
            r, g, b = mask.getpixel((x, y))
            # If the color is magenta (FF0080), set the corresponding pixel in the original image to transparent
            if (r == 255) and (g == 0) and (b == 128):
                img.putpixel((x, y), (255, 0, 128, 0))

    # Save the modified image
    img.save(output_image_path)


# Checks for error of more than 2 touching Blue pixels, Does not correct yet
def check_image_for_more_than_two_blue(image_path):
    # Load the image
    image = Image.open(image_path)
    # Get the pixel data
    pixels = image.load()
    bpc = 0
    # Loop through the pixels
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            # Check if the pixel is green
            if pixels[x, y] == blue:
                # Count the adjacent blue pixels
                count = 0
                if x > 0 and pixels[x - 1, y] == blue:
                    count += 1
                if x < image.size[0] - 1 and pixels[x + 1, y] == blue:
                    count += 1
                if y > 0 and pixels[x, y - 1] == blue:
                    count += 1
                if y < image.size[1] - 1 and pixels[x, y + 1] == blue:
                    count += 1
                # Check if the green pixel has more than one adjacent blue pixel
                if count > 2:
                    print("Error Blue pixel with more than 2 adjacent at ({}, {})".format(x, y), "Blue Pixel Error:",
                          (bpc))
                    bpc += 1


# Test Region of the code

# Path to folder containing heightmap.png, landsea.png, rivers.geojson when testing
path = "River_Test/"

paint_land_sea(path + "heightmap.png", path + "landsea.png")
draw_rivers(path + "landsea.png", path + "rivers.geojson", path + "rivermap_mainstreams.png")
#correct_rivermap(path + "rivermap_mainstreams.png", path + "rivermap_corrected.png")
#mask_landsea(path + "rivermap_corrected.png", path + "landsea.png", path + "rivermap_masked.png")
#check_image_for_more_than_two_blue(path + "rivermap_masked.png")
