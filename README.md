# ud2prolog

Transforming Universal Dependency to Prolog logic programs using Generative Grammar, Lambda Calculus, and Neo-Davidsonian Semantics. This module contains hand-crafted Lambda structures for each dependency relation, which are then composed hierarchically with beta-reduction. The logical representation makes uses of Neo-Davidsonian semantics with thematic roles. 

## Usage

```bash
python -m src "Brutus stabs Caesar"
```
The equivalent logical representation is <code>
&exist;x.&exist;y. stabs(e, x, y) & Brutus(x) & Ceasar(y)</code>

Or with quantificational event semantics + thematic roles (*in development*)
```bash
python -m src -q "John kissed every girl"
```
which produces <code>&forall;x[girl(x) &rarr; &exist;e[kissed(e) & Ag(e, John) & th(e, x)]]</code>

## References & Further readings
1. [Transforming Dependency Structures to Logical Forms for Semantic Parsing](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00088/43352/Transforming-Dependency-Structures-to-Logical)
2. [The interaction of compositional semantics and event semantics](https://link.springer.com/article/10.1007/s10988-014-9162-8)