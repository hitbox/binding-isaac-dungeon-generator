import random

from enum import Enum
from enum import auto

from .room import RoomType

class GeneratorStatus(Enum):
    INITIALIZED = auto()
    STARTED = auto()
    MINROOM_NOT_REACHED = auto()
    UNABLE_TO_FINALIZE = auto()
    FINISHED = auto()


GeneratorStatus.INITIALIZED.label = 'initialized'
GeneratorStatus.STARTED.label = 'started'
GeneratorStatus.MINROOM_NOT_REACHED.label = 'minimum number of rooms not met'
GeneratorStatus.UNABLE_TO_FINALIZE.label = 'unable to set boss, reward, coin and secret rooms'
GeneratorStatus.FINISHED.label = 'finalized floorplan'

class BorisFloorplanGenerator:
    """
    Close approximation of the demo code in:
    https://www.boristhebrave.com/2020/09/12/dungeon-generation-in-binding-of-isaac/
    """

    def __init__(self, minrooms=7, maxrooms=15):
        self.minrooms = minrooms
        self.maxrooms = maxrooms
        self.status = GeneratorStatus.INITIALIZED

    def start(self):
        self.floorplan = [0 for _ in range(101)]
        self.boss = None
        self.cellqueue = []
        self.endrooms = []
        self.placed_special = False
        self.started = True
        self.visit(45)
        self.status = GeneratorStatus.STARTED

    def visit(self, index):
        # .populated(index)
        if self.floorplan[index]:
            return False

        neighbors = self.ncount(index)
        if neighbors > 1:
            return False

        # .populated_cells()
        if sum(room != 0 for room in self.floorplan) >= self.maxrooms:
            return False

        if index != 45 and random.choice([True, False]):
            return False

        self.cellqueue.append(index)
        # .set_cell(index)
        self.floorplan[index] = RoomType.CELL
        return True

    def ncount(self, index):
        populated_neighbors = sum([
            self.floorplan[index - 10] != 0,
            self.floorplan[index - 1] != 0,
            self.floorplan[index + 1] != 0,
            self.floorplan[index + 10] != 0,
        ])
        return populated_neighbors

    def update(self):
        if not self.started:
            return
        if len(self.cellqueue) > 0:
            self._update_cellqueue()
        elif not self.placed_special:
            self.add_final_or_quit()

    def _update_cellqueue(self):
        index = self.cellqueue.pop(0)
        x = index % 10
        created = False
        if x > 1:
            created = created or self.visit(index - 1)
        if x < 9:
            created = created or self.visit(index + 1)
        if index > 20:
            created = created or self.visit(index - 10)
        if index < 70:
            created = created or self.visit(index + 10)
        if not created:
            self.endrooms.append(index)

    def add_final_or_quit(self):
        if sum(room != 0 for room in self.floorplan) < self.minrooms:
            self.status = GeneratorStatus.MINROOM_NOT_REACHED
            return
        # boss
        self.placed_special = True
        self.boss = self.endrooms.pop()
        try:
            # reward
            reward_index = self.poprandomendroom()
            self.floorplan[reward_index, RoomType.REWARD]
            # coin
            coin_index = self.poprandomendroom()
            self.floorplan[coin_index] = RoomType.COIN
            # cell and secret
            secret_index = self.picksecretroom()
            self.floorplan[secret_index] = RoomType.CELL
            self.floorplan[secret_index] = RoomType.SECRET
        except IndexError:
            self.status = GeneratorStatus.UNABLE_TO_FINALIZE
        else:
            self.status = GeneratorStatus.FINISHED

    def poprandomendroom(self):
        indexes = list(range(len(self.endrooms)))
        room_index = random.choice(indexes)
        self.endrooms.pop(room_index)
        return room_index

    def picksecretroom(self):
        for e in range(901):
            x = random.choice(range(1, 10))
            y = random.choice(range(2, 9))
            index = y * 10 + x

            if self.floorplan[index]:
                continue

            if (self.boss == index - 1
                or self.boss == index + 1
                or self.boss == index + 10
                or self.boss == index - 10
            ):
                continue

            ncount = self.ncount(index)
            if (ncount >= 3
                or (ncount >= 2 and e > 300)
                or (ncount >= 1 and e > 600)
            ):
                return index
