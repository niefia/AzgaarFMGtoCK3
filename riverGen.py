import json

from PIL import Image, ImageDraw
import numpy as np

# set scaling factor
scaling_factor = 30
# scaling_factor = float(sys.argv[1])
# print the scaling factor
print("Scaling factor used is: " + str(scaling_factor))
show_failed_rivers = True  # This is used to control popups for failed rivers
print("Show failed rivers as they fail = " + str(show_failed_rivers))

# Constants for colours
blue = (0, 0, 255)
deep_blue = (0, 0, 128)
light_blue = (173, 216, 230)
green = (0, 255, 0)
magenta = (255, 0, 128)
white = (255, 255, 255)
red = (255, 0, 0)
orange = (255, 165, 0)
brown = (165, 42, 42)
purple = (128, 0, 128)

# Declare a debug variable
debug = False

def generate_river_files():
    """ this is the main function for riverGen.py"""
    # "Main"

    # Path to folder containing heightmap.png, landsea.png, rivers.geojson when testing
    path = "River_Test/"

    paint_land_sea(path + "heightmap.png", path + "landsea.png")
    draw_rivers(path + "landsea.png", path + "rivers.geojson", path + "rivermap.png")
    # Kept this in for sanity checking
    check_whole_image_for_river_rules_violations(path + "rivermap.png")

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

    discarded_rivers = []

    print("Number of rivers: " + str(len(rivers)))
    rivers_count = 0
    for river in rivers:

        rivers_count += 1
        # For debug so that we can easier understand what is going on
        # get river name
        river_name = river["properties"]["name"]
        # Get river type
        river_type = river["properties"]["type"]
        # Get river parent
        river_parent = river["properties"]["parent"]
        # Print the progress, river name, type and parent ID to the console.
        print("=============================================")
        print("River " + str(rivers_count) + " of " + str(
            len(rivers)) + ": " + river_name + " (" + river_type + ") " + "Parent ID: " + str(river_parent))

        # Converting the GEOJSON coordinates to pixel coordinates
        flat_coords = np.array([item * scaling_factor for sublist in river["geometry"]["coordinates"]
                                for item in sublist])
        centred_coords = flat_coords + np.tile([img_width / 2, img_height / 2], int(flat_coords.size / 2))
        centred_coords = centred_coords.reshape(int(len(centred_coords) / 2), 2)  # reshaping into 2-column array
        draw_coords = np.floor(centred_coords[0]).reshape(1, 2)  # first coordinates to add

        # Find the pixel coordinates of the river line
        for row in range(1, centred_coords[1:].shape[0]):
            # This is the 2d Array that holds the coordinates of the river line.
            new_coords = np.floor(centred_coords[row]).reshape(1, 2)
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

        # Print info about the river to the console
        print("Literal conversion of river coordinates to pixels gave " + str(len(draw_coords)) + " pixels")

        # Trim any pixels that are outside the image
        draw_coords = draw_coords[draw_coords[:, 0] < img_width]
        draw_coords = draw_coords[draw_coords[:, 1] < img_height]

        print("Trimming pixels outside the image gave " + str(len(draw_coords)) + " pixels")

        # Remove any duplicate coordinates
        draw_coords = remove_duplicate_coordinates(draw_coords)
        print("Trimming duplicate coordinates gave " + str(len(draw_coords)) + " pixels")

        # Check that the river is not empty
        if len(draw_coords) == 0:
            # Print out an error message and continue to the next river
            discarded_rivers.append(river)
            print("River is empty, skipping to next river")
            print("=============================================")
            continue

        # Remove coordinates that run into the ocean (except for some)
        draw_coords = remove_offshore_runoff(draw_coords, img, offshore_runoff_pixel_length)

        # Check the river against itself to make sure that it is valid
        # We will remove invalid pixels from the river, and fill the gaps with a path
        draw_coords = fix_self_violations(draw_coords)
        print("The river passed the self check.")

        # Remove pixels until the river does not overlap with another river, starting from the top and going downstream
        try:
            draw_coords = fix_overdraw(draw_coords, img, river_name)
            print("The river passed the direct overdraw check.")
        except UnfixableOverdrawException:  # If the river is not fixable, then we will skip it
            discarded_rivers.append(river)
            print("=============================================")
            continue

        # Find and correct any pixels that violate what we call the "border rule"
        try:
            draw_coords = fix_borders(draw_coords, img, river_name)
            print("The river passed the border check.")
        except UnfixableBorderException:  # If the river is not fixable, then we will skip it
            discarded_rivers.append(river)
            print("=============================================")
            continue

        # If the river is a tributary, it must connect to a source river in a valid way
        if river_parent != 0:
            try:
                draw_coords, discarded_rivers = fix_tributary_connection(img, draw_coords, discarded_rivers, river)
                # TODO: When a tributary fails to connect, it shoudl become its own river instead of discarding it
            # Handle the specific exception that is thrown when the river could not be fixed
            except TributaryConnectionException:
                print("=============================================")
                continue
        print("The river passed the tributary is connected check.")

        # Draw the river to the map
        try:
            draw.line(sum(draw_coords.tolist(), []), fill=blue)  # draw the river line
        except:
            # The draw.line function will throw an error if the river is too short
            # If the river is too short, then we will skip it
            discarded_rivers.append(river)
            print("The river " + river_name + " is too short (1 pixel), skipping to next river")
            print("=============================================")

        # If the river has 0 as a parent id, then it is a source river
        if river_parent == 0:
            draw.point(draw_coords[0].tolist(), fill=green)  # Recolours the starting point of the river
        else:
            # If the river has a parent id, then it is a tributary. So we change the last pixel to red
            draw.point(draw_coords[-1].tolist(), fill=red)  # Recolours the end point of the river
        print("The river " + river_name + " was drawn successfully.")
        print("=============================================")
        # TODO: Error checking the area around the river to make sure all pixels are valid

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

    # Print out the discarded rivers
    print("The following rivers were discarded because the converter could not fix them\n"
          "for details on why they were discarded, see the detailed log above")
    for river in discarded_rivers:
        print(river["properties"]["name"])
    print("=============================================")

    # System open the image for debug purposes
    img.show()

