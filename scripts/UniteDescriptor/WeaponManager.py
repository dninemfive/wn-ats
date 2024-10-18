from collections import Counter, defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'UniteDescriptor'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

subtypes: defaultdict[str, set[str]] = defaultdict(lambda: set())

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for row in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        unit: Object = row.value
        modules_descriptors: List = unit.by_member('ModulesDescriptors').value
        try:
            weapon_manager: Object = modules_descriptors.by_name('WeaponManager').value
            for member in weapon_manager:
                subtypes[member.member].add(str(member.value))
        except:
            pass

lines: list[str] = []
for k in sorted(subtypes.keys()):
    lines.append(k)
    for v in sorted(subtypes[k]):
        lines.append(f'\t{v}')

with open(os.path.join(FOLDER, f'WeaponManager.data'), 'w') as file:
    file.write('\n'.join(lines))
print(time_since(program_start))