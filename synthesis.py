from argparse import ArgumentParser
from pymad import readWav, synthesize, load_track
from pymad.piano import Sampler, PianoCache, BasicPiano

if __name__ == "__main__":
    parser = ArgumentParser("synthesis", description="synthesis track")
    parser.add_argument("track", help="track path")
    parser.add_argument("output", help="output wav path")
    parser.add_argument("-p", "--pitch", type=float, default=0, help="pitch offset in semitone")
    parser.add_argument("-v", "--volume", type=float, default=0, help="volume offset in dB")
    parser.add_argument("-l", "--length", type=float, default=1, help="note length ratio")
    parser.add_argument("-s", "--speed", type=float, default=1, help="speed ratio")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress log output")
    gp = parser.add_mutually_exclusive_group(required=True)
    gp.add_argument("--sampler", type=str, help="use a sampler", default=None)
    gp.add_argument("--basic", type=str, help="use a basic synthesizer", choices=['sin', 'square', 'sawtooth', 'triangle'], default=None)
    args = parser.parse_args()

    if args.sampler == None:
        piano = BasicPiano(44100, mode=args.basic)
    else:
        x = readWav(args.sampler)
        piano = Sampler(x, pitch_ratio=2 ** (args.pitch / 12))
    piano = PianoCache(piano)
    t = load_track(args.track)
    seq = synthesize(piano, t, len_ratio=args.length, speed_ratio=args.speed, vol_ratio=10 ** (args.volume / 10), quiet=args.quiet)
    seq.writeWav(args.output)