def fix_self_violations(original_coordinates):
    # Convert to local coordinates and draw a sandbox image
    local_river = original_coordinates.copy()

    while True:
        sandbox_img, temp_river = draw_small_river_image(local_river)
        # Find crowded and lonely violations, and remove them, refresh the image
        crowded_violations = river_self_violations_exclude_ends(sandbox_img, temp_river)
        temp_river = remove_coordinates_from_list(crowded_violations, temp_river)
        sandbox_img, temp_river = draw_small_river_image(temp_river)

        # Find endcap violations, and remove them, refresh the image
        endcap_violations = river_self_violations_ends_only(sandbox_img, temp_river)
        temp_river = remove_coordinates_from_list(endcap_violations, temp_river)
        sandbox_img, temp_river = draw_small_river_image(temp_river)

        # Compare the length of temp_river and local_river to see if we have removed any violations
        if len(temp_river) == len(local_river):
            # If we have not removed any violations, then we are done
            local_river = temp_river
            break
        else:
            # If we have removed violations, then should fix any gaps and continue
            # Because fixing gaps may impact other gaps, we will only fix one gap at a time, and then continue
            temp_river = fix_gaps(temp_river)

            # Remove any duplicates
            temp_river_no_dupes = remove_duplicate_coordinates(temp_river)
            if len(temp_river_no_dupes) != len(temp_river):
                # If we have removed duplicates, then we raise an error
                raise ValueError(
                    "Error/DEBUG: Duplicate coordinates were found in the river after fixing a gap. This should not happen. Fix the fill algorithm.")
            temp_river = temp_river_no_dupes
            # Save the temp_river as the local_river
            local_river = temp_river

    # Correct the coordinates to be in global coordinates
    # Find the min x and y values of the original coordinates
    min_x = np.min(original_coordinates[:, 0])
    min_y = np.min(original_coordinates[:, 1])

    # Add the min x and y values to the coordinates
    local_river[:, 0] += min_x
    local_river[:, 1] += min_y

    # Return the fixed coordinates
    return local_river
def remove_offshore_runoff(draw_coords, img, offshore_runoff_pixel_length):
    last_pixel = draw_coords[-1]  # This is the last pixel in the river
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
                  " offshore pixels from the end of the river.")

    else:
        print("River does not have any offshore runoff.")
    return draw_coords

def fix_overdraw(draw_coords, img, river_name):
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
                raise UnfixableOverdrawException
            # Remove the last pixel from the river
            draw_coords = draw_coords[:-1]
            # Check if the river is now valid
            would_draw_over_another_river = False
            for pixel in draw_coords:
                if img.getpixel((pixel[0], pixel[1])) == blue:
                    would_draw_over_another_river = True
                    # print("The river is still invalid, trying to fix it.")
                    break
    return draw_coords

def fix_borders(draw_coords, img, river_name):
    # Time to correct the border
    # If the rivers does not have valid borders,
    # then we will start subtracting pixels from the end of the river
    # until we have a valid river
    has_invalid_border = False
    for pixel in draw_coords:  # TODO: Reverse the order of the pixels, the issue is more likely to be at the start of the river
        if not check_if_valid_border(img, pixel):
            has_invalid_border = True
            print("The river " + river_name + " has an invalid border, trying to fix it.")
            break
    while has_invalid_border:
        # Remove the last pixel from the river
        draw_coords = draw_coords[:-1]
        # if this was the last pixel in the river, then we will abort this river
        if len(draw_coords) == 1:
            print("Could not fix the river border, skipping to next river")
            raise UnfixableBorderException
        # Check if the river is now valid
        has_invalid_border = False
        for pixel in draw_coords:
            if not check_if_valid_border(img, pixel):
                has_invalid_border = True
                print("Still invalid borders, trying to fix it.")
                break
    return draw_coords

