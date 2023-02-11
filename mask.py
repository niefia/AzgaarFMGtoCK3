from PIL import Image
import numpy as np

def apply_mask(img, mask):
    masked_img = np.zeros_like(img)
    masked_img[mask == 255] = img[mask == 255]
    return masked_img

# Load the input image and the mask image
img = Image.open("voronoi_diagram.png")
mask = Image.open("mask.png").convert("L")

# Resize the mask image to the same size as the input image
mask = mask.resize(img.size)

# Convert the images to numpy arrays
img = np.array(img)
mask = np.array(mask)

# Apply the mask to the input image
masked_img = apply_mask(img, mask)

# Convert the masked image back to PIL image
masked_img = Image.fromarray(masked_img)

# Save the output image
masked_img.save("output_image.png")
