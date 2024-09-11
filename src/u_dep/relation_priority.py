relation_priority = {
    "ROOT": -1,
    "amod": 2,
    "nn": 2, 
    "num": 2,
    "quantmod": 2, 
    "nmod": 2,
    
    "dobj": 10, 
    "pobj": 10, 
    "aux": 10,
    "expl": 10, 
    "prt": 10,
    "pcomp": 10, 

    "attr": 30, 
    "prep": 30, 
    "det": 30, 
    "auxpass": 30, 
    "acomp": 30, 
    "rel": 30, 

    "conj": 35, # TODO: sep to conj-np, vp, etc
    "cc": 35,
    "neg": 35,
    "dep": 35,

    "iobj": 40,
    "appos": 40,

    "nsubj": 45,
    "nsubjpass": 45,

    "mark": 50, 
    "poss": 50,

    "npavmod": 50, 
    "advmod": 50, 
    "advcl": 50, 
    "tmod": 50, # TODO

    "punct": 100,
}

from warnings import warn

class RelationPriority:
    def __init__(self) -> None:
        pass

    def get(self, label: str) -> int: 
        if label not in relation_priority: 
            warn(f"Relation {label} has priority not specified.")
            return 500
        return relation_priority[label]