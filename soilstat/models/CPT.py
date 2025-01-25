from dataclasses import dataclass, field
from typing import List


@dataclass
class CPTExp:
    depth: float
    cone_resistance: float


class CPTLog:
    exps: List[CPTExp] = field(default_factory=list)

    def __init__(self, exps: List[CPTExp]):
        self.exps = exps

    def get_exp_at_depth(self, depth: float) -> CPTExp:
        for i, exp in enumerate(self.exps):
            if exp.depth >= depth:
                return self.exps[i - 1]

        return self.exps[-1]
