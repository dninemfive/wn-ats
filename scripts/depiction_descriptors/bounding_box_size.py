from ast import List
from collections import defaultdict
import os
from time import time_ns
from typing import Any

from ndf_parse import Mod
from ndf_parse.model import Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def is_object_of_type(item: Any, type: str) -> bool:
    return isinstance(item, Object) and item.type == type

program_start = time_ns()
data: list[tuple[str, str, str]] = []
with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for row in file:
        try:
            default: Object = row.value.by_member('ModulesDescriptors')\
                                 .value.by_name('GroupeCombat')\
                                 .value.by_member('Default')\
                                .value
            data.append((row.namespace, default.by_member('NbSoldatInGroupeCombat').value, default.by_member('BoundingBoxSize').value))
            print(row.namespace)
        except:
            pass

with open('depiction_descriptors/bounding_box_size.txt', 'w') as file:
    file.write('\n'.join(['\t'.join(t) for t in data]))

print(time_since(program_start))