import json
from PIL import Image, ImageDraw
import numpy as np
import sys

# set scaling factor
scaling_factor = 30
# scaling_factor = float(sys.argv[1])
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


# Function to check how many pixels of a colour surrounds a pixel
def check_number_of_surrounding_color(img, pixel, color):
    '''Checks the pixels around the given pixel for the given color. Returns the number of pixels found.'''
    count = 0
    # Check the pixel above
    try:
        if img.getpixel((pixel[0], pixel[1] - 1)) == color:
            count += 1
    except IndexError:
        pass
    # Check the pixel below
    try:
        if img.getpixel((pixel[0], pixel[1] + 1)) == color:
            count += 1
    except IndexError:
        pass
    # Check the pixel to the left
    try:
        if img.getpixel((pixel[0] - 1, pixel[1])) == color:
            count += 1
    except IndexError:
        pass
    # Check the pixel to the right
    try:
        if img.getpixel((pixel[0] + 1, pixel[1])) == color:
            count += 1
    except IndexError:
        pass
    return count

def tributary_endpoint_is_valid(img, pixel):
    # The criteria for a valid pixel:
    # 1. a pixel must not border more than one blue pixel
    # 2. a cannot border red or green pixels
    is_valid = False
    if check_number_of_surrounding_color(img, pixel, blue) <= 1:
        if check_number_of_surrounding_color(img, pixel, red) == 0:
            if check_number_of_surrounding_color(img, pixel, green) == 0:
                is_valid = True
    return is_valid

def get_neighboring_pixels(pixel_position, img, maskedColors = None):
    '''Returns a list of neighboring pixels to the given pixel, except if they are masked.'''
    neighboring_pixels = []
    # Check the pixel above
    neighboring_pixels.append((pixel_position[0], pixel_position[1] - 1))
    # Check the pixel below
    neighboring_pixels.append((pixel_position[0], pixel_position[1] + 1))
    # Check the pixel to the left
    neighboring_pixels.append((pixel_position[0] - 1, pixel_position[1]))
    # Check the pixel to the right
    neighboring_pixels.append((pixel_position[0] + 1, pixel_position[1]))

    # Remove any pixels that are masked
    for pixel in neighboring_pixels:
        if img.getpixel(pixel) in maskedColors:
            neighboring_pixels.remove(pixel)
    return neighboring_pixels


def pathfind_to_valid_pixel(img, origin_pixel, max_pixels_visited=10000):
    '''Finds a valid pixel to pathfind to. Returns the pixel to pathfind to, or None if no valid pixel is found.'''
    # make list of visited pixels to avoid infinite loops
    visited_pixels = []
    recently_visited_pixels = []
    pixels_queue = []
    # Add the origin pixel to the queue
    pixels_queue.append(origin_pixel)

    valid_endpoint = None
    # While the queue is not empty and a valid pixel has not been found
    while len(pixels_queue) > 0 and valid_endpoint == None:
        # Break if max number of pixels visited
        if len(visited_pixels) > max_pixels_visited:
            break
        # If the queue is empty, get the neighboring pixels of the recently visited pixels and add them to the queue.
        if len(pixels_queue) == 0:
            for pixel in recently_visited_pixels:
                pixels_queue += get_neighboring_pixels(pixel, img, maskedColors=[blue, red, green])
            recently_visited_pixels = []
        # Get the next pixel in the queue
        pixel = pixels_queue.pop(0)
        # If the pixel has not been visited
        if pixel not in visited_pixels:
            # Add the pixel to the recently visited pixels list
            recently_visited_pixels.append(pixel)
            # If the pixel is valid
            if tributary_endpoint_is_valid(img, pixel):
                # Set the valid pixel to the current pixel
                valid_endpoint = pixel
            # Add the pixel to the visited pixels list
            visited_pixels.append(pixel)
    # Return the valid pixel
    return valid_endpoint







