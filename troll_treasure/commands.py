def direction(point_a, point_b):
    """
    Returns the direction from point_a to point_b, or None if they
    are not neighhbouring grid points.
    """
    if point_b == point_a:
        return "nowhere"
    if point_b[1] == point_a[1]:
        if point_b[0] == point_a[0] - 1:
            return "left"
        if point_b[0] == point_a[0] + 1:
            return "right"
    if point_b[0] == point_a[0]:
        if point_b[1] == point_a[1] - 1:
            return "up"
        if point_b[1] == point_a[1] + 1:
            return "down"

    return None

class Room:
    def __init__(self, point, links=None):
        self.point = tuple(point)  # grid point of this room
        self.links = links  # other rooms this rooms connects to
        self._validate_links()

    def __contains__(self, point):
        """
        `(x, y) in room_instance` returns `True` if `room_instance` has a link to
        a room at point `(x, y)`
        """
        return point in [link.point for link in self.links]

    def _validate_links(self):
        """
        Verifies all linked rooms are at neighbouring grid points
        """
        if not self.links:
            return
        for link in self.links:
            if not direction(self.point, link.point):
                raise ValueError(
                    f"Invalid link: {link.point} is not connected to {self.point}"
                )

class Rooms:
    """
    Collection of rooms
    """

    def __init__(self, rooms):
        # rooms dictionary keyed by (x, y) coordinate (grid cell indices)
        self.rooms = {r.point: r for r in rooms}

    def __iter__(self):
        """
        Allows Rooms objects to be iterated over (see Module 7)
        """
        return iter(self.rooms.values())

    def __getitem__(self, point):

        """
        rooms[(x, y)] will retrieve the room at coordinate (x, y) (where
        rooms is an instance of the Rooms class)
        """
        return self.rooms[point]

    def __contains__(self, point):
        """
        (x, y) in rooms will return True if a room at coordinates (x, y)
        is in rooms (where rooms is an instance of the Rooms class)
        """
        return point in self.rooms

    @classmethod
    def from_list(cls, room_list):
        rooms = [
            Room(room["point"], [Room(link) for link in room["links"]])
            for room in room_list
        ]
        return cls(rooms)

class Treasure:
    def __init__(self, point, symbol):
        self.point = tuple(point)  # (x, y) grid location of the treasure
        self.symbol = symbol  # single char symbol to show the treasure on dungeon maps

    @classmethod
    def from_dict(cls, treasure_dict):
        return cls(treasure_dict["point"], treasure_dict["symbol"])

class Agent:
    """
    Base functionality to create and load (but not move) an Agent
    """

    def __init__(self, point, name, symbol, verbose=True, allow_wait=True, **kwargs):
        self.point = tuple(point)  # (x, y) grid location of the agent
        self.name = name  # e.g. adventurer or troll
        self.symbol = symbol  # single char symbol to show the agent on dungeon maps
        self.verbose = verbose  # print output on agent behaviour if True
        self.allow_wait = allow_wait  # allow the agent to move nowhere

    def move(self, rooms):
        raise NotImplementedError("Use an Agent base class")

    @classmethod
    def from_dict(cls, agent_dict):
        return cls(
            agent_dict["point"],
            agent_dict["name"],
            agent_dict["symbol"],
            allow_wait=agent_dict["allow_wait"],
        )

import random


class RandomAgent(Agent):
    """
    Agent that makes random moves
    """

    def move(self, rooms):
        if not rooms[self.point].links:
            # this room isn't linked to anything, can't move
            if self.verbose:
                print(f"{self.name} is trapped")
            return

        # pick a random room to move to
        options = rooms[self.point].links
        if self.allow_wait:
            options.append(self)
        new_room = random.choice(options)

        if self.verbose:
            move = direction(self.point, new_room.point)
            print(f"{self.name} moves {move}")
        self.point = new_room.point

class HumanAgent(Agent):
    """
    Agent that prompts the user where to move next
    """

    def move(self, rooms):
        if not rooms:
            if self.verbose:
                print(f"{self.name} is trapped")
            return
        # populate movement options depending on available rooms
        if self.allow_wait:
            options = ["wait"]
        else:
            options = []
        if (self.point[0] - 1, self.point[1]) in rooms:
            options.append("left")
        if (self.point[0] + 1, self.point[1]) in rooms:
            options.append("right")
        if (self.point[0], self.point[1] - 1) in rooms:
            options.append("up")
        if (self.point[0], self.point[1] + 1) in rooms:
            options.append("down")

        # prompt user for movement input
        choice = None
        while choice not in options:
            choice = input(f"Where will {self.name} move \n{options}? ")

        # move the agent
        if choice == "left":
            self.point = (self.point[0] - 1, self.point[1])
        elif choice == "right":
            self.point = (self.point[0] + 1, self.point[1])
        elif choice == "up":
            self.point = (self.point[0], self.point[1] - 1)
        elif choice == "down":
            self.point = (self.point[0], self.point[1] + 1)

import yaml


