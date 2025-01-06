'''
Sentence generator from respective formal grammars, in the theme of mathematicians... 
    but could change the theme to something more fun, simply edit the lexicon


Sentence generation from three different classes of computational classes:
1.  Context-Free Language (CFL) == Push Down Automata (PDA)
2.  Indexed Language (IXL) == Higher Order Push Down Automata (HOPDA)
3.  Context-Sensitive Language (CSL) == Linear Bounded Automata (LBA)
'''

import random
import sys
import time
import os

from generate_sentences import generate_sentence, generate_sentence_recursion_limits, generate_sentence_noncf, generate_sentence_fsm
# from generate_sentences import generate_sentence_recursion_limits, generate_sentence_noncf

# Increase recursion limit (ONLY if needed)
# sys.setrecursionlimit(2000)  # really try not to do this

# random.seed(1)


# Regular Grammar --> requiring Finite State Machine (nondeterministic) -- no recursions or nested structures
fms_rules = {
        "S": [["NP", "VP", "rNP", "rVP", "rNP"]],
        "NP": [["Det_sg", "N_sg"], ["Det_pl", "N_pl"], ["ProperNoun_sg"],
                ["Det_sg", "Adj", "N_sg"], ["Det_pl", "Adj", "N_pl"],
                ["Det_sg", "N_sg", "RelPronoun"],
                ["Det_pl", "N_pl", "RelPronoun"],
                ["ProperNoun_sg", "Conj", "ProperNoun_sg"],
                ["Det_sg", "N_sg", "Conj", "Det_sg", "N_sg"],
                ["Det_pl", "N_pl", "Conj", "Det_pl", "N_pl"]],
        "VP": [["V_sg"], ["V_pl"], ["Adv", "V_sg"], ["Adv", "V_pl"],
                ["V_sg", "Conj", "V_sg"], ["V_pl", "Conj", "V_pl"]],
        "rNP": [["Det_sg", "N_sg"], ["Det_pl", "N_pl"], ["ProperNoun_sg"],
                ["Det_sg", "Adj", "N_sg"], ["Det_pl", "Adj", "N_pl"],
                ["ProperNoun_sg", "Conj", "ProperNoun_sg"],
                ["Det_sg", "N_sg", "Conj", "Det_sg", "N_sg"],
                ["Det_pl", "N_pl", "Conj", "Det_pl", "N_pl"],
                ["RelPronoun", "V_sg"], ["RelPronoun", "V_pl"],
                ["RelPronoun", "Adv", "V_sg"], ["RelPronoun", "Adv", "V_pl"],
                ["RelPronoun", "V_sg", "Conj", "V_sg"], ["RelPronoun", "V_pl", "Conj", "V_pl"]],
        "rVP": [["V_sg"], ["V_pl"], ["Adv", "V_sg"], ["Adv", "V_pl"],
                ["V_sg", "Conj", "V_sg"], ["V_pl", "Conj", "V_pl"],
                ["V_sg", "P"], ["V_pl", "P"], ["Adv", "V_sg", "P"], ["Adv", "V_pl", "P"]],
}


# Context-Free Grammar(CFG) --- requiring a Push Down Automata (PDA) for recognition
cf_rules = {
        "S": [["NP", "VP"]],

        "NP":   [["NP_sg"], ["NP_pl"]],
        "NP_sg":    [["Det_sg", "N_sg", "NP_conj_sg"], ["Det_sg", "Adj", "N_sg"], 
                    ["ProperNoun_sg"], ["ProperNoun_sg", "NP_conj_sg"]],
        "NP_pl":    [["Det_pl", "N_pl", "NP_conj_pl"], ["Det_pl", "Adj", "N_pl"]],

        "NP_conj_sg": [["Conj", "NP_sg"], []],
        "NP_conj_pl": [["Conj", "NP_pl"], []],

        "VP": [["VP_sg"], ["VP_pl"]],
        "VP_sg":    [["V_sg", "NP", "VP_conj_sg"], ["V_sg", "VP_conj_sg"],
                    ["Adv", "V_sg", "NP", "VP_conj_sg"], ["Adv", "V_sg", "VP_conj_sg"]],
        "VP_pl": [["V_pl", "NP", "VP_conj_pl"], ["Adv", "V_pl", "VP_conj_pl"],
                    ["V_pl", "NP"], ["V_pl"], ["Adv", "V_pl", "NP"]],

        "VP_conj_sg": [["Conj", "VP_sg", "PP"], []],
        "VP_conj_pl": [["Conj", "VP_pl", "PP"], []],

        "PP": [["P", "NP"], ["P", "NP", "PP_conj"]],
        "PP_conj": [["Conj", "PP"], []]
    }