def fix_tributary_connection(img, river_coordinates, discarded_rivers, river):
    if not tributary_endpoint_is_valid(img, river_coordinates[-1]):
        print("This tributary is not connected to the source river in a valid way, trying to fix it.")
        # First, we will remove the last pixel from the river until we have more room to work with
        while not pixel_has_room_to_expand(img, river_coordinates[-1]):
            # Remove the last pixel from the river
            # if this was the last pixel in the river, then we will abort this river
            if len(river_coordinates) < 1:
                discarded_rivers.append(river)
                print("Could not fix the river, it is no longer long enough to process, skipping to next river")
                raise TributaryConnectionException("Could not fix the river, skipping to next river")
            # Remove the last pixel from the river
            river_coordinates = river_coordinates[:-1]
        # Now that we have more room to work with, we will try to find a valid pixel to attach the river to
        try:
            new_endpoint = search_for_valid_pixel_to_attach_river(img, river_coordinates[-1])
        except PathNotFoundException:
            discarded_rivers.append(river)
            print("Could not find a valid pixel to attach the tributary to, skipping to next river")
            raise TributaryConnectionException(
                "Could not find a valid pixel to attach the tributary to, skipping to next river")

        # Print out the position of the new endpoint
        print("Found a new endpoint candidate at " + str(new_endpoint))

        # If we could not find a valid pixel to attach the river to, then we will abort this river
        if new_endpoint is None:
            discarded_rivers.append(river)
            print("Could not find a valid pixel to attach the river to, skipping to next river")
            print("=============================================")
            raise TributaryConnectionException(
                "Could not find a valid pixel to attach the river to, skipping to next river")
        # If we found a valid pixel to attach the river to, then we will path to it
        else:
            # Path to the new endpoint
            path = pathfind_from_a_to_b(img, river_coordinates[-1], new_endpoint)
            # Add the path to the river
            river_coordinates = np.concatenate((river_coordinates, path))
            print("Pathfound to the new endpoint successfully.")
            return river_coordinates, discarded_rivers


def check_whole_image_for_river_rules_violations(image_path):
    """Checks if the image has more than two blue pixels adjacent to a green pixel"""
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

    if bpc == 0:
        print("The final image check found no pixel errors violating the river rules.")
    else:
        print("The final image check found " + str(bpc) + " pixel errors violating the river rules.")
def draw_small_river_image(river_pixels, draw_direction=False):
    # Copy the draw_coords to a new array.
    localized_river_coordinates = river_pixels.copy()

    # Move the entire array so that the min x and min y are at 0,0
    localized_river_coordinates[:, 0] -= int(np.min(river_pixels[:, 0]))
    localized_river_coordinates[:, 1] -= int(np.min(river_pixels[:, 1]))

    padding = 2
    # Now add the padding to the entire array,
    # padding is needed in case pathfinding needs to go on the outside of the river
    localized_river_coordinates[:, 0] += padding
    localized_river_coordinates[:, 1] += padding

    # Calculate the max x and max y
    max_x = int(np.max(localized_river_coordinates[:, 0]))
    max_y = int(np.max(localized_river_coordinates[:, 1]))

    # Create a new image that is the max_x + 1 + padding by max_y + 1 + padding
    river_img = Image.new("RGB", (max_x + 1 + padding, max_y + 1 + padding), color=white)

    if draw_direction:
        # Generate a set of color values ranging from deep blue to light blue
        num_pixels = localized_river_coordinates.shape[0]
        color_range = np.linspace(0, 1, num_pixels)
        colors = [tuple((1 - t) * np.array(deep_blue) + t * np.array(light_blue)) for t in color_range]
        draw = ImageDraw.Draw(river_img)
        for i, pixel in enumerate(localized_river_coordinates):
            draw.point((pixel[0], pixel[1]), fill=tuple(map(int, colors[i])))
    else:
        # Draw the river to the river_img
        draw = ImageDraw.Draw(river_img)
        for pixel in localized_river_coordinates:
            draw.point((pixel[0], pixel[1]), fill=blue)

    # Return the image and the self_check_coords
    return river_img, localized_river_coordinates
def is_octhogonal(coordinate_a, coordinate_b):
    # Check if the two coordinates are one pixel away from each other
    # This function will return True if they are one pixel away
    # This function will return False if they are not one pixel away
    x_variance = abs(coordinate_a[0] - coordinate_b[0])
    y_variance = abs(coordinate_a[1] - coordinate_b[1])
    # If the variance is 1 on one axis and 0 on the other, then they are one pixel away
    if (x_variance == 1 and y_variance == 0) or (x_variance == 0 and y_variance == 1):
        return True
    else:
        return False


