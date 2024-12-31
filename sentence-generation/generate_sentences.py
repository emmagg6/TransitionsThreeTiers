import random
import sys



def generate_sentence_fsm(rules, lexicon, start_state="S", print_out=False):
    '''
    Generates a sentence using FSM rules.
    '''
    if print_out:
        print("\nStarting FSM sentence generation\n")

    current_states = [start_state]
    sentence = []

    while current_states:
        next_states = []
        for state in current_states:
            if state in rules:
                expansions = rules[state]
                if not expansions:
                    # End of sentence
                    if print_out:
                        print(f"Reached terminal symbol.")
                    continue
                expansion = random.choice(expansions)
                if print_out:
                    print(f"Expanding {state} with {expansion}")
                next_states.extend(expansion)
            elif state in lexicon:
                word = random.choice(lexicon[state])
                if print_out:
                    print(f"Replacing {state} with word '{word}'")
                sentence.append(word)
            else:
                # Terminal word
                sentence.append(state)
        current_states = next_states

    if print_out:
        print()

    return sentence


def generate_sentence(rules, lexicon, symbols=None, max_expansion_per_symbol=10, max_recursion_depth=1e5, print_out=False):
    if print_out:
        print("\nStarting sentence generation\n")
        sys.stdout.flush()

    # start symbol mapping from "S" --> NP VP
    start_expansions = rules["S"]
    start_expansion = random.choice(start_expansions)
    if print_out:
        print("Initial expansion: ", start_expansion)
    initial_symbols = start_expansion

    # initialize a shared expansion_counts dictionary (expansion_counts needs to be shared across different recursive calls) per context symbol
    expansion_counts = {}

    sentence = []
    for initial_symbol in initial_symbols:

        if print_out:    
            print("\nPartial symbol: \n", initial_symbol)

        part = get_expansion_cf([initial_symbol], rules, lexicon, max_expansion_per_symbol, expansion_counts, print_out, max_recursion_depth)
        sentence.extend(part)

        if print_out:
            print("\nSentence part: \n", sentence)
            sys.stdout.flush()

    for i, sym in enumerate(sentence):
        if sym in lexicon.keys():
            sentence[i] = random.choice(lexicon[sym])

    if print_out:
        print("\nFinal sentence: ", sentence)
    return sentence


def get_expansion_cf(symbols, rules, lexicon, max_expansion_per_symbol, expansion_counts = None, print_out=False, 
                    max_recursion_depth=1e5, current_recursion_depth=0):
    if expansion_counts is None:
        expansion_counts = {}


    i = 0
    while i < len(symbols):
        sym = symbols[i]
        # to limit the totoal number of expansions of all symbols (limited futher from each symbols)

        if sym in rules:
            # Initialize count if symbol not yet expanded
            if sym not in expansion_counts:
                expansion_counts[sym] = 0
            
            if expansion_counts[sym] < max_expansion_per_symbol and current_recursion_depth < max_recursion_depth:
                expansion_counts[sym] += 1  # Increment the expansion count

                expansions = rules[sym]
                if not expansions:
                    print(f"No expansions available for symbol {sym}.")
                    i += 1
                    continue
                expansion = random.choice(expansions)
                
                if isinstance(expansion, str):
                    expansion = [expansion]
                elif expansion is None:
                    expansion = []
                elif not isinstance(expansion, list):
                    expansion = list(expansion)

                if expansion == []:
                    # remove that symbol
                    symbols = symbols[:i] + symbols[i+1:]
                    if print_out:
                        print(f"Removed {sym}, now symbols: {symbols}")
                else:
                    symbols = symbols[:i] + expansion + symbols[i+1:]
                    if print_out:
                        print(f"Expanded {sym} to {expansion}") 

                    # recursively expand the newly added symbols
                    j = i
                    while j < i + len(expansion):
                        if symbols[j] in rules:
                            # recursively expand the symbol ('NoneType' errors can be incurred if the while loop completes 
                            # without triggering any of the return statements inside the conditional blocks )
                            new_symbols = get_expansion_cf(
                                [symbols[j]], rules, lexicon, 
                                max_expansion_per_symbol, expansion_counts, print_out,
                                max_recursion_depth, current_recursion_depth + 1
                            )
                            
                            if new_symbols is not None and new_symbols != []:
                                symbols = symbols[:j] + new_symbols + symbols[j+1:]
                            else:
                                # if recursion expansion returns empty, remove the symbol
                                symbols = symbols[:j] + symbols[j+1:]
                        j += 1
                    i += len(expansion)
            elif expansion_counts[sym] >= max_expansion_per_symbol:
                if print_out:
                    print(f"\nMax expansion count reached for {sym}. Enforcing terminal expansion.")
                    sys.stdout.flush()
                    print("Symbols: ", symbols)
                # enforce terminal expansion for the remaining symbols
                # while any are in the keys of the rules, since we are mapping to the symbols in the lexicon and then afterward mapping to the terminal
                symbols = forced_terminal_expansion_cf(symbols, lexicon, print_out)   
                return symbols  
            else:
                if print_out:
                    print(f"\nMax recursion depth reached for {sym}. Enforcing terminal expansion.")
                    sys.stdout.flush()
                    print("Symbols: ", symbols)
                for i, sym in enumerate(symbols):
                    syms = forced_terminal_expansion_cf(sym, rules, lexicon, print_out)
                    if isinstance(syms, list):
                        symbols = symbols[:i] + syms + symbols[i+1:]
                    else:
                        symbols = symbols[:i] + [syms] + symbols[i+1:]
                return symbols
        else:
            i += 1  

    return symbols

