from argparse import ArgumentParser
from pymad import writeMidi, loadTrack

if __name__ == "__main__":
    parser = ArgumentParser('write midi', description="write track to midi")
    parser.add_argument('track', help='the source track file')
    parser.add_argument('midi', help='destination')
    args = parser.parse_args()

    mid = writeMidi(loadTrack(args.track))
    mid.save(args.midi)
