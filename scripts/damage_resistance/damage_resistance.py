from collections import Counter, defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'damage_resistance'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

vals: list[list[float]] = []
with mod.edit('GameData/Generated/Gameplay/Gfx/DamageResistance.ndf') as file:
    print(time_since(program_start))
    damage_resistance: Object = file[0].value
    values = damage_resistance.by_member("Values").value
    for row in values:
        r = []
        for col in row.value:
            r.append(float(col.value))
        vals.append(r)

def rows(_data: list[list[float]]) -> Iterable[str]:
    for row in _data:
        line = ''
        for col in row:
            line += f'\t{col}'
        yield line

with open(os.path.join(FOLDER, f'damage_resistance.tsv.data'), 'w') as file:
    file.write('\n'.join(rows(vals)))

print(time_since(program_start))