import os
from collections import Counter, defaultdict
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Map, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'GeneratedDepictionVehicles'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def summarize(value: List | Map | str) -> str | list[str]:
    if isinstance(value, str) and not value.startswith('MAP'):
        return value
    else:
        return value.__class__.__name__

program_start = time_ns()

files = ['Vehicles']

for filename in files:
    subtypes: defaultdict[str, defaultdict[str, set[str]]] = defaultdict(lambda: defaultdict(lambda: set()))

    with mod.edit(f'GameData/Generated/Gameplay/Gfx/Depictions/GeneratedDepiction{filename}.ndf') as data:
        print(time_since(program_start))
        for row in data:
            obj: Object = row.value
            if obj.type == 'TacticVehicleDepictionTemplate':
                for member in obj:
                    subtypes[obj.type][member.member].add(str(summarize(member.value)))

    lines: list[str] = []
    for k1 in sorted(subtypes.keys()):
        lines.append(k1)
        for k2 in sorted(subtypes[k1].keys()):
            lines.append(f'\t{k2}')
            for v in sorted(subtypes[k1][k2]):
                lines.append(f'\t\t{v}')

    with open(os.path.join(FOLDER, f'DepictionTemplates_{filename}.data'), 'w') as file:
        file.write('\n'.join(lines))
    print(time_since(program_start))