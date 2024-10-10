from collections import defaultdict
from enum import member
import os
from time import time_ns
from typing import Any, Iterable, Literal, Self

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'unite_literals'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

members: dict[str, str] = {
    'UnitRole': 'str',
    'SpecialtiesList': 'list[str]',
    'NameToken': 'str',
    'InfoPanelConfigurationToken': 'str',
    'DisplayRoadSpeedInKmph': 'float',
    'GenerateName': 'bool',
    'UpgradeFromUnit': 'str | None',
    'MenuIconTexture': 'str',
    'ButtonTexture': 'str',
    'CountryTexture': 'str',
    'TypeStrategicCount': 'str'
}

lines = []
for k in sorted(members.keys()):
    lines.append(f"    @property\n    def {k}(self: Self) -> {members[k]}:\n        return self.object.by_member('{k}').value")
    lines.append(f"    @{k}.setter\n    def {k}(self: Self, value: {members[k]}) -> None:\n        edit.member(self.object, '{k}', value)")

with open(os.path.join(FOLDER, f'UnitUiModuleWrapperMembers.py'), 'w') as file:
    file.write('\n\n'.join(lines))
print(time_since(program_start))