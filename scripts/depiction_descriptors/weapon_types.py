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
weapon_types: set[str] = set()
skeleton_types: set[str] = set()
with mod.edit('GameData/Generated/Gameplay/Gfx/Infanterie/GeneratedDepictionInfantry.ndf') as file:
    for row in file:
        value = row.value
        if is_object_of_type(value, 'TemplateInfantryDepictionFactoryTactic'):
            for operator in value.by_member('Operators').value:
                skeleton_types.add(operator.value.type)
                try:
                    for tag in operator.value.by_member('ConditionalTags').value:
                        t, _ = tag.value
                        weapon_types.add(t)
                except:
                    pass

print(sorted(weapon_types), sorted(skeleton_types), time_since(program_start))