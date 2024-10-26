import math
from typing import Iterable, Self

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Map, MapRow

CONSECUTIVE_CELL_DISCOUNT = 0.9
PADDING = len('Infantry') + 2

def marginal_utility(cell_index: int) -> float:
    return math.pow(CONSECUTIVE_CELL_DISCOUNT, cell_index)

def cost_utility(cost: int | None) -> float:
    if cost < 0 or cost is None:
        return 0
    return 1 / (cost + 1)

class CostMatrixRow(object):
    def __init__(self: Self, *cells: int):
        self._cells = cells

    def __len__(self: Self) -> int:
        return len(self._cells)

    def __iter__(self: Self) -> Iterable[int]:
        yield from self._cells

    def __getitem__(self: Self, index: int) -> int:
        return self._cells[index]
    
    def __str__(self: Self) -> str:
        items: list[str] = []
        for i in range(max(len(self), 10)):
            try:
                items.append(self[i])
            except:
                items.append('•')
        return ' '.join(str(x) for x in items)
    
    @property
    def utility(self: Self) -> float:
        result: float = 0
        for i in len(self):
            result += marginal_utility(i) * cost_utility(self[i])
        return result
    
    @staticmethod
    def from_ndf(row: List) -> Self:
        return CostMatrixRow(*[int(x.value) for x in row])
    
class CostMatrix(object):
    def __init__(self: Self, name: str = '', **rows: CostMatrixRow):
        self.name = name
        self._rows: dict[str, CostMatrixRow] = rows

    def __len__(self: Self) -> int:
        return len(self._rows)

    def __iter__(self: Self) -> Iterable[tuple[str, CostMatrixRow]]:
        yield from self._rows.items()

    def __getitem__(self: Self, key: str) -> CostMatrixRow:
        return self._rows[key]
    
    def __str__(self: Self) -> str:
        return f'{self.name}\n\t{'\n\t'.join(f'{k.ljust(PADDING)} {str(v)}' for k, v in self)}'

    @property
    def total_utility(self: Self) -> float:
        return sum(v.utility for _, v in self)
    
    @staticmethod
    def from_ndf(row: ListRow) -> Self:
        return CostMatrix(' '.join(row.namespace.split('_')[2:-1]), **{x.key.split('/')[-1]: CostMatrixRow.from_ndf(x.value) for x in row.value})
    
MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'Decks/DivisionCostMatrix'

with mod.edit('GameData/Generated/Gameplay/Decks/DivisionCostMatrix.ndf') as file:
    for row in file:
        print(str(CostMatrix.from_ndf(row)))