def forced_terminal_expansion_cf(sym, rules, lexicon, print_out=False):
    if print_out:
        print("\nEntered forced terminal expansion\n")
        sys.stdout.flush()


    if sym == "NP" or sym == "VP":
        # quickest to terminal  NP --> NP_sg or NP_pl, NP_sg --> Det N_sg, NP_pl --> Det N_pl

        epsilon = random.uniform(0, 1)

        if sym == "NP":
            epsilon2 = random.uniform(0, 1)
            if epsilon < 0.75:
                if epsilon2 < 0.5:
                    if print_out:
                        print(f"Expanded {sym} via {epsilon:.2f} to ['Det_sg', 'N_sg']")
                    sym = ["Det_sg", "N_sg"]
                else:
                    if print_out:
                        print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'N_pl']")
                    sym = ["Det_pl", "N_pl"]
            else:
                if print_out:
                    print(f"Expanded {sym} via {epsilon:.2f} to ['ProperNoun_sg']")
                sym = ["ProperNoun_sg"]

        if sym == "VP":
            if epsilon < 0.5:
                if print_out:
                    print(f"Expanded {sym} via {epsilon:.2f} to ['V_sg']")
                sym = ["V_sg"]
            else:
                if print_out:
                    print(f"Expanded {sym} via {epsilon:.2f} to ['V_pl']")
                sym = ["V_pl"]

    #### SINGULAR ####
    if sym == "NP_sg" or sym == "VP_sg" or sym == "NP_conj_sg" or sym == "VP_sg" or sym == "VP_conj_sg" or sym == "PP_conj" or sym == "PP":
        
        if sym == "NP_sg" or sym == "NP_conj_sg": # in this case, we just make NP singular
            epsilon = random.uniform(0, 1)
            if epsilon < 0.67:
                epsilon2 = random.uniform(0, 1)
                if epsilon2 < 0.5:
                    if print_out:
                        print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['Det_sg', 'Adj', 'N_sg']")
                    sym = ["Det_sg", "Adj", "N_sg"]
                else:
                    if print_out:
                        print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['Det_sg', 'N_sg']")
                    sym = ["Det_sg", "N_sg"]
            else:
                if print_out:
                    print(f"Expanded {sym} via {epsilon:.2f} to ['ProperNoun_sg']")
                sym = ["ProperNoun_sg"]

        if sym == "VP_sg":
            if print_out:
                print(f"Expanded {sym} to ['V_sg']")
            sym = ["V_sg"]

        if sym == "VP_conj_sg":
            if print_out:
                print(f"Expanded {sym}to ['Conj', 'V_sg']")
            sym = ["Conj", "V_sg"]

        if sym == "PP":
            # PP --> P NP, NP --> Det_sg N_sg
            if print_out:
                print(f"Expanded {sym} to ['P', 'Det_sg', 'N_sg']")
            sym = ["P", "Det_sg", "N_sg"]
        
        if sym == "PP_conj":
            # PP_conj --> Conj PP, PP --> P, Det_sg, N_sg 
            if print_out:
                print(f"Expanded {sym} to ['Conj', 'P', 'Det_sg', 'N_sg']")
            sym = ["Conj", "P", "Det_sg", "N_sg"]
                
    ### PLURAL ###
    if sym == "NP_pl" or sym == "VP_pl" or sym == "NP_conj_pl" or sym == "VP_conj_pl":
        
        if sym == "NP_pl" or sym == "NP_conj_pl":
            epsilon = random.uniform(0, 1)
            if epsilon < 0.5:
                if print_out:
                    print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'Adj', 'N_pl']")
                sym = ["Det_pl", "Adj", "N_pl"]
            else:
                if print_out:
                    print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'N_pl']")
                sym = ["Det_pl", "N_pl"]

        if sym == "VP_pl":
            if print_out:
                print(f"Expanded {sym} to ['V_pl']")
            sym = ["V_pl"]

        if sym == "VP_conj_pl":
            if print_out:
                print(f"Expanded {sym} to ['Conj', 'V_pl']")
            sym = ["Conj", "V_pl"]
        
    return sym


