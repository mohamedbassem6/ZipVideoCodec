from tqdm import tqdm
from PIL import Image
from reedsolo import RSCodec, ReedSolomonError
import numpy as np
import cv2


FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30
BLOCK_SIZE = 4

EC_BYTES = 6
MSG_BYTES = 25
RS = RSCodec(EC_BYTES)      # 15% error correction


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

        self.__frames_count = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.__progress_bar = None

        if not self.__cap.isOpened():
            print("Error: Could not open video.")
            exit()


    @staticmethod
    def __fix_color(color):
        red, green, blue = color

        if red <= 85:
            red = 0
        elif red >= 172:
            red = 255
        else:
            return None
        
        if green <= 85:
            green = 0
        elif green >= 172:
            green = 255
        else:
            return None
        
        if blue <= 85:
            blue = 0
        elif blue >= 172:
            blue = 255
        else:
            return None

        return red, green, blue
    

    @staticmethod
    def __get_hamming_dist(color):
        red, green, blue = color
        return min(255 - red, red) + min(255 - green, green) + min(255 - blue, blue)
    

    def __get_color(self, pixels, i, j):
        min_diff = 255 * 3
        color = None

        for x in range(BLOCK_SIZE):
            for y in range(BLOCK_SIZE):
                diff = self.__get_hamming_dist(pixels[i + x, j + y])
                
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
        message = []
        corrupted = False

        j = 0
        while j < self.__height:

            i = 0
            while i < self.__width:
                color = self.__get_color(pixels, i, j)
                if color is None:
                    corrupted = True
                    color = (0, 0, 0)

                byte_data += str(DecoderEngine.color_val[color])  # Append the color value to the octal string
                if len(byte_data) == 3:
                    self.__progress_bar.update(1)

                    message.append(int(byte_data, 8))
                    byte_data = ""  # Reset the octal string

                if len(message) == MSG_BYTES:
                    if corrupted:
                        try:
                            data += RS.decode(message)[0]
                        except ReedSolomonError:
                            print("Error: Data is corrupted, and can't be decoded.")
                            exit()
                    else:
                        data += bytes(message[:MSG_BYTES - EC_BYTES])

                    corrupted = False
                    message = []

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

        print()
        self.__progress_bar = tqdm(total=(self.__frames_count * ((FRAME_HEIGHT * FRAME_WIDTH) / (BLOCK_SIZE ** 2)) / 3), desc="Decoding", unit="byte", unit_scale=True)
        
        while True:
            ret, frame = self.__cap.read()

            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            self.__data += self.__read_bytes(img)

        self.__cap.release()

        with open(self.__destination_path, "wb") as file:
            file.write(self.__data)

        self.__progress_bar.close()
        print()


class EncoderEngine():
    color = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]

    def __init__(self, file_path, video_name):
        self.__video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'avc1'), FPS, (FRAME_WIDTH, FRAME_HEIGHT))

        self.__file_bytes = self.__read_file(file_path)
        # self.__frames_count = ceil((len(self.__file_bytes) * 3) / (FRAME_WIDTH * FRAME_HEIGHT / (BLOCK_SIZE ** 2)))

        self.__img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT))
        self.__pixels = self.__img.load()

        self.__progress_bar = None


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
        print()
        self.__progress_bar = tqdm(total=len(self.__file_bytes) + (len(self.__file_bytes) * EC_BYTES / (MSG_BYTES - EC_BYTES)), desc="Encoding", unit="byte", unit_scale=True)
        
        i, j, k = 0, 0, 0
        for m in range(0, len(self.__file_bytes), MSG_BYTES - EC_BYTES):
            data = self.__file_bytes[m:m + MSG_BYTES - EC_BYTES]
            encoded_data = RS.encode(data)

            for byte in encoded_data:
                self.__progress_bar.update(1)

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
        print()
