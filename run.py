import argparse
from zvc import EncoderEngine, DecoderEngine


parser = argparse.ArgumentParser(
    description="A program to encode zip files to videos, or decode videos to zip files.",
    epilog="Example usage: python run.py -e source.zip destination.mp4"
)

# Add the mutually exclusive group for -e and -d
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-e', '--encode', action='store_true', help='Encode the source file to the destination file')
group.add_argument('-d', '--decode', action='store_true', help='Decode the source file to the destination file')

# Add arguments for source and destination files
parser.add_argument('source', type=str, help='The path to the source file')
parser.add_argument('destination', type=str, help='The path to the destination file')

# Parse the arguments
args = parser.parse_args()

# Perform encoding or decoding based on the arguments
if args.encode:
    encoder_engine = EncoderEngine(args.source, args.destination)
    encoder_engine.encode()
elif args.decode:
    decoder_engine = DecoderEngine(args.source, args.destination)
    decoder_engine.decode()
