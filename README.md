# TransitionsThreeTiers

Supporting code for generating the sentences from a context-free grammar, an indexed grammar, and a context-sensitive grammar in the folder **sentence-generation** and Dataset S1 (stats.csv) for the Supplemental Text of **Three tiers of computation in transformers and in brain architectures** by Emma Graham and Richard Granger.

This code was run with Python 3.10.15 and with the packages *random*, *os*, *sys*, and *time* to run the **sentence-generation/main.py** file. 

### Abstract

i) Transformer-based language models (LMs), and human subjects, were prompted to empirically asses the *acceptability* of sentences generated from the rules of three distinct tiers of the grammar-automata (G-A) hierarchy: unrestricted-stack pushdown automata (PDA), nested-stack higher-order pushdown automata (HOPDA), and linear bounded automata (LBA). In accordance with extensive previous findings, humans reliably recognize sentences that require an automaton of the HOPDA tier, equivalent in power to indexed grammars (IXG). Only LMs of sufficient sizes are able to recognize the same tier as humans; all smaller LMs recognize only sub-HOPDA tiers.
ii) HOPDA is the most powerful tier of automata that use solely single-stack memories; all higher tiers (LBA through Turing machines) require multiple independent memory stores. Thus HOPDA constitute a natural *ceiling* within the G-A hierarchy.  
iii) Nonhuman animal communication is sub-HOPDA whereas humans process HOPDA-level indexed grammars. Humans also can learn to process supra-HOPDA formal logic, but this requires specific rigorous training, in stark contrast to the ubiquitous and seemingly effortless human acquisition of natural language. Taken together, these findings identify specific augmentations that may be entailed in the acquisition of logical reasoning faculties in artificial systems.
