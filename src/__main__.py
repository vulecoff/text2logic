from .lambda_calculus.lambda_ast import Abstr
from .lambda_calculus import lambda_processor

from .u_dep.transformer import build_deptree_from_spacy


import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Disney acquired Pixar.")

root = list(doc.sents)[0].root
dt = build_deptree_from_spacy(root)
print(dt)

from .u_dep.relation_priority import RelationPriority
from .u_dep.dep2lambda import Dep2Lambda
from .u_dep.transformer import Transformer
from .u_dep.dep_tree import DepTree

rp = RelationPriority()
d2l = Dep2Lambda()

tf = Transformer(rp, d2l)

dep = tf.binarize(dt)
print(dep)

tf.assign_lambda(dep)

print(tf.compose_semantics(dep))


