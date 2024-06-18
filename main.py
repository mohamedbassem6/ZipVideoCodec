from zvt import DecoderEngine, EncoderEngine

encoder = EncoderEngine("Complete-Works-of-William-Shakespeare.zip", "out4_30_720.mp4")
encoder.encode()

# decoder = DecoderEngine("/Users/mohamedbassem/Downloads/out4 30 720.mp4", "test.zip")
# decoder.decode()