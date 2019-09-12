from argparse import ArgumentParser
from pymad.play import play
from pymad.automation import parseNodeList
from pymad.automation.actor import JsonNode

if __name__ == "__main__":
    parser = ArgumentParser("piano-test", description="test-piano")
    parser.add_argument("piano", help="path to piano")
    parser.add_argument("--track", default='tmp/lib/instr/test-score.json', help="path to test track")
    args = parser.parse_args()

    piano, _ = parseNodeList(args.piano)
    piano.updateInput({ "track": JsonNode(args.track) })
    play(piano.execute())