# Indexed Grammar (IXG) (a.k.a. mildly context-sensitive grammar) --- requiring a Higher Order Push Down Automata (HOPDA) for recognition
ix_rules = {   # adjusted rules for unbounded cross-serial dependencies
        "S": [["NP_sg", "VP_sg"], ["NP_pl", "VP_pl"]],

        "NP": [["NP_sg"], ["NP_sg", "NP_conj_sg"],
                ["NP_sg", "PP"], ["NP_pl", "PP"],
                ["NP_pl"], ["NP_pl", "NP_conj_pl"]],

        "NP_sg": [
                ["Det_sg", "N_sg"], ["Det_sg", "Adj", "N_sg"], 
                ["NP_sg", "PP"],
                ["ProperNoun_sg", "RC_sg"], [ "ProperNoun_sg"],
                ["Det_sg", "N_sg", "RC_sg"], 
                ["Det_sg", "Adj", "N_sg", "RC_sg"]
                ],
        "NP_pl": [
                ["Det_pl", "N_pl"], ["Det_pl", "Adj", "N_pl"],
                ["NP_pl", "PP"],
                ["Det_pl", "Adj", "N_pl", "RC_pl"], 
                ["Det_pl", "N_pl", "RC_pl"]
                ],

        "NP_conj_sg": [["Conj", "NP_sg"],  ["Conj", "NP_sg", "NP_conj_sg"], []],
        "NP_conj_pl": [["Conj", "NP_pl"], ["Conj", "NP_pl", "NP_conj_pl"], []],

        # RC productions
        "RC_sg": [["RelPronoun", "VP_sg"]], # to induce nested dependencies
        "RC_pl": [["RelPronoun", "VP_pl"]],

        "VP": [["VP_sg"], ["VP_pl"]],
        "VP_sg": [["V_sg", "NP", "VP_conj_sg"], ["V_sg", "VP_conj_sg"],
                ["Adv", "V_sg", "VP_conj_sg"],
                ["V_sg", "NP"], ["V_sg"], 
                ["VP_sg", "PP"], ["Adv", "VP_sg"]],
        "VP_pl": [["V_pl", "NP", "VP_conj_pl"], ["V_pl", "VP_conj_pl"],
                ["V_pl", "NP"], ["V_pl"], ["Adv", "V_pl", "NP"],
                ["VP_pl", "PP"], ["VP_pl"]],

        "VP_conj_sg": [["Conj", "VP_sg"], []],
        "VP_conj_pl": [["Conj", "VP_pl"], []],

        # PP and Conj
        "PP": [["P", "NP"], ["P", "NP", "PP_conj"]],
        "PP_conj": [["Conj", "PP"], []]
    }

# Context-Sensitive Grammar (CSG) rules --- requiring a Linear Bound Automata (LBA) for recognition
cs_rules = {
   
        "S": [["NP_sequence", "VP_placeholder"]],
        # context-sensitive productions to enforce cross-serial dependencies
        ("NP_sequence", "VP_placeholder"): [
            ["NP_sg", "NP_sequence", "VP_sg", "VP_sequence"],
            ["NP_pl", "NP_sequence", "VP_pl", "VP_sequence"],
            # []  # Base case when sequences are empty -- we would like the sentences to be non-empty for our purposes but if this is wanted then uncomment
        ],
        # Noun phrase sequence
        "NP_sequence": [["NP", "NP_sequence"], ["NP"]],
        # Verb phrase sequence (with production rules)
        "VP_sequence": [["VP_sg", "VP_sequence"], ["VP_sg"], 
                        ["VP_pl", "VP_sequence"], ["VP_pl"], []],

        # Noun phrases
        "NP": [["NP_sg"], ["NP_pl"]],
        "NP_sg": [
            ["Det_sg", "Adj", "N_sg"],
            ["Det_sg", "Adj", "N_sg", "PP"],
            ["Det_sg", "N_sg"],
            ["Det_sg", "N_sg", "PP"],
            ["ProperNoun_sg"],
            ["ProperNoun_sg", "PP"],
            ["Det_sg", "N_sg", "RC_sg"],
        ],
        "NP_pl": [
            ["Det_pl", "Adj", "N_pl"],
            ["Det_pl", "Adj", "N_pl", "PP"],
            ["Det_pl", "N_pl"],
            ["Det_pl", "N_pl", "PP"],
            ["Det_pl", "N_pl", "RC_pl"],
        ],

        "PP": [["P", "NP"], ["P", "NP", "PP_conj"]],
        "PP_conj": [["Conj", "PP"], []],

        "RC_sg": [["RelPronoun", "VP_sg"]],
        "RC_pl": [["RelPronoun", "VP_pl"]],

        "VP_placeholder": [["VP_sequence"], []],  # used to align with cs rules and allows replacing with VP_sequence or removing it
        "VP_sg": [["Adv", "V_sg", "NP"], ["V_sg"], ["V_sg", "NP"], ["Adv", "V_sg"]],
        "VP_pl": [["Adv", "V_pl", "NP"], ["V_pl"], ["V_pl", "NP"], ["Adv", "V_pl"]],
    }

