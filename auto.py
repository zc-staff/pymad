from argparse import ArgumentParser
from pymad.util import play
from pymad.automation import parseNodeList

if __name__ == "__main__":
    parser = ArgumentParser("auto", description="auto")
    parser.add_argument("script", help="path to scipt")
    parser.add_argument("--out", help="path to output")
    args = parser.parse_args()

    piano, _ = parseNodeList(args.script)
    t = piano.execute()
    if args.out == None:
        play(t)
    else:
        t.writeWav(args.out)

