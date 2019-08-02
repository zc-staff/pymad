from argparse import ArgumentParser
from pymad import dump_midi

if __name__ == "__main__":
    parser = ArgumentParser('dump_midi', description="dump midi to track json")
    parser.add_argument('midi', help='the source midi file')
    parser.add_argument('prefix', help='destination prefix to store json')

    args = parser.parse_args()
    dump_midi(args.source, args.prefix)