lexicon = {
        ## Determiners
        "Det_sg": ["the", "a"],
        "Det_pl": ["the"],
        
        ## Nouns
        "N_sg": [
            "dog", "tree", "sunset", "ocean", "star", "university",
            "lion", "hat", "novel", "book", "leaf", "person", "bird", "blueberry"
        ],
        "N_pl": [
            "dogs", "trees", "mountains", "oceans", "stars", "universities",
            "lions", "rooms", "people", "items", "primates", "fish",
            "equations", "theorems", "functions", "strawberries"
        ],
        "ProperNoun_sg": ["Euclid", "Leibniz", "Galileo", "Euler", "Turing", "Gauss",
                        "Hilbert", "Riemann", "Cauchy", "Poincare", "Ramanujan", "Cantor", "Fourier",
                        "Fermat", "Pascal", "Lagrange", "Laplace", "Gödel",  "Kolmogorov", "Chebyshev", 
                        "Bernoulli", "Fibonacci"],
        
        ## Adjectives
        "Adj": [
            "quick", "slow", "bright", "deep", "soft", "mystic", "defective",
            "forlorn", "fiery", "fair", "brilliant", "famous", "ancient", "modern",
            "complex", "simple", "elegant", "intricate"
        ],

        ## Verbs
        "V_sg": [
            "chases", "finds", "sees", "believes", "learns", "receives", "admires", 'moves', 'writes', 
            'grows', 'belongs', 'inspires', 'motivates', 'deteriorates', "models", "admits", "studies", 
            "proves", "derives", 'rests', 'exists', 'speaks', 'votes', 'falls', 'wanders', 'fades', 
            'inspects', 'wears', 'laughs', "solves", "conjectures", "discovers", "asks", "invites", 
            "goes", "expects", 'sleeps', 'sings', 'works', 'reads', 'saves', 'thinks', 'yawns', 'jumps'
        ],
        "V_pl": [
            "chase", "find", "see", "believe", "learn", "receive", "admire", 'speak', 'write', 'fall', 
            'belong', 'inspire', 'deteriorate', 'laugh', "locate", "model", "admit", "study", "prove", 
            "derive", 'sleep', 'exist', 'vote', 'work', 'read', 'fade', 'inspect', "solve", "conjecture", 
            "discover", "invite", "ask", "go", 'eat', 'move', 'sing', 'grow', 'wander', 'save', 'think'
        ],

        ## Adverbs, Prepositions, Conjunctions, Relative Pronouns (for ix)
        "Adv": [
            "quickly", "silently", "happily", "desperately", "softly", "fairly",
            "elegantly", "intricately", "brilliantly", "deeply"
        ],
        "P": ["with", "about", "of", "from", "by", "without", "to", "for"],
        "Conj": ["and", "or"],
        "RelPronoun": ["who", "which", "that"],
    }

# ================================================================================================
# Exmples & Creation Functions


