from PIL import Image
from pathlib import Path
import cv2

ORIGINAL_WIDTH = 1280
ORIGINAL_HEIGHT = 720
BLOCK_SIZE = 4

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

    if red < 128:
        red = 0
    else:
        red = 255

    if green < 128:
        green = 0
    else:
        green = 255

    if blue < 128:
        blue = 0
    else:
        blue = 255

    return red, green, blue


def get_diff_color(color):
    red, green, blue = color
    return min(255 - red, red) + min(255 - green, green) + min(255 - blue, blue)


def get_color(pixels, i, j):
    min_diff = 255 * 3
    color = None

    for x in range(BLOCK_SIZE):
        for y in range(BLOCK_SIZE):
            diff = get_diff_color(pixels[i + x, j + y])
            
            if diff < min_diff:
                min_diff = diff
                color = pixels[i + x, j + y]

    return fix_color(color)


def read_bytes(img: Image):
    """
    This function reads the bytes from an image file.
    It takes an instance of the PIL Image class as input.
    It returns the byte data extracted from the image.
    """

    data = bytes([])  # Initialize an empty byte array to store the extracted data
    pixels = img.load()  # Load the pixels of the image

    width, height = img.size  # Get the width and height of the image

    byte_data = ""  # Initialize an empty string to store the octal representation of the data

    j = 0
    while j < height:
        i = 0

        while i < width:
            color = get_color(pixels, i, j)

            byte_data += str(color_val[color])  # Append the color value to the octal string
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


decode("/Users/mohamedbassem/Downloads/out4 30 720.mp4", "test.zip")
