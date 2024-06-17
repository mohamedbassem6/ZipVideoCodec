from PIL import Image
from pathlib import Path
import os

ORIGINAL_WIDTH = 1920
ORIGINAL_HEIGHT = 1080
ORIGINAL_BLOCK_SIZE = 8

color_val = {
    (0, 0, 0):   0,
    (255, 0, 0): 1,
    (0, 255, 0): 2,
    (0, 0, 255): 3,
    (255, 255, 0): 4,
    (0, 255, 255): 5,
    (255, 0, 255): 6,
    (255, 255, 255): 7
}


def fix_color(color):
    red, green, blue = color

    if red < 107:
        red = 0
    elif red > 148:
        red = 255
    else:
        raise ValueError("Data is Corrupted")

    if green < 107:
        green = 0
    elif green > 148:
        green = 255
    else:
        raise ValueError("Data is Corrupted")

    if blue < 107:
        blue = 0
    elif blue > 148:
        blue = 255
    else:
        raise ValueError("Data is Corrupted")

    return red, green, blue


# This function reads the bytes from an image file.
# It takes the path of the image file as input.
# It returns the byte data extracted from the image.

def read_bytes(image_path):
    # file = open("testing_output.txt", "w")
    data = bytes([])  # Initialize an empty byte array to store the extracted data
    img = Image.open(image_path, "r")  # Open the image file
    pixels = img.load()  # Load the pixels of the image

    width, height = img.size  # Get the width and height of the image

    BLOCK_SIZE = width / (ORIGINAL_WIDTH / ORIGINAL_BLOCK_SIZE)  # Calculate the block size

    byte_data = ""  # Initialize an empty string to store the octal representation of the data

    j = BLOCK_SIZE / 2  # Start from the center of the first block in the vertical direction
    while j < height:
        j_tmp = round(j)
        i = BLOCK_SIZE / 2  # Start from the center of the first block in the horizontal direction

        while i < width:
            i_tmp = round(i)

            ref_pix = pixels[i_tmp, j_tmp]  # Get the color of the reference pixel
            color = fix_color(ref_pix)  # Fix the color if necessary

            byte_data += str(color_val[color])  # Append the color value to the octal string
            if len(byte_data) == 3:
                data += bytes([int(byte_data, 8)])
                byte_data = ""  # Reset the octal string

            i += BLOCK_SIZE

        j += BLOCK_SIZE

    return data  # Return the extracted byte data


def decode(directory_path, destination_path):
    data = bytes()  # Initialize an empty byte array to store the extracted data

    directory = Path(directory_path)
    if not directory.is_dir():
        raise NotADirectoryError("The specified path is not a directory")
    
    files = [file.name for file in directory.iterdir() if file.suffix == ".png"]
    files.sort(key=lambda x: int(Path(x).stem))
    for file in files:
        file_path = os.path.join(directory_path, file)
        data += read_bytes(file_path)

    with open(destination_path, "wb") as file:
        file.write(data)

decode("frames_octal_8", "test.zip")