def detect_and_fix_1_wide_gap(self_check_img, gap):
    '''Detects and fixes a 1 pixel wide gap in the river.'''
    x_variance = abs(gap[0][0] - gap[1][0])
    y_variance = abs(gap[0][1] - gap[1][1])
    if x_variance + y_variance > 1:
        # If x_variance is 2, then we are dealing with a orthogonal gap
        if x_variance == 2:
            # If the gap is going right, then we will add a pixel to the right
            if gap[0][0] < gap[1][0]:
                gap = (gap[0], (gap[1][0] - 1, gap[1][1]))
            # If the gap is going left, then we will add a pixel to the left
            else:
                gap = (gap[0], (gap[1][0] + 1, gap[1][1]))
        # If y_variance is 2, then we will add a pixel to the gap
        if y_variance == 2:
            # If the gap is going down, then we will add a pixel below
            if gap[0][1] < gap[1][1]:
                gap = (gap[0], (gap[1][0], gap[1][1] - 1))
            # If the gap is going up, then we will add a pixel above
            else:
                gap = (gap[0], (gap[1][0], gap[1][1] + 1))
        # If the variance is 1 on both axis, then we are dealing with a diagonal gap
        if x_variance == 1 and y_variance == 1:
            # If the gap is going right and down, then we will check if we can add a pixel to the right
            if gap[0][0] < gap[1][0] and gap[0][1] < gap[1][1]:
                if check_number_of_surrounding_color(self_check_img, (gap[0][0] + 1, gap[0][1]), blue) == 2:
                    gap = (gap[0], (gap[1][0] - 1, gap[1][1]))
                # Else we will check if we can add a pixel below
                elif check_number_of_surrounding_color(self_check_img, (gap[0][0], gap[0][1] + 1), blue) == 2:
                    gap = (gap[0], (gap[1][0], gap[1][1] - 1))
                else:
                    # Throw an error, as we should never get here
                    raise PathNotFoundException("Error: Diagonal gap could not be filled.")
            # If the gap is going right and up, then we will check if we can add a pixel to the right
            if gap[0][0] < gap[1][0] and gap[0][1] > gap[1][1]:
                if check_number_of_surrounding_color(self_check_img, (gap[0][0] + 1, gap[0][1]), blue) == 2:
                    gap = (gap[0], (gap[1][0] - 1, gap[1][1]))
                # Else we will check if we can add a pixel above
                elif check_number_of_surrounding_color(self_check_img, (gap[0][0], gap[0][1] - 1), blue) == 2:
                    gap = (gap[0], (gap[1][0], gap[1][1] + 1))
                else:
                    # Throw an error, as we should never get here
                    raise PathNotFoundException("Error: Diagonal gap could not be filled.")
            # If the gap is going left and down, then we will check if we can add a pixel to the left
            if gap[0][0] > gap[1][0] and gap[0][1] < gap[1][1]:
                if check_number_of_surrounding_color(self_check_img, (gap[0][0] - 1, gap[0][1]), blue) == 2:
                    gap = (gap[0], (gap[1][0] + 1, gap[1][1]))
                # Else we will check if we can add a pixel below
                elif check_number_of_surrounding_color(self_check_img, (gap[0][0], gap[0][1] + 1), blue) == 2:
                    gap = (gap[0], (gap[1][0], gap[1][1] - 1))
                else:
                    # Throw an error, as we should never get here
                    raise PathNotFoundException("Error: Diagonal gap could not be filled.")
            # If the gap is going left and up, then we will check if we can add a pixel to the left
            if gap[0][0] > gap[1][0] and gap[0][1] > gap[1][1]:
                if check_number_of_surrounding_color(self_check_img, (gap[0][0] - 1, gap[0][1]), blue) == 2:
                    gap = (gap[0], (gap[1][0] + 1, gap[1][1]))
                # Else we will check if we can add a pixel above
                elif check_number_of_surrounding_color(self_check_img, (gap[0][0], gap[0][1] - 1), blue) == 2:
                    gap = (gap[0], (gap[1][0], gap[1][1] + 1))
                else:
                    # Throw an error, as we should never get here
                    raise PathNotFoundException("Error: Diagonal gap could not be filled.")
    return gap


def river_self_violations_ends_only(sandbox_img, coordinates):
    # Check the first and last pixel in the river path for self violations
    # Returns a list of coordinates that are self violations

    violations = []
    # Check the first pixel
    if check_number_of_surrounding_color(sandbox_img, coordinates[0], blue) != 1:
        violations.append(coordinates[0])
    # Check the colour of the first pixel
    if sandbox_img.getpixel((coordinates[0][0], coordinates[0][1])) != blue:
        raise ValueError("Error: Alignment is off, first pixel in river path is not blue. Image size is: " + str(
            sandbox_img.size) + " and coordinates are: " + str(coordinates[0]))

    # Check the last pixel
    if check_number_of_surrounding_color(sandbox_img, coordinates[-1], blue) != 1:
        violations.append(coordinates[-1])
    # Check the colour of the last pixel
    if sandbox_img.getpixel((coordinates[-1][0], coordinates[-1][1])) != blue:
        raise ValueError("Error: Alignment is off, last pixel in river path is not blue. Image size is: " + str(
            sandbox_img.size) + " and coordinates are: " + str(coordinates[-1]))
    return violations


