from argparse import ArgumentParser
from pymad import loadTrack, synthesize
from pymad.piano import loadDrum

if __name__ == "__main__":
    parser = ArgumentParser("drum", description="synthesis drum track")
    parser.add_argument("track", help="track path")
    parser.add_argument("output", help="output wav path")
    parser.add_argument("-o", "--orchestra", action="append", nargs=2, metavar=("id", "path"), help="add an orchestra")
    parser.add_argument("-v", "--volume", type=float, default=0, help="volume offset in dB")
    parser.add_argument("-s", "--speed", type=float, default=1, help="speed ratio")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress log output")
    args = parser.parse_args()

    drums = {}
    for o in args.orchestra:
        drums[int(o[0])] = o[1]
    drum = loadDrum(drums)
    t = loadTrack(args.track)

    seq = synthesize(drum, t, speedRatio=args.speed, volRatio=10 ** (args.volume / 10), quiet=args.quiet)
    seq.writeWav(args.output)

