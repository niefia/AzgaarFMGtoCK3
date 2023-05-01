import json
from scaleHelper import ScaleInfo
from PIL import Image, ImageDraw


# def function called run tests that runs test
def test_scale_info():
    print("Running test to validate that Scale_Info is works as intended")

    file_location = "test.geojson"
    image_width =  8192
    image_height =  4096
    # Check if it is a file
    scale_info_object = ScaleInfo(file_location, image_width, image_height)

    # Print the minimum and maximum x and y values
    print("Can we retrieve min and max values?")
    print("Minimum x:", scale_info_object.min_x)
    print("Maximum x:", scale_info_object.max_x)
    print("Minimum y:", scale_info_object.min_y)
    print("Maximum y:", scale_info_object.max_y)
    print()
    print("scalefactor:", scale_info_object.scale_factor)
    print("X offset: ", scale_info_object.x_offset)
    print("Y offset: ", scale_info_object.y_offset)

    # make an image
    img = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(img)

    # FOr each feature in the geojson file
    with open(file_location, "r") as f:
        data = json.load(f)
    for feature in data["features"]:
        # Draw a pixel to the image
        coords = feature["geometry"]["coordinates"]
        for coord in coords:
            x, y = scale_info_object.scale_coordinate(coord)
            draw.point((x, y), fill='blue')

    # show the image
    img.show()


test_scale_info()