def draw_rivers(landsea_image, rivers_geojson, output_file):
    """Implements the river-drawing algorithm, taking in a land-sea painted image and a river geojson file."""
    # Set the pixel length that rivers extend into the sea
    offshore_runoff_pixel_length = 3

    # load the painted land sea map
    img = Image.open(landsea_image)
    # Flip top to bottom for right coordinate alignment
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    # get image width and height
    img_width, img_height = img.size
    # Create an ImageDraw object to draw on the image
    draw = ImageDraw.Draw(img)


    with open(rivers_geojson, "r") as riverData:
        data = json.load(riverData)

    # get rivers
    rivers = data["features"]

    # Order the list of rivers by parent ID, so that ID 0 is first, and ID 1 is second, etc.
    # This is so that tributaries are rendered later than source rivers
    rivers = sorted(rivers, key=lambda k: k["properties"]["parent"])

    print("Number of rivers: " + str(len(rivers)))
    rivers_count = 0
    for river in rivers:
        rivers_count += 1
        # For debug so that we can easier understand what is going on
        # get river name
        river_name = river["properties"]["name"]
        #Get river type
        river_type = river["properties"]["type"]
        #Get river parent
        river_parent = river["properties"]["parent"]
        # Print the progress, river name, type and parent ID to the console.
        print("=============================================")
        print("River " + str(rivers_count) + " of " + str(len(rivers)) + ": " + river_name + " (" + river_type + ") " + "Parent ID: " + str(river_parent))


        #Converting the GEOJSON coordinates to pixel coordinates
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

        #Check that the river is not empty
        if len(draw_coords) == 0:
            # Print out an error message and continue to the next river
            print("River is empty, skipping to next river")
            print("=============================================")
            continue

        # Remove cordinates that are above the ocean (except for some)
        last_pixel = draw_coords[-1]   #This is the last pixel in the river

        # Is the last pixel in the river a magenta pixel? If yes then we need to trim it down a bit
        if img.getpixel((last_pixel[0], last_pixel[1])) == magenta:
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
                print("Removed " + str(magenta_pixel_count - offshore_runoff_pixel_length) +
                      " magenta pixels from the end of the river.")

        else:
            print("The river did not end on a magenta pixel, no need to remove any pixels from the river.")


        # Check if any of the coordinates would draw over another river
        would_draw_over_another_river = False
        for pixel in draw_coords:
            if img.getpixel((pixel[0], pixel[1])) == blue:
                # Print out an error message and continue to the next river
                print("The river " + river_name + " would draw over another river, trying to fix it.")
                would_draw_over_another_river = True
                break
        if would_draw_over_another_river:
            # If we are about to overdraw another river,
            # then we need to try to handle it by removing pixels from the river until we are valid.
            # We will remove pixels from the end of the river until we are valid. Or until the river is empty.
            while would_draw_over_another_river:
                # Remove the last pixel from the river
                # if this was the last pixel in the river, then we will abort this river
                if len(draw_coords) < 1:
                    print("Could not fix the river, skipping to next river")
                    print("=============================================")
                    break

                #Remove the last pixel from the river
                draw_coords = draw_coords[:-1]
                # Check if the river is now valid
                would_draw_over_another_river = False
                for pixel in draw_coords:
                    if img.getpixel((pixel[0], pixel[1])) == blue:
                        would_draw_over_another_river = True
                        #print("The river is still invalid, trying to fix it.")
                        break
        print("The river passed the direct overdraw check.")

        # Time to correct the border
        # If the rivers does not have valid borders,
        # then we will start subtracting pixels from the end of the river
        # until we have a valid river
        has_invalid_border = False
        for pixel in draw_coords:
            if check_number_of_surrounding_color(img, pixel, blue) > 1:
                has_invalid_border = True
                print("The river " + river_name + " has an invalid border, trying to fix it.")
                break
        while has_invalid_border:
            # Remove the last pixel from the river
            # if this was the last pixel in the river, then we will abort this river
            if len(draw_coords) < 1:
                print("Could not fix the river border, skipping to next river")
                print("=============================================")
                break
            #Remove the last pixel from the river
            draw_coords = draw_coords[:-1]
            # Check if the river is now valid
            has_invalid_border = False
            for pixel in draw_coords:
                if check_number_of_surrounding_color(img, pixel, blue) > 1:
                    has_invalid_border = True
                    print("Still invalid borders, trying to fix it.")
                    break
        print("The river passed the border check.")

        if river_parent != 0:
            # If the river is a tributary, we must now make sure that it is connected to the source river in a valid way
            if not tributary_endpoint_is_valid(img, draw_coords[-1]):
                print("This tributary is not connected to the source river, trying to fix it.")
                new_endpoint = pathfind_to_valid_pixel(img, draw_coords[-1])
                # Find every pixel between the old endpoint and the new endpoint
                # AKA pathfind from the old endpoint to the new endpoint
                # TODO: Impement pathfinding

        # Draw the river to the map
        try:
            draw.line(sum(draw_coords.tolist(), []), fill=blue)  # draw the river line
            # if the river is named "Fargo" then we will draw it in orange
            if river_name == "Fargo":
                draw.line(sum(draw_coords.tolist(), []), fill=(255, 165, 0)) #Orange DEBUG DEBUG DEBUG
        except:
            print("Error: Pixel out of bounds")

        # If the river has 0 as a parent id, then it is a source river
        if river_parent == 0:
            draw.point(draw_coords[0].tolist(), fill=green)  # Recolours the starting point of the river
        else:
        # If the river has a parent id, then it is a tributary. So we change the last pixel to red
            draw.point(draw_coords[-1].tolist(), fill=red)  # Recolours the end point of the river

        # TODO: Error checking the area around the river to make sure all pixels are valid


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
