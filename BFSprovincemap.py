import ast
import pandas as pd
from PIL import Image, ImageDraw

# read the Excel file
df = pd.read_excel('BFSoutput.xlsx')

def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))


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

# set up image
width, height = 8192, 4096
img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# draw each polygon
for coord, color in zip(coords, colors):
    # convert coordinates to pixel values
    coord_px = [(int((x + 180) * (width / 360)), int((y + 90) * (height / 180))) for x, y in coord]
    # draw polygon
    rgbcolor =hex_to_rgb(color)
    draw.polygon(coord_px, fill=rgbcolor, outline=None)

# save image
img.save('output.png')