class Dungeon:
    """
    Dungeon with:
    - Connected set of rooms on a square grid
    - The location of some treasure
    - An adventurer agent with an initial position
    - A troll agent with an initial position
    """

    def __init__(self, rooms, treasure, adventurer, troll, verbose=True):
        self.rooms = rooms
        self.treasure = treasure
        self.adventurer = adventurer
        self.troll = troll
        self.verbose = True

        # the extent of the square grid
        self.xlim = (
            min(r.point[0] for r in self.rooms),
            max(r.point[0] for r in self.rooms),
        )
        self.ylim = (
            min(r.point[1] for r in self.rooms),
            max(r.point[1] for r in self.rooms),
        )

        self._validate()

    def _validate(self):
        if self.treasure.point not in self.rooms:
            raise ValueError(f"Treasure{self.treasure.point} is not in the dungeon")
        if self.adventurer.point not in self.rooms:
            raise ValueError(
                f"{self.adventure.name}{treasure.point} is not in the dungeon"
            )
        if self.troll.point not in self.rooms:
            raise ValueError(f"{self.troll.name}{treasure.point} is not in the dungeon")

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            spec = yaml.safe_load(f)

        rooms = Rooms.from_list(spec["rooms"])
        treasure = Treasure.from_dict(spec["treasure"])

        agent_keys = ["adventurer", "troll"]
        agents = {}
        for agent in agent_keys:
            if spec[agent]["type"] == "random":
                agent_class = RandomAgent
            elif spec[agent]["type"] == "human":
                agent_class = HumanAgent
            else:
                raise ValueError(f"Unknown agent type {spec[agent]['type']}")
            agents[agent] = agent_class(**spec[agent])

        return cls(rooms, treasure, agents["adventurer"], agents["troll"])

    def update(self):
        """
        Move the adventurer and the troll
        """
        self.adventurer.move(self.rooms)
        self.troll.move(self.rooms)
        if self.verbose:
            print()
            self.draw()

    def outcome(self):
        """
        Check whether the adventurer found the treasure or the troll
        found the adventurer
        """
        if self.adventurer.point == self.troll.point:
            return -1
        if self.adventurer.point == self.treasure.point:
            return 1
        return 0

    def set_verbose(self, verbose):
        """Set whether to print output"""
        self.verbose = verbose
        self.adventurer.verbose = verbose
        self.troll.verbose = verbose

    def draw(self):
        """Draw a map of the dungeon"""
        layout = ""

        for y in range(self.ylim[0], self.ylim[1] + 1):
            for x in range(self.xlim[0], self.xlim[1] + 1):
                # room and character symbols
                if (x, y) in self.rooms:
                    if self.troll.point == (x, y):
                        layout += self.troll.symbol
                    elif self.adventurer.point == (x, y):
                        layout += self.adventurer.symbol
                    elif self.treasure.point == (x, y):
                        layout += self.treasure.symbol
                    else:
                        layout += "o"
                else:
                    layout += " "

                # horizontal connections
                if ((x, y) in self.rooms) and (((x + 1), y) in self.rooms[(x, y)]):
                    layout += " - "
                else:
                    layout += "   "

            # vertical connections
            if y < self.ylim[1]:
                layout += "\n"
                for x in range(self.xlim[0], self.xlim[1] + 1):
                    if ((x, y) in self.rooms) and ((x, y + 1) in self.rooms[(x, y)]):
                        layout += "|"
                    else:
                        layout += " "
                    if x < self.xlim[1]:
                        layout += "   "
                layout += "\n"

        print(layout)

import copy

from art import tprint


class Game:
    def __init__(self, dungeon):
        self.dungeon = dungeon

    def preamble(self):
        tprint("Troll Treasure\n", font="small")
        print(
            f"""
The {self.dungeon.adventurer.name} is looking for treasure in a mysterious dungeon.
Will they succeed or be dinner for the {self.dungeon.troll.name} that lurks there?

The map of the dungeon is below:
o : an empty room
o - o : connected rooms
{self.dungeon.troll.symbol} : {self.dungeon.troll.name}
{self.dungeon.adventurer.symbol} : {self.dungeon.adventurer.name}
{self.dungeon.treasure.symbol} : the treasure
            """
        )

    def run(self, max_steps=1000, verbose=True, start_prompt=False):
        dungeon = copy.deepcopy(self.dungeon)
        dungeon.set_verbose(verbose)
        if verbose:
            self.preamble()
            dungeon.draw()
            if start_prompt:
                input("\nPress enter to continue...")
            else:
                print("\nLet the hunt begin!")

        for turn in range(max_steps):
            result = dungeon.outcome()
            if result != 0:
                if verbose:
                    if result == 1:
                        print(
                            f"\n{self.dungeon.adventurer.name} gets the treasure and returns a hero!"
                        )
                        tprint("WINNER", font="small")
                    elif result == -1:
                        print(f"\n{self.dungeon.troll.name} will eat tonight!")
                        tprint("GAME OVER", font="small")
                return result
            if verbose:
                print(f"\nTurn {turn + 1}")
            dungeon.update()
        # no outcome in max steps (e.g. no treasure and troll can't reach adventurer)
        if verbose:
            print(
                f"\nNo one saw {self.dungeon.adventurer.name} or {self.dungeon.troll.name} again."
            )
            tprint("STALEMATE", font="small")

        return result

    def probability(self, trials=10000, max_steps=1000, verbose=False):
        outcomes = {-1: 0, 0: 0, 1: 0}
        for _ in range(trials):
            result = self.run(max_steps=max_steps, verbose=False)
            outcomes[result] += 1
        for result in outcomes:
            outcomes[result] = outcomes[result] / trials
        return outcomes