def river_self_violations_exclude_ends(self_check_img, coordinates):
    violations = []
    # Check each pixel in the river path for self violations
    # Returns a list of coordinates that are self violations,
    # The first and last pixel have the same special rule

    for i in range(len(coordinates)):
        # If the pixel is the first or last pixel then we will skip it
        if i == 0 or i == len(coordinates) - 1:
            continue
        # Else we will check if the pixel is not surrounded by exactly 2 blue pixels
        else:
            if check_number_of_surrounding_color(self_check_img, coordinates[i], blue) != 2:
                # We have a violation
                violations.append(coordinates[i])
            elif self_check_img.getpixel((coordinates[i][0], coordinates[i][1])) != blue:
                # We have a violation
                raise ValueError("Error: Alignment is off, pixel in river path is not blue.")
    return violations


# Pathfind from a to b, return a list of pixels
def pathfind_from_a_to_b(img, origin_pixel, destination_pixel, max_pixels_visited=10000):
    """Pathfinds from the origin pixel to the destination pixel, returns a list of pixels.
    Throws an exception if no path is found."""

    open_nodes = []
    closed_nodes = []
    # Add the origin pixel to the open nodes list
    open_nodes.append(Node(origin_pixel, None, 0, 0))
    current_node = None
    # While true
    while True:
        # Throw a max number of pixels visited exception
        if len(open_nodes) + len(closed_nodes) > max_pixels_visited:
            raise PathNotFoundException("Max number of pixels visited during pathfinding.")
        # Throw an exception if there are no more nodes to visit
        if len(open_nodes) == 0:
            raise PathNotFoundException("No more nodes to visit and could not find a path")
        # Get the node with the lowest f value
        current_node = open_nodes.pop(0)
        # Add the current node to the closed nodes list
        closed_nodes.append(current_node)
        # If the current node is the destination node, break
        if current_node.pixel[0] == destination_pixel[0] and current_node.pixel[1] == destination_pixel[1]:
            break
        # Get the neighboring pixels
        neighboring_pixels = get_neighboring_pixels(current_node.pixel, img, [blue, red, green])
        # Remove pixels that violate border rules
        for pixel in neighboring_pixels:
            # TODO: shoudl not pathfind to pixel with 1 blue neightbour, unless it is the destination pixel
            if coordinates_equals(pixel, destination_pixel):
                continue
            if check_number_of_surrounding_color(img, pixel, blue) > 0:
                neighboring_pixels.remove(pixel)
        # For each neighboring pixel
        for pixel in neighboring_pixels:
            # Create a node for the pix, calculate the h value to be the sum of the x and y distance to the destination.
            # Using the Manhattan distance, encourages the pathfinder to move in a diagonal direction.
            neighbour = Node(pixel, current_node, current_node.g + 1,
                             abs(pixel[0] - destination_pixel[0]) + abs(pixel[1] - destination_pixel[1]))
            # If the node is in the closed nodes list, skip it
            if neighbour in closed_nodes:
                continue
            # If the node is not in the open nodes list, add it
            if neighbour not in open_nodes:
                open_nodes.append(neighbour)
            # Update the g value of the node if the new g value is lower
            elif neighbour.g > current_node.g + 1:
                neighbour.g = current_node.g + 1
                neighbour.parent = current_node

        # Sort the open nodes list on f value, and if f values are equal, sort on h value
        open_nodes.sort(key=lambda x: (x.f, x.h))

    shortest_path = []
    # Start at the destination node and work backwards to the origin node
    while current_node is not None:
        shortest_path.append(current_node.pixel)
        current_node = current_node.parent
    # invert the list - when traversing the parent nodes, the path is in reverse order

    return shortest_path[::-1]
class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, pixel, parent, g, h):
        self.pixel = pixel
        self.parent = parent  # Parent node is the current node's shortest path predecessor
        self.g = g  # g is the cost of the path from the start node to this node
        self.h = h  # h is the estimated cost of the path from this node to the goal node
        self.f = g + h  # f is the sum of g and h and is used to determine the next node to visit

    def __lt__(self, other):  # Overload the less than operator
        return self.f < other.f

    def __eq__(self, other):  # Overload the equals operator
        # Check if the pixel value for both nodes is the same
        is_equal = self.pixel[0] == other.pixel[0] and self.pixel[1] == other.pixel[1]
        return is_equal
def get_neighboring_pixels(pixel_position, img, maskedColors=None):
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
        try:
            if img.getpixel(pixel) in maskedColors:
                neighboring_pixels.remove(pixel)
        except IndexError:
            pass
    return neighboring_pixels
