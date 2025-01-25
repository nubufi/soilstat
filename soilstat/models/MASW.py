from dataclasses import dataclass, field
from typing import List


@dataclass
class MASWExp:
    depth: float
    shear_wave_velocity: float


class MASWLog:
    exps: List[MASWExp] = field(default_factory=list)

    def __init__(self, exps: List[MASWExp]):
        self.exps = exps

    def get_exp_at_depth(self, depth: float) -> MASWExp:
        for i, exp in enumerate(self.exps):
            if exp.depth >= depth:
                return self.exps[i - 1]

        return self.exps[-1]
