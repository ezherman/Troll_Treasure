from argparse import ArgumentParser
from troll_treasure.commands import Dungeon, Game

def process():
    parser = ArgumentParser(description="Run a single Dungeon game or calculate outcome probabilities")

    # required (positional) arguments
    parser.add_argument("yml")              # path to yml file
    parser.add_argument("--probabilities", "-p", 
                        action = "store_true")  # game or probabilities

    args = parser.parse_args()

    d = Dungeon.from_file(args.yml)

    if args.probabilities:
        print(Game(d).probability(max_steps = 10))
    
    else:
        print(Game(d).run(max_steps = 10))


if __name__ == "__main__":
    process()
