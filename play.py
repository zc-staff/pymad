from argparse import ArgumentParser
from pymad import readWav
from pymad.play import play

if __name__ == "__main__":
    parser = ArgumentParser("play", description="play wav")
    parser.add_argument("wav", help="wav path")
    args = parser.parse_args()
    play(readWav(args.wav))
