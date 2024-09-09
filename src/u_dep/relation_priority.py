relation_priority = {
    "l-ROOT": -1,
    "l-amod": 10, 
    "l-compound": 10,
    "l-det": 15, 
    "l-quantmod": 15,
    "l-cc": 15,
    "l-acl": 16, 
    "l-cop": 20, 
    "l-dobj": 20, 
    "l-auxpass": 30, 
    "l-aux": 30,
    "l-xcomp": 30, 
    "l-nmod": 40, 
    "l-advmod": 40, 
    "l-ccomp": 40,
    "l-mark": 50,
    "l-nsubj": 60, 
    "l-case": 70,
    "l-punct": 90
}

from warnings import warn

class RelationPriority:
    def __init__(self) -> None:
        pass

    def get(self, label: str) -> int: 
        if label not in relation_priority: 
            warn(f"Relation {label} has priority not specified.")
        return relation_priority[label]