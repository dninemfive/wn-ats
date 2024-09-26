from ast import List
from collections import defaultdict
import os
from time import time_ns
from typing import Any

from ndf_parse import Mod
from ndf_parse.model import Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

# testing hypothesis: the last item of all _Alternatives lists matches:
#   TMeshlessDepictionDescriptor(
#       SelectorId = "'none'"
#       ReferenceMeshForSkeleton = <previous item>.MeshDescriptor
#   )

mod = Mod(MOD_PATH, MOD_PATH)

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def is_object_of_type(item: Any, type: str) -> bool:
    return isinstance(item, Object) and item.type == type

program_start = time_ns()
with mod.edit('GameData/Generated/Gameplay/Gfx/Infanterie/GeneratedDepictionInfantry.ndf') as file:
    transported_infantry_alternatives_count = file.by_name('TransportedInfantryAlternativesCount').value
    for row in transported_infantry_alternatives_count:
        soldier_key = f'TacticDepiction_{row.key[1:-1]}_Soldier'
        selector: str = file.by_name(soldier_key).value.by_member('Selector').value
        l1, r1 = row.value
        l1, r1 = int(l1), int(r1)
        split = selector.split('_')
        l2, r2 = int(split[1]), int(split[2])
        if not(l1 == l2 and r1 == r2):
            print(row.key, l1, r1, l2, r2)

print(time_since(program_start))