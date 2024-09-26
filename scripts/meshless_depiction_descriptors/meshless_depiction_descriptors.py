from ast import List
from collections import defaultdict
import os
from time import time_ns
from typing import Any

from ndf_parse import Mod
from ndf_parse.model import Object

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
operators: defaultdict[str, set[str]] = defaultdict(lambda: set())
hypothesis_ever_violated = False
with mod.edit('GameData/Generated/Gameplay/Gfx/Infanterie/GeneratedDepictionInfantry.ndf') as file:
    for row in file:
        value = row.value
        if isinstance(value, List):
            hypothesis_violated: False
            second_last = value[-2]
            hypothesis_violated = not is_object_of_type(second_last.value, 'TDepictionDescriptor')
            last = value[-1]
            hypothesis_violated = (hypothesis_violated 
                                   or not (is_object_of_type(last.value, 'TMeshlessDepictionDescriptor')
                                      and second_last.by_member('MeshDescriptor').value == last.by_member('ReferenceMeshForSkeleton').value))
            if hypothesis_violated:
                print(row.namespace)
                hypothesis_ever_violated = True
print(hypothesis_ever_violated, time_since(program_start))