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

FOLDER = 'MissileCarriage'

types: set[str] = set()

with mod.edit('GameData/Generated/Gameplay/Gfx/MissileCarriage.ndf') as file:
    for row in file:
        if isinstance(row.value, Object):
            try:
                weapon_infos: List = row.value.by_member('WeaponInfos').value
                for info in weapon_infos:
                    types.add(info.value.type)
            except:
                pass

print(str(types))