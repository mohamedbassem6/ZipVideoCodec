from PIL import Image
import numpy as np
import cv2


FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30
BLOCK_SIZE = 4


class DecoderEngine():
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


    def __init__(self, video_path, destination_path):
        self.__destination_path = destination_path
        self.__data = bytes()

        self.__cap = cv2.VideoCapture(video_path)
        self.__width = int(self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.__height = int(self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if not self.__cap.isOpened():
            print("Error: Could not open video.")
            exit()


    @staticmethod
    def __fix_color(color):
        red, green, blue = color

        red = 0 if red < 128 else 255
        green = 0 if green < 128 else 255
        blue = 0 if blue < 128 else 255

        return red, green, blue
    

    @staticmethod
    def __get_diff_color(color):
        red, green, blue = color
        return min(255 - red, red) + min(255 - green, green) + min(255 - blue, blue)
    

    def __get_color(self, pixels, i, j):
        min_diff = 255 * 3
        color = None

        for x in range(BLOCK_SIZE):
            for y in range(BLOCK_SIZE):
                diff = self.__get_diff_color(pixels[i + x, j + y])
                
                if diff < min_diff:
                    min_diff = diff
                    color = pixels[i + x, j + y]

        return self.__fix_color(color)
    

    def __read_bytes(self, img: Image):
        """
        This function reads the bytes from an image file.
        It takes an instance of the PIL Image class as input.
        It returns the byte data extracted from the image.
        """
    
        pixels = img.load()
        data = bytes()

        byte_data = ""

        j = 0
        while j < self.__height:
            i = 0

            while i < self.__width:
                color = self.__get_color(pixels, i, j)

                byte_data += str(DecoderEngine.color_val[color])  # Append the color value to the octal string
                if len(byte_data) == 3:
                    data += bytes([int(byte_data, 8)])
                    byte_data = ""  # Reset the octal string

                i += BLOCK_SIZE

            j += BLOCK_SIZE

        return data  # Return the extracted byte data
    

    def decode(self):
        """
        This function decodes a video file and extracts the byte data from each frame.
        It takes the path of the video file as input and the destination path to save the extracted data.
        It uses the OpenCV library to read the video frames and the PIL library to convert each frame to an image.
        The read_bytes function is called to extract the byte data from each image frame.
        The extracted data is then saved to the specified destination path.
        """

        while True:
            ret, frame = self.__cap.read()

            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            self.__data += self.__read_bytes(img)

        with open(self.__destination_path, "wb") as file:
            file.write(self.__data)


class EncoderEngine():
    color = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]

    def __init__(self, file_path, video_name):
        self.__video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'avc1'), FPS, (FRAME_WIDTH, FRAME_HEIGHT))

        self.__file_bytes = self.__read_file(file_path)
        # self.__frames_count = ceil((len(self.__file_bytes) * 3) / (FRAME_WIDTH * FRAME_HEIGHT / (BLOCK_SIZE ** 2)))

        self.__img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT))
        self.__pixels = self.__img.load()


    def __read_file(self, file_path):
        with open(file_path, "rb") as file:
            binary_data = file.read()

        return binary_data
    

    @staticmethod
    def __byte_to_octal(byte):
        octal_string = oct(byte)

        # Remove the '0o' prefix added to octal literals
        octal_string = octal_string[2:]

        octal_string = octal_string.zfill(3)

        return octal_string
    

    def encode(self):
        i, j, k = 0, 0, 0
        for byte in self.__file_bytes:
            octal_byte = EncoderEngine.__byte_to_octal(byte)

            for digit in octal_byte:
                if i > FRAME_WIDTH - BLOCK_SIZE:
                    i = 0
                    j += BLOCK_SIZE

                if j > FRAME_HEIGHT - BLOCK_SIZE:
                    j = 0
                    k += 1

                    frame = np.array(self.__img)
                    self.__video.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    self.__img.close()

                    self.__img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT))
                    self.__pixels = self.__img.load()

                color_value = EncoderEngine.color[ord(digit) - ord('0')]

                for x in range(BLOCK_SIZE):
                    for y in range(BLOCK_SIZE):
                        self.__pixels[i + x, j + y] = color_value
                        
                i += BLOCK_SIZE

        frame = np.array(self.__img)
        self.__video.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        self.__img.close()

        self.__video.release()
