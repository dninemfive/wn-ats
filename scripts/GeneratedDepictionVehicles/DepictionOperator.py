from collections import Counter, defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'GeneratedDepictionVehicles'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

files = ['Vehicles', 'AerialUnits']

for filename in files:
    subtypes: defaultdict[str, set[str]] = defaultdict(lambda: set())

    with mod.edit(f'GameData/Generated/Gameplay/Gfx/Depictions/GeneratedDepiction{filename}.ndf') as data:
        print(time_since(program_start))
        for row in data:
            obj: Object = row.value
            if obj.type.startswith('DepictionOperator_'):
                for member in obj:
                    subtypes[obj.type].add(member.member)

    lines: list[str] = []
    for k in sorted(subtypes.keys()):
        lines.append(k)
        for v in sorted(subtypes[k]):
            lines.append(f'\t{v}')

    with open(os.path.join(FOLDER, f'DepictionOperator_{filename}.data'), 'w') as file:
        file.write('\n'.join(lines))
    print(time_since(program_start))