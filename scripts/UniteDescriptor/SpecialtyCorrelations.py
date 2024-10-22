from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Literal, Self
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

T_ATTR = Literal['modules', 'specialties', 'capacites']
MODULE, SPECIALTY, CAPACITE = 'modules', 'specialties', 'capacites'
# alias the constants for readability
MODULES, SPECIALTIES, CAPACITES = MODULE, SPECIALTY, CAPACITE
ATTRS = [MODULE, SPECIALTY, CAPACITE]

class Unit(object):
    def __init__(self: Self, row: ListRow):
        self.name = row.namespace
        for attr in ATTRS:
            value = getattr(self, f'_init_{attr}')(row.value)
            print(f'_init_{attr}({row.value}) -> {value}') 
            setattr(self, attr, value)

    def _init_modules(self: Self, unit: Object):
        modules: List = unit.by_member('ModulesDescriptors').value
        self.modules: set[str] = set([str(Module(x)) for x in modules])

    def _init_specialties(self: Self, unit: Object):
        modules: List = unit.by_member('ModulesDescriptors').value
        ui_module: Object = modules.find_by_cond(lambda x: isinstance(x.value, Object) and x.value.type == 'TUnitUIModuleDescriptor').value
        self.specialties: set[str] = set([x.value for x in ui_module.by_member('SpecialtiesList').value])

    def _init_capacites(self: Self, unit: Object):
        self.capacites: set[str] = set()
        try:
            capacites: Object = unit.find_by_cond(lambda x: isinstance(x.value, Object)
                                                            and x.value.type == 'TModuleSelector'
                                                            and x.value.by_member('Default').value.type == 'TCapaciteModuleDescriptor').value
            for row in (capacites.by_member('Default').value
                                 .by_member('DefaultSkillList').value):
                self.capacites.add(row.value)
        except:
            pass

    def has_(self: Self, attr: T_ATTR, val: str) -> bool:
        return val in getattr(self, attr)
    
print('Loading data...')
units: list[Unit] = []
with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for row in file:
        units.append(Unit(row))

print('Finding correlations...')
unit_count: int = len(units)
all: dict[T_ATTR, list[str]] = {}
for attr in ATTRS:
    items = set()
    for unit in units:
        stuff = getattr(unit, attr)
        if stuff is not None:
            items |= getattr(unit, attr)
    all[attr] = sorted(items)

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
    return len([x for x in _units if x.has_(SPECIALTY, specialty)])

max_module_len = max([len(x) for x in all[MODULES]])

def tsv() -> Iterable[str]:
    yield make_row('↓ Module | Specialty →', all[SPECIALTIES], 'Total')
    for module in all[MODULES]:
        units_with_module: list[Unit] = [x for x in units if x.has_(MODULE, module)]
        print(module.ljust(max_module_len),'\t',str(len(units_with_module)).rjust(10))
        yield make_row(module, [count_with_specialty(units_with_module, x) for x in all[SPECIALTIES]], len(units_with_module))
    yield make_row('Total', [count_with_specialty(units, x) for x in all[SPECIALTIES]], len(units))

print('Writing correlations...')
with open(f'{FOLDER}/SpecialtyCorrelation.tsv.data', 'w', encoding='utf') as file:
    file.write('\n'.join(tsv()))

def all_units_have(attr: str, module: str) -> bool:
    for unit in units:
        if not unit.has_(attr, module):
            return False
    return True

print('Finding specialty requirements...')
modules_on_all_units: set[str] = set()
for module in all[MODULES]:
    if all_units_have(MODULE, module):
        modules_on_all_units.add(module)

print('\t', str(modules_on_all_units))


def specialty_requires(attr: T_ATTR, specialty: str, value: str) -> bool:
    for unit in units:
        if unit.has_(SPECIALTY, specialty) and not unit.has_(attr, value):
            return False
    return True

def specialty_requirements(attr: T_ATTR) -> Iterable[str]:
    for specialty in all[SPECIALTIES]:
        requirements: list[str] = []
        for value in all[attr]:
            if specialty_requires(attr, specialty, value):
                requirements.append(value)
        yield f'{specialty}: {'\n\t'.join(requirements)}'

for attr in [MODULES, CAPACITES]:
    print(f'Writing specialty requirements ({attr})...')
    with open(f'{FOLDER}/SpecialtyRequirements_{attr}.txt.data', 'w', encoding='utf') as file:
        file.write('\n'.join(specialty_requirements(attr)))

print('Done!')