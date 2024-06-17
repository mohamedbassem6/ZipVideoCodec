from math import ceil
from PIL import Image
import os

BLOCK_SIZE = 8
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

color = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]


def clear_screen():
    if os.name == 'posix':  # Unix-based systems
        os.system('clear')
    elif os.name == 'nt':  # Windows
        os.system('cls')


def read_file(file_path):
    with open(file_path, "rb") as file:
        binary_data = file.read()

    return binary_data


def byte_to_octal(byte):
    octal_string = oct(byte)

    # Remove the '0o' prefix added to octal literals
    octal_string = octal_string[2:]

    octal_string = octal_string.zfill(3)

    return octal_string


def encode_octal_rgb(file_path, dest_directory):
    file_bytes = read_file(file_path)

    frames_count = ceil((len(file_bytes) * 3) / (FRAME_WIDTH * FRAME_HEIGHT / (BLOCK_SIZE ** 2)))
    print(f"FRAMES COUNT: {frames_count}")

    img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT))
    pixels = img.load()

    i, j, k = 0, 0, 0
    for byte in file_bytes:
        octal_byte = byte_to_octal(byte)

        for nibble in octal_byte:
            if i > FRAME_WIDTH - BLOCK_SIZE:
                i = 0
                j += BLOCK_SIZE

            if j > FRAME_HEIGHT - BLOCK_SIZE:
                j = 0
                k += 1

                img.save(os.path.join(dest_directory, f"{k}.png"))
                img.close()

                img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT))
                pixels = img.load()

            color_value = color[ord(nibble) - ord('0')]

            for x in range(BLOCK_SIZE):
                for y in range(BLOCK_SIZE):
                    pixels[i + x, j + y] = color_value
            i += BLOCK_SIZE

    img.save(os.path.join(dest_directory, f"{k + 1}.png"))
    img.close()
