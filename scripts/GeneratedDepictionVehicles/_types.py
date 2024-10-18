from collections import Counter, defaultdict
import os
from time import time_ns

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'GeneratedDepictionVehicles'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def summarize(value: List | str) -> str | list[str]:
    if isinstance(value, str):
        return value
    result = []
    for item in value:
        result.append(str(item.value))
    return result

program_start = time_ns()

files = ['Vehicles', 'AerialUnits']

for filename in files:
    types: set[str] = set()

    with mod.edit(f'GameData/Generated/Gameplay/Gfx/Depictions/GeneratedDepiction{filename}.ndf') as data:
        print(time_since(program_start))
        for row in data:
            obj: Object = row.value
            types.add(obj.type)

    with open(os.path.join(FOLDER, f'{filename}_types.data'), 'w') as file:
        file.write('\n'.join(sorted(types)))
    print(time_since(program_start))