def search_for_valid_pixel_to_attach_river(img, origin_pixel, max_search_distance=1000):
    '''Uses a fill algorithm to look for the closest valid pixel to attach a river to.
    Returns the pixel to pathfind to, or None if no valid pixel is found.'''
    # make list of visited pixels to avoid infinite loops, add the origin pixel to the list to set the type

    visited_pixels = []
    recently_visited_pixels = []
    pixels_queue = []
    # Add the origin pixel to the queue
    pixels_queue.append(origin_pixel)

    # Debugging
    # Show a preview of the search
    img_copy = img.copy()
    draw = ImageDraw.Draw(img_copy)

    valid_endpoint = None
    distance = 0
    # While the queue is not empty and a valid pixel has not been found
    while True:
        # Print a warning if the visited pixels list is getting too long
        if distance == max_search_distance * 0.5:
            print("Warning: Visited pixels list is getting long. Length: " + str(len(visited_pixels)))

        # Throw an exception if we have reach the max distance to search
        if distance > max_search_distance:
            raise PathNotFoundException("Max distance to search reached. "
                                        "Could not find a valid pixel to attach river to.")

        # If the queue is empty, get the neighboring pixels of the recently visited pixels and add them to the queue.
        if len(pixels_queue) == 0:
            for pixel in recently_visited_pixels:
                pixels_queue += get_neighboring_pixels(pixel, img, maskedColors=[blue, red, green])
            recently_visited_pixels = []
        # Throw an exception if there are no more pixels to visit, print the number of pixels visited
        if len(pixels_queue) == 0:
            raise PathNotFoundException(
                "No more pixels to evaluate and could not find a valid pixel to attach river to. Pixels visited: " + str(
                    len(visited_pixels)))

        # Get the next pixel in the queue
        pixel = pixels_queue.pop(0)

        # Determine that the pixel is not in the visited pixels list
        pixel_is_in_visited_pixels = False
        for visited_pixel in visited_pixels:
            if visited_pixel[0] == pixel[0] and visited_pixel[1] == pixel[1]:
                pixel_is_in_visited_pixels = True

        if not pixel_is_in_visited_pixels:
            # Add the pixel to the recently visited pixels list
            recently_visited_pixels.append(pixel)
            # If the pixel is valid
            if tributary_endpoint_is_valid(img, pixel):
                # Set the valid pixel to the current pixel
                valid_endpoint = [pixel[0], pixel[1]]
                # check that the pixel is not teh origin pixel
                if valid_endpoint[0] == origin_pixel[0] and valid_endpoint[1] == origin_pixel[1]:
                    print("ERROR: Valid endpoint is the same as the origin pixel")
                break
            # Add the pixel to the visited pixels list
            visited_pixels.append(pixel)

        # increment the distance
        distance += 1

    # Throw an exception if no valid pixel was found
    if valid_endpoint is None:
        raise Exception("No valid pixel found to attach river to.")

    # Return the valid pixel
    return valid_endpoint

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

def check_if_valid_border(img, pixel):
    """Checks if a river pixel at the position would violate the rules of the river system."""
    # Check sourounding pixels for blue
    # If there is a blue, green or red pixel, return false
    is_valid = False
    if check_number_of_surrounding_color(img, pixel, blue) == 0:
        if check_number_of_surrounding_color(img, pixel, red) == 0:
            if check_number_of_surrounding_color(img, pixel, green) == 0:
                is_valid = True
    return is_valid

def tributary_endpoint_is_valid(img, pixel):
    # The criteria for a valid pixel:
    # 1. a pixel must not border more than one blue pixel
    # 2. a cannot border red or green pixels
    is_valid = False
    if check_number_of_surrounding_color(img, pixel, blue) == 1:
        if check_number_of_surrounding_color(img, pixel, red) == 0:
            if check_number_of_surrounding_color(img, pixel, green) == 0:
                is_valid = True
    return is_valid


# Function to check if a pixel has room to expand
def pixel_has_room_to_expand(img, pixel):
    '''Checks if the given pixel has room to expand. Returns True if it does, False otherwise.'''
    # The criteria for a valid pixel:
    # 1. a pixel must not border any blue pixels
    # 2. a pixel cannot border red or green pixels
    has_room = False
    if check_number_of_surrounding_color(img, pixel, blue) == 0:
        if check_number_of_surrounding_color(img, pixel, red) == 0:
            if check_number_of_surrounding_color(img, pixel, green) == 0:
                has_room = True
    return has_room


def get_first_gap(sandbox_coordinates):
    # This function will take a list of coordinates and return the first gap that is found
    # A gap has two anchor points, the first pixel in the gap and the last pixel in the gap
    # The anchor points are known valid pixels, but the pixels in between are not
    # The gap will be returned as a tuple of two coordinates

    # If the river is shorter than 2, then there cannot be a gap
    if len(sandbox_coordinates) < 2:
        # Throw an error, as we should never get here
        raise ValueError("Error: You are trying to find a gap in a list of coordinates that is less than 2.")

    # If no gap is found, then the function will return None
    gap = None
    # Loop through the coordinates and find the first gap
    for i in range(len(sandbox_coordinates) - 1):
        # If the next coordinate is not one pixel away from the current coordinate
        if not is_octhogonal(sandbox_coordinates[i], sandbox_coordinates[i + 1]):
            # We have found a gap
            gap = (sandbox_coordinates[i], sandbox_coordinates[i + 1])
            break

    # Check the gap does not have two equal anchors
    if gap is not None:
        if gap[0][0] == gap[1][0] and gap[0][1] == gap[1][1]:
            sandbox_coordinates = remove_duplicate_coordinates(sandbox_coordinates)
            img, _ = draw_small_river_image(sandbox_coordinates, True)
            img = highlight_point(img, gap[0], red)
            highlight_point(img, gap[1], purple).show()
            # Throw an error, as we should never get here
            raise ValueError("Error: Gap detected but it is invalid. Gap had the same anchor points at both ends.")

    return gap


