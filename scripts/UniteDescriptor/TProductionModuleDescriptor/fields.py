from collections import Counter, defaultdict
import os
from time import time_ns
from tokenize import maybe
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'
MODULE = 'TProductionModuleDescriptor'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = f'UniteDescriptor/{MODULE}/Fields'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

def try_unquote(s: str) -> str:
    if s.startswith("'") or s.startswith('"'):
        s = s[1:]
    if s.endswith("'") or s.endswith('"'):
        s = s[:-1]
    return s

def find_common_prefix(strs: Iterable[str]) -> str | None:
    strs = [try_unquote(s) for s in strs]
    maybe_prefix = strs[0]
    for s in strs[1:]:
        if len(maybe_prefix) < 1:
            break
        while not s.startswith(maybe_prefix):
            maybe_prefix = maybe_prefix[:-1]
    return maybe_prefix if len(maybe_prefix) > 0 else None

def strip_prefix(s: str, prefix: str) -> str:
    s = try_unquote(s)
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

fields: dict[str, set[str]] = {x: set() for x in ['Factory']}

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for row in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        unit: Object = row.value
        modules_descriptors: List = unit.by_member('ModulesDescriptors').value
        module: Object = modules_descriptors.find_by_cond(lambda x: isinstance(x.value, Object)
                                                    and x.value.type == MODULE).value
        for k, v in fields.items():
            v.add(module.by_member(k).value)

for k, v in fields.items():
    with open(os.path.join(FOLDER, f'{k}.txt.data'), 'w') as file:
        file.write('\n'.join(sorted(v)))
    common_prefix: str = find_common_prefix(v)
    if common_prefix is not None:
        stripped = sorted([strip_prefix(x, common_prefix) for x in v])
        with open(os.path.join(FOLDER, f'{k}_stripped.txt.data'), 'w') as file:
            file.write('\n'.join([f'prefix: {common_prefix}', *stripped]))
print(time_since(program_start))