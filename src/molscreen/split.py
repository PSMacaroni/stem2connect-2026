"""Group split shared by the scaffold split (loop 1) and the leave-lineage-out split (loop 2)."""

import random
from collections import defaultdict
from collections.abc import Hashable, Sequence


def group_split(groups: Sequence[Hashable], test_frac: float = 0.2, seed: int = 0) -> tuple[list[int], list[int]]:
    """Indices (train, test) such that no group is on both sides. `groups[i]` is the group of item i.

    Groups go to train largest first while they fit under (1 - test_frac) of the items; groups that do not fit go
    to test. `seed` only breaks ties between groups of equal size.
    """
    members = defaultdict(list)
    for i, g in enumerate(groups):
        members[g].append(i)
    sets = list(members.values())
    random.Random(seed).shuffle(sets)
    sets.sort(key=len, reverse=True)  # stable, so equal-size groups keep the seeded order

    train_cutoff = (1 - test_frac) * len(groups)
    train, test = [], []
    for idx in sets:
        (train if len(train) + len(idx) <= train_cutoff else test).extend(idx)
    return sorted(train), sorted(test)