def fill_gap(gap, sandbox_coordinates):
    # This function will take a gap and fill it in using path finding

    # First we must trim the gap from the sandbox coordinates
    # Cast the gap to a numpy array, so we can use numpy functions
    gap_removed_sandbox_coordinates = remove_coordinates_from_list(np.array(gap), sandbox_coordinates)

    # Then we must generate an image for the algorithm to work on with the gap removed
    path_image, _ = draw_small_river_image(gap_removed_sandbox_coordinates)

    # It is an error to have the same anchor points, so we should handle that
    if gap[0][0] == gap[1][0] and gap[0][1] == gap[1][1]:
        # Throw an error, as we should never get here
        raise PathNotFoundException("Error: Gap could not be filled. Gap had the same anchor points at both ends.")

    # If the gap is huge, it is likely an error
    if abs(gap[0][0] - gap[1][0]) > 10 or abs(gap[0][1] - gap[1][1]) > 10:
        gap_size = abs(gap[0][0] - gap[1][0]) + abs(gap[0][1] - gap[1][1])
        raise PathNotFoundException(
            "Error: Gap could not be filled. Gap was massively large at " + str(gap_size) + " pixels.")

    # Then we must find a path between the two anchor points
    path = pathfind_from_a_to_b(path_image, gap[0], gap[1], 10)

    # Then we must add the path into the sandbox coordinates at the gap
    # We find where this is by looking for the first coordinate in the sandbox_coordinate that is octhogonal to the first anchor point
    for i in range(len(gap_removed_sandbox_coordinates)):
        if is_octhogonal(gap_removed_sandbox_coordinates[i], gap[0]):
            # We have found the index, now we can insert the path into the sandbox_coordinates
            gap_fixed_sandbox_coordinates = np.insert(gap_removed_sandbox_coordinates, i + 1, path, axis=0)
            return gap_fixed_sandbox_coordinates
    # If we get here, then we have an error
    raise PathNotFoundException(
        "Error: Gap could not be filled. Found no location for it to be inserted into the sandbox coordinates. Meaning it was never a gap")


def fix_gaps(river):
    gapless_river = river.copy()

    # While we can find gaps, we will keep filling them
    while True:
        # Get the first gap
        gap = get_first_gap(gapless_river)
        # If there is no gap, then we are done
        if gap is None:
            break
        # Else we will fill the gaps
        gapless_river = fill_gap(gap, gapless_river)

    return gapless_river
def find_matches(target_coordinate, coordinates):
    matching_indices = []
    for i, coordinate in enumerate(coordinates):
        if coordinates_equals(coordinate, target_coordinate):
            matching_indices.append(i)
    return matching_indices


def coordinates_equals(a, b):
    return a[0] == b[0] and a[1] == b[1]


def remove_duplicate_coordinates(coords):
    # Verified that it keeps the order // This works wierd with Sadabasadiget, it flips every other pixel order it seems
    _, unique_idx = np.unique(coords, axis=0, return_index=True)
    unique_coords = coords[np.sort(unique_idx)]
    return unique_coords


def remove_coordinates_from_list(coordinates_to_remove, list_to_remove_from):
    # If the list to remove from is empty, then we will throw an error
    if len(list_to_remove_from) == 0:
        raise ValueError("Error: The list to remove from is empty")
    # If the list of coordinates to remove is empty, then we will return the list to remove from
    if len(coordinates_to_remove) == 0:
        return list_to_remove_from

    #  cleansed_coordinate_list must be of type np.array
    cleansed_coordinate_list = np.empty((0, 2), dtype=np.int32)

    # Loop through the list to remove from
    for coordinate in list_to_remove_from:
        # check it against the list of coordinates to remove
        # If the coordinate is in the coordinates to remove, then we will skip it
        found_in_blacklist = False
        for coordinate_to_remove in coordinates_to_remove:
            if coordinate[0] == coordinate_to_remove[0] and coordinate[1] == coordinate_to_remove[1]:
                found_in_blacklist = True
                break
        # If the coordinate is in the coordinates to remove, then we will skip it
        if found_in_blacklist:
            continue
        # Else we will add it to the cleansed list
        cleansed_coordinate_list = np.append(cleansed_coordinate_list, [coordinate], axis=0)
    # Return the cleansed list
    return cleansed_coordinate_list


def highlight_violations(highlight_img, violations):
    # Copy the image so we don't modify the original
    highlight_img = highlight_img.copy()
    # This function will take a list of violations and highlight them on the image
    # Draw object
    draw = ImageDraw.Draw(highlight_img)
    for violation in violations:
        # Draw a red pixel at the violation
        draw.point((violation[0], violation[1]), red)
    highlight_img.show()


