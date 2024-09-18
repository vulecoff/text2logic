
from warnings import warn
from ..dep_priority.default import default

class RelationPriority:
    def __init__(self, priority_dt = default) -> None:
        self.priority_dt = priority_dt

    def get(self, label: str) -> int: 
        if label not in self.priority_dt: 
            warn(f"Relation {label} has priority not specified.")
            return 500
        return self.priority_dt[label]