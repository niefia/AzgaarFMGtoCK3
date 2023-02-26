import random



#converts hex to rgb
def hex_to_rgb(hex_color):
    if not hex_color.startswith("#") or len(hex_color) != 7:
        return None
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

def bfs_hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))



def color_gen():
    # Generates a random RGB color
    return "#{:02x}{:02x}{:02x}".format(*(random.randint(0, 255) for _ in range(3)))