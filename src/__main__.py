from .lambda_calculus.lambda_ast import Abstr, LambdaExpr
from .lambda_calculus.lambda_processor import uniqueify_var_names, flatten

from .u_dep.relation_priority import RelationPriority
from .u_dep.dep2lambda import Dep2Lambda
from .u_dep.transformer import Transformer, build_deptree_from_spacy
from .u_dep.dep_tree import DepTree
from .u_dep.postprocessor import PostProcessor
from .dep2lambda_converter.default import default_converter
from .dep2lambda_converter.quantificational import quant_converter
import argparse

import spacy
from spacy import displacy

def print_section(txt): 
    print("_" * 5 + txt + "_" *5)

def numeric_incrementer_gen(): 
    id = 0
    while True:
        id += 1
        yield f"<{id}>"
def alphabet_incrementer_gen():
    alphabet = [chr(ord('a') + i) for i in range(26)]
    for x in alphabet: 
        yield x

def parse_with_quantifer(text: str, with_show=False):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sents = list(doc.sents)

    print_section("Token Description")
    for token in doc: 
        print(token.text, token.dep_, token.pos_, token.ent_type_)
    print()
    # for now parsing single sentence
    assert len(sents) == 1
    root = sents[0].root

    rel_priority = RelationPriority()
    converter = quant_converter
    d2lambda = Dep2Lambda(converter=converter)
    tf = Transformer(relation_priority=rel_priority, dep2lambda=d2lambda)

    deptree = build_deptree_from_spacy(root)
    DepTree.validate(deptree)
    print_section("Original DepTree")
    print(tf.tree_repr_with_priority(deptree))
    print()
    
    preprocesed_dt = tf.preprocess(deptree)
    DepTree.validate(preprocesed_dt)
    binarized = tf.binarize(preprocesed_dt)

    print_section("Preprocessed DepTree")
    print(tf.tree_repr_with_priority(preprocesed_dt))
    print()
    print("Binarized DepTree")
    print(tf.tree_repr_with_priority(binarized))
    
    print("\n")
    tf.assign_lambda(binarized)
    result = tf.compose_semantics(binarized)
    result = uniqueify_var_names(result, alphabet_incrementer_gen())
    result = flatten(result)
    print_section("Final Lambda")
    print(LambdaExpr.colored_repr(result))
    print()

    # postprocessor = PostProcessor()
    # result = postprocessor.process(result)
    # print_section("Post-processed Lambda")
    # print(result)    

    if with_show: 
        displacy.serve(doc)


def parse(text: str, with_show=False):
    # input in sentence --> tree, final lambda
    """Pipeline: 
        parse from spacy --> convert to internal repr --> preprocess
        --> binarize + assign_lambda + compose_semantics --> postprocess
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sents = list(doc.sents)

    print_section("Token Description")
    for token in doc: 
        print(token.text, token.dep_, token.pos_, token.ent_type_)
    print()
    # for now parsing single sentence
    assert len(sents) == 1
    root = sents[0].root

    rel_priority = RelationPriority()
    converter = default_converter
    d2lambda = Dep2Lambda(converter=converter)
    tf = Transformer(relation_priority=rel_priority, dep2lambda=d2lambda)

    deptree = build_deptree_from_spacy(root)
    DepTree.validate(deptree)
    print_section("Original DepTree")
    print(tf.tree_repr_with_priority(deptree))
    print()
    
    preprocesed_dt = tf.preprocess(deptree)
    DepTree.validate(preprocesed_dt)
    binarized = tf.binarize(preprocesed_dt)

    print_section("Preprocessed DepTree")
    print(tf.tree_repr_with_priority(preprocesed_dt))
    print()
    print("Binarized DepTree")
    print(tf.tree_repr_with_priority(binarized))
    
    print("\n")
    tf.assign_lambda(binarized)
    result = tf.compose_semantics(binarized)
    result = uniqueify_var_names(result, alphabet_incrementer_gen())
    print_section("Final Lambda")
    print(result)
    print()

    postprocessor = PostProcessor()
    result = postprocessor.process(result)
    print_section("Post-processed Lambda")
    print(result)    

    if with_show: 
        displacy.serve(doc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse sentence to lambda, for now")
    parser.add_argument("text", type=str, 
                        help="Text to parse")
    parser.add_argument("--show", "-s", action="store_true",
                        help="Show dep graph with displaCy", dest="show")
    parser.add_argument("--quantifier", "-q", action="store_true", 
                        help="Experimental: Quantificational Event Semantics")
    # TODO: file to input/output

    args = parser.parse_args()
    if args.quantifier: 
        parse_with_quantifer(args.text, with_show=args.show)
    else: 
        parse(args.text, with_show=args.show)