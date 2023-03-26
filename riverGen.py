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
light_blue = (173, 216, 230)
green = (0, 255, 0)
magenta = (255, 0, 128)
white = (255, 255, 255)
red = (255, 0, 0)

# Declare a debug variable
debug = True
orange = (255, 165, 0)
brown = (165, 42, 42)
purple = (128, 0, 128)


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


# Custom ExceptionClass for when a path is not found
class PathNotFoundException(Exception):
    pass


# Function to paint the explored pixels
def paint_and_show_explored_pixels(img, center_pixel, explored_pixels, endpoint_pixel=None):
    """Paints the explored pixels and shows the image. If an endpoint pixel is given, it will be highlighted. The colors used are:
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

def paint_and_show_river(img, river_pixels, colour = orange):
    """Paints the river pixels and shows the image."""

    # Make a copy of the image
    img_copy = img.copy()
    # Get a drawing object
    draw = ImageDraw.Draw(img_copy)

    #Highlight the region by drawing a thick red box around the river
    draw.rectangle((river_pixels[0][0] - 30, river_pixels[0][1] - 30, river_pixels[-1][0] + 30, river_pixels[-1][1] + 30),
                     outline=red, width=5)

    # Draw the river pixels
    for pixel in river_pixels:
        draw.point((pixel[0],pixel[1]), fill=colour)

    # Flip the image
    img_copy = img_copy.transpose(Image.FLIP_TOP_BOTTOM)
    # Show the image
    img_copy.show()

def draw_small_river_image(river_pixels):
    min_x = int(np.min(river_pixels[:, 0]))
    max_x = int(np.max(river_pixels[:, 0]))
    min_y = int(np.min(river_pixels[:, 1]))
    max_y = int(np.max(river_pixels[:, 1]))

    # Create a new image that is the max_x and max y in size
    padding = 4
    river_img = Image.new("RGB", (max_x - min_x + padding, max_y - min_y + padding), color=white)
    # Copy the draw_coords to a new array.
    self_check_coords = river_pixels.copy()
    # Offset the coordinates so that they are relative to the river_img + padding
    self_check_coords[:, 0] -= min_x - padding / 2
    self_check_coords[:, 1] -= min_y - padding / 2

    # Draw the river to the river_img
    draw = ImageDraw.Draw(river_img)
    for pixel in self_check_coords:
        draw.point((pixel[0], pixel[1]), fill=blue)
    # Return the image and the self_check_coords
    return river_img, self_check_coords

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
    draw.point((destination_pixel[0] , destination_pixel[1]), fill=purple)

    # Draw the closed nodes (Nodes visited
    for node in closed_nodes:
        draw.point(node.pixel, fill=orange)

    # Flip the image
    img_copy = img_copy.transpose(Image.FLIP_TOP_BOTTOM)
    # Show the image
    img_copy.show()

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
            paint_and_show_explored_path(img, closed_nodes, origin_pixel, destination_pixel)
            raise PathNotFoundException("Max number of pixels visited during pathfinding.")
        # Throw an exception if there are no more nodes to visit
        if len(open_nodes) == 0:
            paint_and_show_explored_path(img, closed_nodes, origin_pixel, destination_pixel)
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
            if check_number_of_surrounding_color(img, pixel, blue) > 1:
                neighboring_pixels.remove(pixel)
        # For each neighboring pixel
        for pixel in neighboring_pixels:
            # Create a node for the pix, calculate the h value to be the sum of teh x and y distance to the destination.
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
            paint_and_show_explored_pixels(img, origin_pixel, (visited_pixels, recently_visited_pixels))
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
    return violations


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
def get_first_gap(sandbox_coordinates):
    # This function will take a list of coordinates and return the first gap that is found
    # A gap has two anchor points, the first pixel in the gap and the last pixel in the gap
    # The anchor points are known valid pixels, but the pixels in between are not
    # The gap will be returned as a tuple of two coordinates

    # If no gap is found, then the function will return None
    gap = None
    # Loop through the coordinates and find the first gap
    for i in range(len(sandbox_coordinates) - 1):
        # If the next coordinate is not one pixel away from the current coordinate
        if not is_octhogonal(sandbox_coordinates[i], sandbox_coordinates[i + 1]):
            # We have found a gap
            gap = (sandbox_coordinates[i], sandbox_coordinates[i + 1])
            break
    return gap



def fill_gap(gap, sandbox_coordinates):
    # This function will take a gap and fill it in using path finding

    # First we must trim the gap from the sandbox coordinates
    # Cast the gap to a numpy array, so we can use numpy functions
    gap_removed_sandbox_coordinates = remove_coordinates_from_list(np.array(gap), sandbox_coordinates)

    # Then we must generate an image for the algorithm to work on
    path_image, _ = draw_small_river_image(gap_removed_sandbox_coordinates)

    # Then we must find a path between the two anchor points
    path = pathfind_from_a_to_b(path_image, gap[0], gap[1])

    # Then we must add the path into the sandbox coordinates at the gap
    # We find where this is by looking for the first coordinate in the sandbox_coordinate that is octhogonal to the first anchor point
    for i in range(len(gap_removed_sandbox_coordinates)):
        if is_octhogonal(gap_removed_sandbox_coordinates[i], gap[0]):
            # We have found the index, now we can insert the path into the sandbox_coordinates
            gap_fixed_sandbox_coordinates = np.insert(gap_removed_sandbox_coordinates, i + 1, path, axis=0)
            break
    return gap_fixed_sandbox_coordinates



def fix_self_violations(original_coordinates):
    was_altered = False
    # Convert to local coordinates and draw a sandbox image
    sandbox_img, fixed_sandbox_coordinates = draw_small_river_image(original_coordinates)

    # Try to clear the river, if it fails go into a loop where we try to fix the river
    while True:
        # First we will check if we can find any gaps in the river
        gap = get_first_gap(fixed_sandbox_coordinates)
        # If a gap is not found, then we will look for self violations
        if gap is None:
            # ie, any pixel that isn't bordering exactly 2 blue pixels
            sandbox_img, _ = draw_small_river_image(fixed_sandbox_coordinates)
            violations = river_self_violations_exclude_ends(sandbox_img, fixed_sandbox_coordinates)
            print("Found " + str(len(violations)) + " self violations")
            if len(violations) == 0:
            # If there are no gaps and no violations, then we are done
                break

        # Remove coordinates that are violations from the sandbox coordinates
        fixed_sandbox_coordinates = remove_coordinates_from_list(violations, fixed_sandbox_coordinates)
        # Find the first contiguous gap in the river
        gap = get_first_gap(fixed_sandbox_coordinates)

        # If no gap is found, then we have a problem
        if gap is None:
            raise PathNotFoundException("Error: No gap found in river path but "
                                        + str(len(violations)) + " violations was found.")
        # Else we will try to fill the gap
        fixed_sandbox_coordinates = fill_gap(gap, fixed_sandbox_coordinates)

    # Correct the coordinates to be in global coordinates
    # Find the min x and y values of the original coordinates
    min_x = np.min(original_coordinates[:, 0])
    min_y = np.min(original_coordinates[:, 1])

    # Add the min x and y values to the coordinates
    fixed_sandbox_coordinates[:, 0] += min_x
    fixed_sandbox_coordinates[:, 1] += min_y

    # Return the fixed coordinates
    return fixed_sandbox_coordinates




def remove_coordinates_from_list(coordinates_to_remove, list_to_remove_from):
    #  cleansed_coordinate_list must be of type np.array
    cleansed_coordinate_list = np.empty((0, 2), dtype=np.int32)

    # Loop through the list to remove from
    for coordinate in list_to_remove_from:
        # If the coordinate is not in the coordinates to remove, then add it to the cleansed list
        if not np.any(np.all(coordinates_to_remove == coordinate, axis=1)):
            cleansed_coordinate_list = np.append(cleansed_coordinate_list, [coordinate], axis=0)
    # Return the cleansed list
    return cleansed_coordinate_list


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

        # Check that the river is not empty
        if len(draw_coords) == 0:
            # Print out an error message and continue to the next river
            print("River is empty, skipping to next river")
            print("=============================================")
            continue

        # Remove cordinates that are above the ocean (except for some)
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

                # Remove the last pixel from the river
                draw_coords = draw_coords[:-1]
                # Check if the river is now valid
                would_draw_over_another_river = False
                for pixel in draw_coords:
                    if img.getpixel((pixel[0], pixel[1])) == blue:
                        would_draw_over_another_river = True
                        # print("The river is still invalid, trying to fix it.")
                        break
        print("The river passed the direct overdraw check.")

        # Time to correct the border
        # If the rivers does not have valid borders,
        # then we will start subtracting pixels from the end of the river
        # until we have a valid river
        has_invalid_border = False
        for pixel in draw_coords: #TODO: Reverse the order of the pixels, the issue is more likely to be at the start of the river
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
                print("=============================================")
                break
            # Check if the river is now valid
            has_invalid_border = False
            for pixel in draw_coords:
                if not check_if_valid_border(img, pixel):
                    has_invalid_border = True
                    print("Still invalid borders, trying to fix it.")
                    break
        print("The river passed the border check.")

        if river_parent != 0:
            # If the river is a tributary, we must now make sure that it is connected to the source river in a valid way
            if not tributary_endpoint_is_valid(img, draw_coords[-1]):
                print("This tributary is not connected to the source river in a valid way, trying to fix it.")
                # First, we will remove the last pixel from the river until we have more room to work with
                while not pixel_has_room_to_expand(img, draw_coords[-1]):
                    # Remove the last pixel from the river
                    # if this was the last pixel in the river, then we will abort this river
                    if len(draw_coords) < 1:
                        print("Could not fix the river, skipping to next river")
                        print("=============================================")
                        break
                    # Remove the last pixel from the river
                    draw_coords = draw_coords[:-1]
                # Now that we have more room to work with, we will try to find a valid pixel to attach the river to
                try:
                    new_endpoint = search_for_valid_pixel_to_attach_river(img, draw_coords[-1])
                except PathNotFoundException:
                    print("Could not find a valid pixel to attach the tributary to, skipping to next river")
                    print("=============================================")
                    break

                # Print out the position of the new endpoint
                print("Found a new endpoint at " + str(new_endpoint))

                # If we could not find a valid pixel to attach the river to, then we will abort this river
                if new_endpoint is None:
                    print("Could not find a valid pixel to attach the river to, skipping to next river")
                    print("=============================================")
                    # TODO: When a river is skipped, it should be added to a list of skipped rivers, so that we can
                    #       try to fix them after other rivers have been drawn.
                    break
                # If we found a valid pixel to attach the river to, then we will path to it
                else:
                    # Path to the new endpoint
                    path = pathfind_from_a_to_b(img, draw_coords[-1], new_endpoint)
                    # Add the path to the river
                    draw_coords = np.concatenate((draw_coords, path))
                    print("Pathfound to the new endpoint successfully.")
        print("The river passed the tributary is connected check.")

        # Finally, check the river against itself to make sure that it is valid
        # We wil remove invalid pixels from teh river, and fill the gaps with a path
        draw_coords = fix_self_violations(draw_coords)
        print("The river passed the self check.")


        # Draw the river to the map
        try:
            draw.line(sum(draw_coords.tolist(), []), fill=blue)  # draw the river line
        except:
            # The draw.line function will throw an error if the river is too short
            # If the river is too short, then we will skip it
            print("The river " + river_name + " is too short (1 pixel), skipping to next river")
            print("=============================================")

        # If the river has 0 as a parent id, then it is a source river
        if river_parent == 0:
            draw.point(draw_coords[0].tolist(), fill=green)  # Recolours the starting point of the river
        else:
            # If the river has a parent id, then it is a tributary. So we change the last pixel to red
            draw.point(draw_coords[-1].tolist(), fill=red)  # Recolours the end point of the river

        # TODO: Error checking the area around the river to make sure all pixels are valid

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")
    # System open the image for debug purposes
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
# correct_rivermap(path + "rivermap_mainstreams.png", path + "rivermap_corrected.png")
# mask_landsea(path + "rivermap_corrected.png", path + "landsea.png", path + "rivermap_masked.png")
# check_image_for_more_than_two_blue(path + "rivermap_masked.png")
