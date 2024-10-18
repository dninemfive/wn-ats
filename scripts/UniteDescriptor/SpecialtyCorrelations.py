from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Self
from ndf_parse import Mod
from ndf_parse.model import List, ListRow, MemberRow, Object

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'UniteDescriptor'

class Module(object):
    def __init__(self: Self, module: ListRow):
        val = module.value
        if isinstance(val, str):
            self.type = val
            self.namespace = None
        else:
            self.type = module.value.type
            self.namespace = module.namespace

    def __str__(self: Self) -> str:
        return self.type if self.namespace is None else f'{self.namespace} ({self.type})'

class Unit(object):
    def __init__(self: Self, row: ListRow):
        self.name = row.namespace
        unit: Object = row.value
        modules: List = unit.by_member('ModulesDescriptors').value
        self.modules: set[str] = set([str(Module(x)) for x in modules])
        try:
            ui_module: Object = modules.find_by_cond(lambda x: isinstance(x.value, Object) and x.value.type == 'TUnitUIModuleDescriptor').value
            self.specialties: set[str] = set([x.value for x in ui_module.by_member('SpecialtiesList').value])
        except:
            print(f"\tCouldn't find ui module on {unit.by_member('ClassNameForDebug').value}!")

    def has_specialty(self: Self, specialty: str) -> bool:
        return specialty in self.specialties
    
    def has_module(self: Self, module: str) -> bool:
        return module in self.modules
    
print('Loading data...')
units: list[Unit] = []
with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for row in file:
        units.append(Unit(row))

print('Finding correlations...')
unit_count: int = len(units)
all_modules: set[str] = set()
all_specialties: set[str] = set()
for unit in units:
    all_modules |= unit.modules
    all_specialties |= unit.specialties
all_modules = sorted(all_modules)
all_specialties = sorted(all_specialties)

def make_row(*items: str | Iterable[str | int]) -> str:
    columns = []
    for item in items:
        if isinstance(item, (str | int)):
            columns.append(str(item))
        else:
            for item2 in item:
                columns.append(str(item2))
    return '\t'.join(columns)

def count_with_specialty(_units: list[Unit], specialty: str) -> int:
    return len([x for x in _units if x.has_specialty(specialty)])

max_module_len = max([len(x) for x in all_modules])

def rows() -> Iterable[str]:
    yield make_row('↓ Module | Specialty →', all_specialties, 'Total')
    for module in all_modules:
        units_with_module: list[Unit] = [x for x in units if x.has_module(module)]
        print(module.ljust(max_module_len),'\t',str(len(units_with_module)).rjust(10))
        yield make_row(module, [count_with_specialty(units_with_module, x) for x in all_specialties], len(units_with_module))
    yield make_row('Total', [count_with_specialty(units, x) for x in all_specialties], len(units))

print('Writing correlations...')
with open(f'{FOLDER}/SpecialtyCorrelation.tsv.data', 'w', encoding='utf') as file:
    file.write('\n'.join(rows()))

def all_units_have(module: str) -> bool:
    for unit in units:
        if not unit.has_module(module):
            return False
    return True

print('Finding specialty requirements...')
modules_on_all_units: set[str] = set()
for module in all_modules:
    if all_units_have(module):
        modules_on_all_units.add(module)

print('\t', str(modules_on_all_units))


def specialty_requires(specialty: str, module: str) -> bool:
    if module in modules_on_all_units:
        return False
    for unit in units:
        if unit.has_specialty(specialty) and not unit.has_module(module):
            return False
    return True

specialty_requirements: list[str] = []
for specialty in all_specialties:
    s_modules: list[str] = []
    for module in all_modules:
        if specialty_requires(specialty, module):
            s_modules.append(module)
    specialty_requirements.append(f'{specialty}: {'\n\t'.join(s_modules)}')

print('Writing specialty requirements...')
with open(f'{FOLDER}/SpecialtyRequirements.txt.data', 'w', encoding='utf') as file:
    file.write('\n'.join(specialty_requirements))

print('Done!')