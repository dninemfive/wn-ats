from collections import defaultdict
from enum import member
import os
from time import time_ns
from typing import Any, Callable, Iterable, Literal, Self

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'MissileCarriageDepiction'

missile_types: set[str] = set()
depiction_types: set[str] = set()

with mod.edit(f'GameData/Generated/Gameplay/Gfx/{FOLDER}.ndf') as file:
    for row in file:
        if isinstance(row.value, Object):
            try:
                missiles: List = row.value.by_member('Missiles').value
                for info in missiles:
                    assert info.value.type == 'TStaticMissileCarriageSubDepictionMissileInfo' and 'Showroom' in row.namespace, row.namespace
                    missile_types.add(info.value.type)
                    depiction_types.add(info.value.by_member('Depiction').value.type)
            except Exception as e:
                print(e)

print(str(missile_types))
print(str(depiction_types))