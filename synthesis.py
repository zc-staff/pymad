from argparse import ArgumentParser
from pymad import readWav, synthesize, load_track
from pymad.piano import Sampler, PianoCache

if __name__ == "__main__":
    parser = ArgumentParser("synthesis", description="synthesis track")
    parser.add_argument("source", help="source wav path")
    parser.add_argument("track", help="track path")
    parser.add_argument("output", help="output wav path")
    parser.add_argument("-p", "--pitch", type=float, default=0, help="pitch offset in semitone")
    parser.add_argument("-v", "--volume", type=float, default=0, help="volume offset in dB")
    parser.add_argument("-l", "--length", type=float, default=1, help="note length ratio")
    parser.add_argument("-s", "--speed", type=float, default=1, help="speed ratio")
    parser.add_argument("-f", "--filter", type=float, default=4, help="ratio for the comb filter, advanced use")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress log output")
    args = parser.parse_args()

    x = readWav(args.source)
    piano = PianoCache(Sampler(x, filter_ratio=args.filter, pitch_ratio=2 ** (args.pitch / 12)))
    t = load_track(args.track)
    seq = synthesize(piano, t, len_ratio=args.length, speed_ratio=args.speed, vol_ratio=10 ** (args.volume / 10), quiet=args.quiet)
    seq.writeWav(args.output)
