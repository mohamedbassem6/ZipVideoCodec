from PIL import Image
from pathlib import Path
import os
import cv2

ORIGINAL_WIDTH = 1920
ORIGINAL_HEIGHT = 1080
ORIGINAL_BLOCK_SIZE = 15

color_val = {
    (0, 0, 0): 0,
    (255, 0, 0): 1,
    (0, 255, 0): 2,
    (0, 0, 255): 3,
    (255, 255, 0): 4,
    (0, 255, 255): 5,
    (255, 0, 255): 6,
    (255, 255, 255): 7,
}


def fix_color(color):
    red, green, blue = color

    if red < 107:
        red = 0
    elif red > 148:
        red = 255
    else:
        raise ValueError("RED: Data is Corrupted")

    if green < 107:
        green = 0
    elif green > 148:
        green = 255
    else:
        raise ValueError("GREEN: Data is Corrupted")

    if blue < 107:
        blue = 0
    elif blue > 148:
        blue = 255
    else:
        raise ValueError("BLUE: Data is Corrupted")

    return red, green, blue


def get_color(pixels, i, j, size):
    dx = [0, 1, 0, 1, -1, 0, -1, 1, -1]
    dy = [0, 0, 1, 1, 0, -1, -1, -1, 1]

    avg_red = 0
    avg_green = 0
    avg_blue = 0

    avg_count = 9
    for k in range(9):
        x = i + dx[k]
        y = j + dy[k]

        if x >= size[0] or y >= size[1] or x < 0 or y < 0:
            avg_count -= 1
            continue

        avg_red += pixels[x, y][0]
        avg_green += pixels[x, y][1]
        avg_blue += pixels[x, y][2]

    avg_red = avg_red / avg_count
    avg_green = avg_green / avg_count
    avg_blue = avg_blue / avg_count

    return fix_color((avg_red, avg_green, avg_blue))


def read_bytes(img: Image):
    """
    This function reads the bytes from an image file.
    It takes an instance of the PIL Image class as input.
    It returns the byte data extracted from the image.
    """

    data = bytes([])  # Initialize an empty byte array to store the extracted data
    pixels = img.load()  # Load the pixels of the image

    # img.show()

    width, height = img.size  # Get the width and height of the image

    BLOCK_SIZE = width / (ORIGINAL_WIDTH / ORIGINAL_BLOCK_SIZE)  # Calculate the block size

    byte_data = ""  # Initialize an empty string to store the octal representation of the data

    j = BLOCK_SIZE / 2  # Start from the center of the first block in the vertical direction
    while j < height:
        j_tmp = round(j) if round(j) < height else height - 1
        i = (
            BLOCK_SIZE / 2
        )  # Start from the center of the first block in the horizontal direction

        while i < width:
            i_tmp = round(i) if round(i) < width else width - 1

            ref_pix = pixels[i_tmp, j_tmp]  # Get the color of the reference pixel
            # color = fix_color(ref_pix)  # Fix the color if necessary
            color = get_color(pixels, i_tmp, j_tmp, img.size)

            byte_data += str(
                color_val[color]
            )  # Append the color value to the octal string
            if len(byte_data) == 3:
                data += bytes([int(byte_data, 8)])
                byte_data = ""  # Reset the octal string

            i += BLOCK_SIZE

        j += BLOCK_SIZE

    return data  # Return the extracted byte data


def decode(video_path, destination_path):
    """
    This function decodes a video file and extracts the byte data from each frame.
    It takes the path of the video file as input and the destination path to save the extracted data.
    It uses the OpenCV library to read the video frames and the PIL library to convert each frame to an image.
    The read_bytes function is called to extract the byte data from each image frame.
    The extracted data is then saved to the specified destination path.
    """

    data = bytes()  # Initialize an empty byte array to store the extracted data

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        data += read_bytes(img)

    with open(destination_path, "wb") as file:
        file.write(data)


decode("/Users/mohamedbassem/Downloads/out15 24.mp4", "test.zip")