def generate_sentence_noncf(rules, lexicon, symbols=None, max_expansion_per_symbol=10, max_recursion_depth=1e5, print_out=False):
    if print_out:
        print("\nStarting sentence generation\n")
        sys.stdout.flush()

    # Start symbol mapping from "S"
    start_expansions = rules["S"]
    start_expansion = random.choice(start_expansions)
    if print_out:
        print("Initial expansion: ", start_expansion)
    initial_symbols = start_expansion 
    ## by starting expansions of the relations between singular and plural, the relations are maintained, since S --> NP_sg VP_sg | NP_pl VP_pl

    sentence = []
    for initial_symbol in initial_symbols:
        # initialize a shared expansion_counts dictionary (expansion_counts needs to be shared across different recursive calls) per context symbol
        expansion_counts = {}

        if print_out:    
            print("\nPartial symbol: \n", initial_symbol)

        part = get_expansion_noncf([initial_symbol], rules, lexicon, max_expansion_per_symbol, expansion_counts, print_out, max_recursion_depth)
        sentence.extend(part)

        if print_out:
            print("\nSentence part: \n", sentence)
            sys.stdout.flush()

    for i, sym in enumerate(sentence):
        if sym in lexicon.keys():
            sentence[i] = random.choice(lexicon[sym])

    if print_out:
        print("\nFinal sentence: ", sentence)
    return sentence


def get_expansion_noncf(symbols, rules, lexicon, max_expansion_per_symbol, expansion_counts = None, print_out=False, 
                    max_recursion_depth=1e5, current_recursion_depth=0):
    if expansion_counts is None:
        expansion_counts = {}

    i = 0
    while i < len(symbols):
        sym = symbols[i]
        # to limmit the totoal number of expansions of all symbols (limited futher from each symbols)
        if sym in rules:
            # Initialize count if symbol not yet expanded
            if sym not in expansion_counts:
                expansion_counts[sym] = 0
            
            if expansion_counts[sym] < max_expansion_per_symbol and current_recursion_depth < max_recursion_depth:
                expansion_counts[sym] += 1  # Increment the expansion count

                expansions = rules[sym]
                if not expansions:
                    print(f"No expansions available for symbol {sym}.")
                    i += 1
                    continue
                expansion = random.choice(expansions)
                
                if isinstance(expansion, str):
                    expansion = [expansion]
                elif expansion is None:
                    expansion = []
                elif not isinstance(expansion, list):
                    expansion = list(expansion)

                if expansion == []:
                    # remove that symbol
                    symbols = symbols[:i] + symbols[i+1:]
                    if print_out:
                        print(f"Removed {sym}, now symbols: {symbols}")
                else:
                    symbols = symbols[:i] + expansion + symbols[i+1:]
                    if print_out:
                        print(f"Expanded {sym} to {expansion}") 

                    # recursively expand the newly added symbols
                    j = i
                    while j < i + len(expansion):
                        if symbols[j] in rules:
                            # recursively expand the symbol ('NoneType' errors can be incurred if the while loop completes 
                            # without triggering any of the return statements inside the conditional blocks )
                            new_symbols = get_expansion_noncf(
                                [symbols[j]], rules, lexicon, 
                                max_expansion_per_symbol, expansion_counts, print_out,
                                max_recursion_depth, current_recursion_depth + 1
                            )
                            
                            if new_symbols is not None and new_symbols != []:
                                symbols = symbols[:j] + new_symbols + symbols[j+1:]
                            else:
                                # if recursion expansion returns empty, remove the symbol
                                symbols = symbols[:j] + symbols[j+1:]
                        j += 1
                    i += len(expansion)
            elif expansion_counts[sym] >= max_expansion_per_symbol:
                if print_out:
                    print(f"\nMax expansion count reached for {sym}. Enforcing terminal expansion.")
                    sys.stdout.flush()
                    print("Symbols: ", symbols)
                # enforce terminal expansion for the remaining symbols
                # while any are in the keys of the rules, since we are mapping to the symbols in the lexicon and then afterward mapping to the terminal
                symbols = forced_terminal_expansion_mcs(symbols, lexicon, print_out)   
                return symbols  
            else:
                if print_out:
                    print(f"\nMax recursion depth reached for {sym}. Enforcing terminal expansion.")
                    sys.stdout.flush()
                    print("Symbols: ", symbols)
                symbols = forced_terminal_expansion_mcs(symbols, lexicon, print_out)
                return symbols
        else:
            i += 1  

    return symbols
            

