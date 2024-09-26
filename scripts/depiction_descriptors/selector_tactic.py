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
selector_tactics: defaultdict[str, set[str]] = defaultdict(lambda: set())
hypothesis_ever_violated = False
with mod.edit('GameData/Generated/Gameplay/Gfx/Infanterie/GeneratedDepictionInfantry.ndf') as file:
    for row in file:
        value = row.value
        if isinstance(value, Object) and value.type == 'TemplateInfantryDepictionFactoryTactic':
            selector_tactics[value.by_member('Selector').value].add(row.namespace)
result: list[str] = []
for k in sorted(selector_tactics.keys()):
    result.append(k)
    for item in sorted(selector_tactics[k]):
        result.append(f'\t{item}')
with open('selector_tactics.txt', 'w') as file:
    file.write('\n'.join(result))
print(f"Found {len(selector_tactics)} selector tactics in", time_since(program_start))