def main_example(print_traversal=False):
    '''
    Prints out a sentence generated from each of the three classes of languages
    '''
    print("\n=== Regular Grammar (RG) Sentence ===")
    fms_sentence = generate_sentence_fsm(fms_rules, lexicon, print_out=True)
    sentence_str = ' '.join(fms_sentence)
    sentence_str = sentence_str[0].upper() + sentence_str[1:]
    print(sentence_str + ".\n")

    print("=== Context-Free Grammar (CFG) Sentence ===")
    cf_sentence = generate_sentence(cf_rules, lexicon, max_expansion_per_symbol=10, max_recursion_depth=4, print_out=print_traversal)
    sentence_str = ' '.join(cf_sentence)
    sentence_str = sentence_str[0].upper() + sentence_str[1:]
    print(sentence_str + ".\n")


    print("\n=== Indexed Grammar (IXG) Sentence ===")
    ix_sentence = generate_sentence_noncf(ix_rules, lexicon, max_expansion_per_symbol=10, max_recursion_depth=4, print_out=print_traversal)  # limit to better represent English-like sentences
    sentence_str = ' '.join(ix_sentence)
    sentence_str = sentence_str[0].upper() + sentence_str[1:]
    print(sentence_str + ".\n")


    print("\n=== Context-Sensitive Grammar (CSG) Sentence ===")
    try:
        cs_sentence = generate_sentence_recursion_limits(cs_rules, lexicon, max_expansion_per_symbol=10, max_recursion_depth=4, print_out=print_traversal)
    except Exception as e:
        print(f"Error: {e}")
    # check is there are any rules in the sentence, if so, then replace them with terminals

    for sym in cs_sentence:
        if sym in lexicon.keys():
            print(f"post-processing replacement of {sym}")
            cs_sentence[cs_sentence.index(sym)] = random.choice(lexicon[sym])

    sentence_str = ' '.join(cs_sentence)
    sentence_str = sentence_str[0].upper() + sentence_str[1:]
    print(sentence_str + ".\n")

 
def main_export_lists(n, path = ''):
    cf_cnt, mini_ix_cnt, ix_cnt, cs_cnt = 0, 0, 0, 0

    with open("sentence_lists/cf_sentences.txt", "w") as cf_file:
        while cf_cnt < n:
            print(f"\n\n\nGenerating CF sentence {cf_cnt+1}...")
            cf_sentence = generate_sentence(cf_rules, lexicon, max_expansion_per_symbol=20, max_recursion_depth=10, print_out=False)
            if cf_sentence is not None and len(cf_sentence) > 10 and len(cf_sentence) < 21: # limit to better represent English-like sentences
                sentence_str = ' '.join(cf_sentence)
                sentence_str = sentence_str[0].upper() + sentence_str[1:]
                cf_file.write(sentence_str + ".\n")
                cf_cnt += 1

    with open("sentence_lists/ix_sentences.txt", "w") as ix_file:
        while ix_cnt < n:
            try:
                print(f"\n\n\nGenerating IX sentence {ix_cnt+1}...")
                ix_sentence = generate_sentence_noncf(ix_rules, lexicon, max_expansion_per_symbol=20, max_recursion_depth=10, print_out=False)
            except Exception as e:
                print(f"Error: {e}")
            if ix_sentence is not None and len(ix_sentence) > 10 and len(ix_sentence) < 21: # limit to better represent English-like sentences
                # check if there are at least 3 instances of any of these words "that, "which, "who" -- this is uncommented if this amount of dependencies is wanted
                # if ix_sentence.count("that") + ix_sentence.count("which") + ix_sentence.count("who") > 3:
                    sentence_str = ' '.join(ix_sentence)
                    sentence_str = sentence_str[0].upper() + sentence_str[1:]
                    ix_file.write(sentence_str + ".\n")
                    ix_cnt += 1

    with open("sentence_lists/cs_sentences.txt", "w") as cs_file:
        while cs_cnt < n:
            try:
                print(f"\n\n\nGenerating CS sentence {cs_cnt+1}...")
                # run with python -u to see print dispite recursion limits (python -u current-new-sentences.py)
                cs_sentence = generate_sentence_recursion_limits(cs_rules, lexicon, max_expansion_per_symbol=20, max_recursion_depth=10, print_out=False)
            except Exception as e:
                print(f"Error: {e}")
            if cs_sentence is not None and len(cs_sentence) > 10 and len(cs_sentence) < 21: # limit to the length of the other sentences
                sentence_str = ' '.join(cs_sentence)
                sentence_str = sentence_str[0].upper() + sentence_str[1:]
                cs_file.write(sentence_str + ".\n")
                cs_cnt += 1


if __name__ == "__main__":
    print_out_tree_traversal_of_sentence_construction = True

    main_example(print_out_tree_traversal_of_sentence_construction)
    main_example()

    path = os.path.join(os.getcwd())
    main_export_lists(250)
    print("\n\nExported sentences to files.\n\n")