def highlight_river(highlight_img, coordinates):
    # Copy the image so we don't modify the original
    highlight_img = highlight_img.copy()

    # This function will take a list of coordinates and highlight them on the image in a repeating pattern
    pattern = [blue, (59, 59, 255), (98, 98, 255), (137, 137, 255)]
    # Draw object
    draw = ImageDraw.Draw(highlight_img)
    index = 0
    for coordinate in coordinates:
        # Draw a pixel at the coordinate
        draw.point((coordinate[0], coordinate[1]), pattern[index % len(pattern)])
    highlight_img.show()


def highlight_point(highlight_img, coordinate, color=red):
    # Copy the image so we don't modify the original
    highlight_img = highlight_img.copy()
    # This function will take a coordinate and highlight it on the image
    # Draw object
    draw = ImageDraw.Draw(highlight_img)
    # Draw a pixel at the coordinate
    draw.point((coordinate[0], coordinate[1]), color)
    return highlight_img


def highlight_points(highlight_img, coordinates, color=red):
    # Copy the image so we don't modify the original
    highlight_img = highlight_img.copy()
    # This function will take a list of coordinates and highlight them on the image
    # Draw object
    draw = ImageDraw.Draw(highlight_img)
    for coordinate in coordinates:
        # Draw a pixel at the coordinate
        draw.point((coordinate[0], coordinate[1]), color)
    return highlight_img


def paint_and_show_explored_pixels(img, center_pixel, explored_pixels, endpoint_pixel=None):
    """ Helper function for search_for_valid_pixel_to_attach_river
    Paints the explored pixels and shows the image. If an endpoint pixel is given, it will be highlighted. The colors used are:
    red: origin pixel
    light_blue: pixels explored by the first list of pixels in the explored_pixels list
    dark_blue: pixels explored by the second list of pixels in the explored_pixels list
    green: valid endpoint pixel
    """

    # Make a copy of the image
    img_copy = img.copy()
    # Get a drawing object
    draw = ImageDraw.Draw(img_copy)

    # Highlight the region by drawing a thick red box around it at 30 pixels from the origin pixel
    draw.rectangle((center_pixel[0] - 30, center_pixel[1] - 30, center_pixel[0] + 30, center_pixel[1] + 30),
                   outline=red, width=5)

    # For the first list of pixels in the explored_pixels list, fill in every pixel with a light blue color
    for pixel in explored_pixels[0]:
        draw.point(pixel, fill=orange)
    # For the second list of pixels in the explored_pixels list, fill in every pixel with a dark blue color
    for pixel in explored_pixels[1]:
        draw.point(pixel, fill=orange)
    # Highlight the origin pixel and the valid endpoint pixel
    draw.point((center_pixel[0], center_pixel[1]), fill=red)
    # If an endpoint pixel was given, highlight it
    if endpoint_pixel:
        draw.point(endpoint_pixel, fill=purple)

    # Flip the image
    img_copy = img_copy.transpose(Image.FLIP_TOP_BOTTOM)
    # Show the image
    img_copy.show()


def paint_and_show_river_on_image(img, river_pixels, colour=orange):
    """Paints the river pixels and shows the image."""

    # Make a copy of the image
    img_copy = img.copy()
    # Get a drawing object
    draw = ImageDraw.Draw(img_copy)

    # Highlight the region by drawing a thick red box around the river
    draw.rectangle(
        (river_pixels[0][0] - 30, river_pixels[0][1] - 30, river_pixels[-1][0] + 30, river_pixels[-1][1] + 30),
        outline=red, width=5)

    # Draw the river pixels
    for pixel in river_pixels:
        draw.point((pixel[0], pixel[1]), fill=colour)

    # Flip the image
    img_copy = img_copy.transpose(Image.FLIP_TOP_BOTTOM)
    # Show the image
    img_copy.show()


def paint_and_show_river(river_pixels):
    img = draw_small_river_image(river_pixels, draw_direction=True)[0]
    img.show()
    return img

def paint_and_show_explored_path(img, closed_nodes, origin_pixel, destination_pixel):
    """
    Paints the path pixels and shows the image.
    red: origin pixel
    Orange: closed nodes
    purple: valid endpoint pixel
    """

    # Make a copy of the image
    img_copy = img.copy()
    # Get a drawing object
    draw = ImageDraw.Draw(img_copy)

    # Draw origin and destination nodes
    draw.point((origin_pixel[0], origin_pixel[1]), fill=red)
    draw.point((destination_pixel[0], destination_pixel[1]), fill=purple)

    # Draw the closed nodes (Nodes visited
    for node in closed_nodes:
        draw.point(node.pixel, fill=orange)

    # Flip the image
    img_copy = img_copy.transpose(Image.FLIP_TOP_BOTTOM)
    # Show the image
    img_copy.show()


class TributaryConnectionException(Exception):
    """Exception raised when a tributary is not connected to a river system."""


class PathNotFoundException(Exception):
    """Exception raised when a path is not found."""
    pass


class UnfixableBorderException(Exception):
    """Exception raised when a river border cannot be fixed."""
    pass


class UnfixableOverdrawException(Exception):
    """Exception raised when a river overdraw cannot be fixed."""
    pass


generate_river_files()
