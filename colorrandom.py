import json
import random



def color_gen():
    # Generates a random RGB color
    return "#{:02x}{:02x}{:02x}".format(*(random.randint(0, 255) for _ in range(3)))


def convert_geojson(input_file, output_file):
    with open(input_file) as f:
        data = json.load(f)

    for feature in data['features']:
        feature['properties']['color'] = color_gen()

    with open(output_file, 'w') as f:
        json.dump(data, f)


input_file = "input.geojson"
output_file = "output.geojson"
convert_geojson(input_file, output_file)