def forced_terminal_expansion_mcs(symbols, lexicon, print_out=False):
    if print_out:
        print("Entered forced terminal expansion")
    lexicon_keys = lexicon.keys()
    lexicon_values = lexicon.values()
    non_lex = True
    while non_lex:
        # if max expansion is reached, force terminals that agree with the rules
        for sym in symbols:

            if sym == "NP" or sym == "VP":
                # quickest to terminal  NP --> NP_sg or NP_pl, NP_sg --> Det N_sg, NP_pl --> Det N_pl
                where = symbols.index(sym)
                epsilon = random.uniform(0, 1)
                if sym == "NP":
                    epsilon2 = random.uniform(0, 1)
                    if epsilon < 0.75:
                        if epsilon2 < 0.5:
                            symbols = symbols[:where] + ["Det_sg", "N_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Det_sg', 'N_sg']")
                            where += 1
                        else:
                            symbols = symbols[:where] + ["Det_pl", "N_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'N_pl']")
                            where += 1
                    else:
                        symbols = symbols[:where] + ["ProperNoun_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['ProperNoun_sg']")

                if sym == "VP":
                    if epsilon < 0.5:
                        symbols = symbols[:where] + ["V_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['V_sg']")
                    else:
                        symbols = symbols[:where] + ["V_pl"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['V_pl']")

                # English restriction : check for preceding determiner to avoid duplication (uncomment this for a slight deviation closer to English)
                if where > 0 and symbols[where-1] in ["Det_sg", "Det_pl"]:
                    if print_out:
                        print(f"Skipped inserting determiner before position {where} to avoid duplication.")
                    continue  # skip insertion to prevent duplication

            #### SINGULAR ####
            if sym == "NP_sg" or sym == "VP_sg" or sym == "NP_conj_sg" or sym == "RC_sg" or sym == "VP_sg" or sym == "VP_conj_sg" or sym == "PP_conj" or sym == "PP":
                where = symbols.index(sym)
                
                if sym == "NP_sg" or sym == "NP_conj_sg": # in this case, we just make NP singular
                    epsilon = random.uniform(0, 1)
                    if epsilon < 0.67:
                        epsilon2 = random.uniform(0, 1)
                        if epsilon2 < 0.5:
                            symbols = symbols[:where] + ["Det_sg", "Adj", "N_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['Det_sg', 'Adj', 'N_sg']")
                            where += 2
                        else:
                            symbols = symbols[:where] + ["Det_sg", "N_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['Det_sg', 'N_sg']")
                            where += 1
                    else:
                        symbols = symbols[:where] + ["ProperNoun_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['ProperNoun_sg']")
                    ### for nested and cross-serial dependencies (coordinated phrases) check if the next symbol is a verb phrase, if so, expand that now before continuing
                    if where + 1 < len(symbols):
                        if symbols[where + 1] == "Adv":
                            where += 1
                        if symbols[where + 1] == "VP_sg" or symbols[where + 1] == "VP":
                            if where + 2 < len(symbols):
                                symbols = symbols[:where + 1] + ["V_sg"] + symbols[where + 2:]
                                if print_out:
                                    print(f"Expanded VP_sg to ['V_sg']")
                            else:
                                symbols = symbols = symbols[:where + 1] + ["V_sg"]
                                if print_out:
                                    print(f"Expanded VP_sg to ['V_sg']")

                if sym == "VP_sg":
                    symbols = symbols[:where] + ["V_sg"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['V_sg']")

                if sym == "VP_conj_sg":
                    symbols = symbols[:where] + ["Conj", "V_sg"] + symbols[where + 1:]
                    if print_out:
                            print(f"Expanded {sym}to ['Conj', 'V_sg']")

                if sym == "PP":
                    # PP --> P, Det_sg, N_sg
                    symbols = symbols[:where] + ["P", "Det_sg", "N_sg"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['P', 'Det_sg', 'N_sg']")

                if sym == "PP_conj":
                    # PP_conj --> Conj PP, PP --> P, Det_sg, N_sg 
                    symbols = symbols[:where] + ["Conj", "P", "Det_sg", "N_sg"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['Conj', 'P', 'Det_sg', 'N_sg']")

                if sym == "RC_sg":
                    symbols = symbols[:where] + ["RelPronoun", "V_sg"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['RelPronoun', 'V_sg']")
                        
    

            ### PLURAL ###
            if sym == "NP_pl" or sym == "VP_pl" or sym == "NP_conj_pl" or sym == "RC_pl" or sym == "VP_conj_pl":
                where = symbols.index(sym)
                
                if sym == "NP_pl" or sym == "NP_conj_pl":
                    epsilon = random.uniform(0, 1)
                    if epsilon < 0.5:
                        symbols = symbols[:where] + ["Det_pl", "Adj", "N_pl"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'Adj', 'N_pl']")
                        where += 2
                    else:
                        symbols = symbols[:where] + ["Det_pl", "N_pl"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'N_pl']")
                        where += 1
                    ### for nested and cross-serial dependencies (coordinated phrases) check if the next symbol is a verb phrase, if so, expand that now before continuing
                    if where + 1 < len(symbols):
                        if symbols[where + 1] == "Adv":
                            where += 1
                        if symbols[where + 1] == "VP_pl" or symbols[where + 1] == "VP":
                            if where + 2 < len(symbols):
                                symbols = symbols[:where + 1] + ["V_pl"] + symbols[where + 2:]
                                if print_out:
                                    print(f"Expanded VP_pl to ['V_pl']")
                            else:
                                symbols = symbols = symbols[:where + 1] + ["V_pl"]
                                if print_out:
                                    print(f"Expanded VP_pl to ['V_pl']")

                if sym == "VP_pl":
                    symbols = symbols[:where] + ["V_pl"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['V_pl']")

                if sym == "VP_conj_pl":
                    symbols = symbols[:where] + ["Conj", "V_pl"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['Conj', 'V_pl']")

                if sym == "RC_pl":
                    symbols = symbols[:where] + ["RelPronoun", "V_pl"] + symbols[where + 1:]
                    if print_out:
                        print(f"Expanded {sym} to ['RelPronoun', 'V_pl']")


        
        non_lex = any(sym not in lexicon for sym in symbols)
        if print_out:
            print("Symbols: ", symbols)
            print("Non lexicon: ", non_lex)
    return symbols


def generate_sentence_recursion_limits(rules, lexicon, symbols=None, max_expansion_per_symbol=10, max_recursion_depth=1e5, print_out=False):
    if print_out:
        print("\n --Starting sentence generation-- \n")
        sys.stdout.flush()


    # Start symbol mapping from "S"
    start_expansions = rules["S"]
    start_expansion = tuple(start_expansions[0])
    if print_out:
        print("Initial expansion: ", start_expansion)
    initial_symbols = start_expansion

    # Initial expansion from context-sensitive production branches
    cs_rule = initial_symbols
    context_expansions = rules[initial_symbols]
    context_expansion = random.choice(context_expansions)
    if print_out:
        print("Context expansion: ", context_expansion)
    context_symbols = context_expansion

    sentence = []
    for context_symbol in context_symbols:
        # initialize a shared expansion_counts dictionary (expansion_counts needs to be shared across different recursive calls) per context symbol
        expansion_counts = {}

        if print_out:    
            print("\nContext symbol: \n", context_symbol)
            
        part = get_expansion([context_symbol], rules, lexicon, max_expansion_per_symbol, expansion_counts, print_out, max_recursion_depth)
        sentence.extend(part)

        if print_out:
            print("\nSentence part: ", sentence)
            sys.stdout.flush()

    for i, sym in enumerate(sentence):
        if sym in lexicon.keys():
            sentence[i] = random.choice(lexicon[sym])

    if print_out:
        print("\nFinal sentence: ", sentence)
    return sentence


def get_expansion(symbols, rules, lexicon, max_expansion_per_symbol, expansion_counts = None, print_out=False, 
                    max_recursion_depth=1e5, current_recursion_depth=0):
    if expansion_counts is None:
        expansion_counts = {}

    i = 0
    while i < len(symbols):
        sym = symbols[i]
        # to limmit the totoal number of expansions of all symbols (limited futher from each symbols)
        if sym in rules:
            # Initialize count if symbol not yet expanded
            if sym not in expansion_counts:
                expansion_counts[sym] = 0
            
            if expansion_counts[sym] < max_expansion_per_symbol and current_recursion_depth < max_recursion_depth:
                expansion_counts[sym] += 1  # Increment the expansion count

                expansions = rules[sym]
                if not expansions:
                    print(f"No expansions available for symbol {sym}.")
                    i += 1
                    continue
                expansion = random.choice(expansions)
                
                if isinstance(expansion, str):
                    expansion = [expansion]
                elif expansion is None:
                    expansion = []
                elif not isinstance(expansion, list):
                    expansion = list(expansion)

                if expansion == []:
                    # remove that symbol
                    symbols = symbols[:i] + symbols[i+1:]
                    if print_out:
                        print(f"Removed {sym}, now symbols: {symbols}")
                else:
                    symbols = symbols[:i] + expansion + symbols[i+1:]
                    if print_out:
                        print(f"Expanded {sym} to {expansion}") 

                    # recursively expand the newly added symbols
                    j = i
                    while j < i + len(expansion):
                        if symbols[j] in rules:
                            # recursively expand the symbol ('NoneType' errors can be incurred if the while loop completes 
                            # without triggering any of the return statements inside the conditional blocks )
                            new_symbols = get_expansion(
                                [symbols[j]], rules, lexicon, 
                                max_expansion_per_symbol, expansion_counts, print_out,
                                max_recursion_depth, current_recursion_depth + 1
                            )
                            
                            if new_symbols is not None and new_symbols != []:
                                symbols = symbols[:j] + new_symbols + symbols[j+1:]
                            else:
                                # if recursion expansion returns empty, remove the symbol
                                symbols = symbols[:j] + symbols[j+1:]
                        j += 1
                    i += len(expansion)
            elif expansion_counts[sym] >= max_expansion_per_symbol:
                if print_out:
                    print(f"\nMax expansion count reached for {sym}. Enforcing terminal expansion.")
                    # sys.stdout.flush()
                    print("Symbols: ", symbols)
                # enforce terminal expansion for the remaining symbols
                # while any are in the keys of the rules, since we are mapping to the symbols in the lexicon and then afterward mapping to the terminal
                symbols = forced_terminal_expansion(symbols, lexicon, print_out)   
                return symbols  
            else:
                if print_out:
                    print(f"\nMax recursion depth reached for {sym}. Enforcing terminal expansion.")
                    # sys.stdout.flush()
                    print("Symbols: ", symbols)
                symbols = forced_terminal_expansion(symbols, lexicon, print_out)
                return symbols
        else:
            i += 1  

    return symbols
            

def forced_terminal_expansion(symbols, lexicon, print_out=False):
    if print_out:
        print("Entered forced terminal expansion")
    lexicon_keys = lexicon.keys()
    lexicon_values = lexicon.values()
    non_lex = True
    while non_lex:
        # if max expansion is reached, force terminals that agree with the rules
        for sym in symbols:
                # if max_expansion is minimal, then start from S --> NP_seq VP_seq
                # so, if sym == ["NP_sequence", "VP_placeholder"] then expand to either NP_sg, NP VP_sg or NP_pl NP VP_pl (let VP_seq = [] in this forced terminal case)
                if sym == ("NP_sequence", "VP_placeholder") or sym == ["NP_sequence", "VP_placeholder"]: # this will be taken care of before this forced terminal section is reached, but incase the initialization gets changed
                    where = symbols.index(sym)
                    epsilon = random.uniform(0, 1)
                    if epsilon < 0.5:
                        epsilon2 = random.uniform(0, 1)
                        epsilon2 = random.uniform(0, 1)
                        if epsilon2 < 0.5:
                            symbols = symbols[:where] + ["NP_sg", "NP_sg", "VP_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['NP_sg', 'NP_sg', 'VP_sg']")
                        else:
                            symbols = symbols[:where] + ["NP_sg", "NP_pl", "VP_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['NP_sg', 'NP_pl', 'VP_sg']")
                    elif epsilon >= 0.5:
                        epsilon2 = random.uniform(0, 1)
                        if epsilon2 < 0.5:
                            symbols = symbols[:where] + ["NP_pl", "NP_sg", "VP_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['NP_pl', 'NP_sg', 'VP_pl']")
                        else:
                            symbols = symbols[:where] + ["NP_pl", "NP_pl", "VP_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['NP_pl', 'NP_pl', 'VP_pl']")

                if sym == "NP_sequence": 
                    # for context-dependence, if there is a "VP_sg" or a "VP_pl" directly succeeding this symbol, change that first
                    # so that the agreement is maintained before additional expansions loses track of the corresponding verb phrase
                    where = symbols.index(sym)
                    if where + 1 < len(symbols):
                        if symbols[where + 1] == "VP_sg":
                            if epsilon < 0.5:
                                if where + 2 < len(symbols):
                                    symbols = symbols[:where + 1] + ["V_sg"] + symbols[where + 2:]
                                    if print_out:
                                        print(f"Expanded {sym} via {epsilon:.2f} to ['V_sg']")
                                else:
                                    symbols = symbols[:where + 1] + ["Adv", "V_sg"]
                                    if print_out:
                                        print(f"Expanded {sym} via {epsilon:.2f} to ['Adv', 'V_sg']")
                        if symbols[where + 1] == "VP_pl":
                            if epsilon < 0.5:
                                if where + 2 < len(symbols):
                                    symbols = symbols[:where + 1] + ["V_pl"] + symbols[where + 2:]
                                    if print_out:
                                        print(f"Expanded {sym} via {epsilon:.2f} to ['V_pl']")
                                else:
                                    symbols = symbols[:where + 1] + ["Adv", "V_pl"]
                                    if print_out:
                                        print(f"Expanded {sym} via {epsilon:.2f} to ['V_pl']")


                    where = symbols.index(sym)
                    epsilon = random.uniform(0, 1)
                    if epsilon <= 0.5:
                        epsilon2 = random.uniform(0, 1)
                        if epsilon2 < 0.67:
                            epsilon3 = random.uniform(0, 1)
                            if epsilon3 < 0.5:
                                symbols = symbols[:where] + ["Det_sg", "Adj", "N_sg"] + symbols[where + 1:]
                                if print_out:
                                    print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f}, {epsilon3:.2f} to ['Det_sg', 'Adj', 'N_sg']")
                            else:
                                symbols = symbols[:where] + ["Det_sg", "N_sg"] + symbols[where + 1:]
                                if print_out:
                                    print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f}, {epsilon3:.2f} to ['Det_sg', 'N_sg']")
                        else:
                            symbols = symbols[:where] + ["ProperNoun_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['ProperNoun_sg']")
                    elif epsilon > 0.5:
                        if symbols[where - 1] == "N_pl":
                            symbols = symbols[:where] + ["Det_pl", "N_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'N_pl']")
                        else:
                            symbols = symbols[:where] + ["Det_sg", "N_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Det_sg', 'N_sg']")


                #### SINGULAR ####
                if sym == "NP" or sym == "NP_sg" or sym == "VP_sg" or sym == "NPPrime_sg" or sym == "VP_sequence" or sym == "VP_sg" or sym == "RC_sg":
                    #NP_seq --> NP , then have NP --> NP_sg , then NP_sg --> Det N_sg, then select terminals of "Det" and "N"
                    where = symbols.index(sym)
                    epsilon = random.uniform(0, 1)
                    if sym == "NP" or sym == "NP_sg": # in this case, we just make NP singular
                        if epsilon < 0.67:
                            epsilon2 = random.uniform(0, 1)
                            if epsilon2 < 0.5:
                                symbols = symbols[:where] + ["Det_sg", "Adj", "N_sg"] + symbols[where + 1:]
                                if print_out:
                                    print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['Det_sg', 'Adj', 'N_sg']")
                            else:
                                symbols = symbols[:where] + ["Det_sg", "N_sg"] + symbols[where + 1:]
                                if print_out:
                                    print(f"Expanded {sym} via {epsilon:.2f}, {epsilon2:.2f} to ['Det_sg', 'N_sg']")
                        else:
                            symbols = symbols[:where] + ["ProperNoun_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['ProperNoun_sg']")

                    if sym == "VP_sequence" or  sym == "VP_sg":
                        symbols = symbols[:where] + ["V_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} via {epsilon:.2f} to ['V_sg']")

                    if sym == "PP_conj":
                        # PP_conj --> Cong PP
                        symbols = symbols[:where] + ["Conj", "P", "Det_sg", "N_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} to ['Conj', 'P', 'Det_sg', 'N_sg']")
                    
                    if sym == "NPPrime_sg":
                        # NPprime_sg --> PP , PP --> P, Det_sg, N_sg
                        symbols = symbols[:where] + ["P", "Det_sg", "N_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} to ['P', 'Det_sg', 'N_sg']")
                    
                    if sym == "RC_sg":
                        symbols = symbols[:where] + ["RelPronoun", "V_sg"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} to ['RelPronoun', 'V_sg']")
        

                ### PLURAL ###
                if sym == "NP_pl" or sym == "NPPrime_pl" or sym == "VP_pl" or sym == "RC_pl":
                    where = symbols.index(sym)
                    if sym == "VP_pl":
                        # replace sym with "V_pl" or "Adv V_pl"
                        epsilon = random.uniform(0, 1)
                        if epsilon < 0.5:
                            symbols = symbols[:where] + ["Adv", "V_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Adv', 'V_pl']")
                        else: 
                            symbols = symbols[:where] + ["V_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['V_pl']")

                    if sym == "NP_pl":
                        # NP_pl --> Det_pl N_pl or Det_pl Adj N_pl
                        epsilon = random.uniform(0, 1)
                        if epsilon < 0.5:
                            symbols = symbols[:where] + ["Det_pl", "Adj", "N_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'Adj', 'N_pl']")
                        else:
                            symbols = symbols[:where] + ["Det_pl", "N_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} via {epsilon:.2f} to ['Det_pl', 'N_pl']")

                    if sym == "NPPrime_pl":
                        # NPprime_pl --> PP , PP --> P, Det_pl, N_pl
                        symbols = symbols[:where] + ["P", "Det_pl", "N_pl"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} to ['P', 'Det_pl', 'N_pl']")

                    if sym == "RC_pl":
                        symbols = symbols[:where] + ["RelPronoun", "V_pl"] + symbols[where + 1:]
                        if print_out:
                            print(f"Expanded {sym} to ['RelPronoun', 'V_pl']")
    
                if sym == "PP" or sym == "PP_conj":
                    where = symbols.index(sym)
                    if sym == "PP_conj":
                        epsilon = random.uniform(0, 1)
                        if epsilon < 0.5:
                            # PP_conj --> Conj PP , pp --> P Det_pl N_pl
                            symbols = symbols[:where] + ["Conj", "P", "Det_pl", "N_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} to ['Conj', 'P', 'Det_pl', 'N_pl'] due to agreement with previous symbol {symbols[where - 1]}")
                        else:
                            # PP_conj --> Cong PP
                            where = symbols.index(sym)
                            symbols = symbols[:where] + ["Conj", "P", "Det_sg", "N_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} to ['Conj', 'P', 'Det_sg', 'N_sg'] due to agreement with previous symbol {symbols[where - 1]}")
                    if sym == "PP":
                        epsilon = random.uniform(0, 1)
                        if epsilon < 0.5:
                            # PP --> P Det N_sg
                            symbols = symbols[:where] + ["P", "Det_pl", "N_pl"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} to ['P', 'Det_pl', 'N_pl'] due to agreement with previous symbol {symbols[where - 1]}")
                        else:
                            # PP --> P Det N_pl
                            symbols = symbols[:where] + ["P", "Det_sg", "N_sg"] + symbols[where + 1:]
                            if print_out:
                                print(f"Expanded {sym} to ['P', 'Det_sg', 'N_sg'] due to agreement with previous symbol {symbols[where - 1]}")

        
        non_lex = any(sym not in lexicon for sym in symbols)
        if print_out:
            print("\nSymbols: ", symbols)
            print("\nNon lexicon: ", non_lex)
    return symbols
