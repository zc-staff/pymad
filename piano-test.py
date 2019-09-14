from argparse import ArgumentParser
from pymad.util import play
from pymad.automation import parseNodeList
from pymad.automation.actor import JsonNode
from pymad.piano import BasicPiano, LinearASDR
from pymad import synthesize, loadTrack

if __name__ == "__main__":
    parser = ArgumentParser("piano-test", description="test-piano")
    parser.add_argument("piano", help="path to piano")
    parser.add_argument("--track", default='tmp/lib/instr/test-score.json', help="path to test track")
    parser.add_argument("--out", help="path to output")
    args = parser.parse_args()

    piano, _ = parseNodeList(args.piano)
    piano.updateInput({ "track": JsonNode(args.track) })
    t = piano.execute()
    if args.out == None:
        play(t)
    else:
        t.writeWav(args.out)

