def read_grammar(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    variables = lines[0].strip().split(': ')[1].split(', ')
    terminals = lines[1].strip().split(': ')[1].split(', ')
    start_var = lines[2].strip().split(': ')[1]
    rules = {}
    for line in lines[4:]:
        lhs, rhs = line.strip().split(', ')
        if lhs not in rules:
            rules[lhs] = []
        rules[lhs].append(rhs)
    return variables, terminals, start_var, rules


def remove_epsilon(rules):
    eps_vars = set()
    for lhs, rhs_list in rules.items():
        if '0' in rhs_list:
            eps_vars.add(lhs)
            rhs_list.remove('0')
    while eps_vars:
        lhs = eps_vars.pop()
        for rhs_list in rules.values():
            for rhs in rhs_list:
                if lhs in rhs:
                    new_rhs = ''
                    for char in rhs:
                        if char != lhs:
                            new_rhs += char
                    if not new_rhs:
                        new_rhs = '0'
                    if new_rhs not in rhs_list:
                        rhs_list.append(new_rhs)
    return rules


def remove_unit_productions(rules, variables):
    for lhs, rhs_list in rules.items():
        for production in rhs_list:
            if production in variables:
                unit_production = production
                rhs_list.remove(production)
                unit_pr_rhs_list = rules[unit_production]
                for rhs in unit_pr_rhs_list:
                    if rhs not in rhs_list:
                        rhs_list.append(rhs)
    return rules


def convert_to_len2(variables, rules, unused_symbols):
    new_rules = {}
    for lhs, rhs_list in rules.items():
        for rhs in rhs_list:
            available_in_new_rules = False
            if len(rhs) > 2:

                for new_rules_lhs, new_rules_rhs_list in new_rules.items():
                    if rhs[1:] in new_rules_rhs_list:
                        available_in_new_rules = True
                        new_var = new_rules_lhs
                        new_rhs = str(rhs[0]) + str(new_var)
                        rhs_list.remove(rhs)
                        rhs_list.append(new_rhs)
                        break

                if not available_in_new_rules:
                    new_var = unused_symbols[len(unused_symbols) - 1]
                    unused_symbols.pop()
                    variables.append(new_var)
                    new_rhs = str(rhs[0]) + str(new_var)
                    new_var_production = rhs[1:]
                    rhs_list.remove(rhs)
                    rhs_list.append(new_rhs)
                    new_rules[new_var] = [new_var_production]

    for lhs, rhs_list in new_rules.items():
        rules[lhs] = rhs_list

    return rules, variables, unused_symbols


def remove_nonsingle_terminals(rules, variables, terminals, unused_symbols):
    new_rules = {}
    for lhs, rhs_list in rules.items():
        productions_changed = False
        new_productions = []
        for rhs in rhs_list:
            new_rhs = rhs
            if len(rhs) > 1:
                if rhs[0] in terminals or rhs[1] in terminals:
                    if rhs[0] in terminals:
                        if rhs[0] not in new_rules.values():
                            new_var = unused_symbols[len(unused_symbols) - 1]
                            variables.append(new_var)
                            unused_symbols.pop()
                            new_rules[new_var] = rhs[0]
                            new_rhs = str(new_var) + new_rhs[1]
                            productions_changed = True
                        else:
                            for new_rules_lhs, new_rules_rhs in new_rules.items():
                                if new_rules_rhs == rhs[0]:
                                    new_rhs = str(new_rules_lhs) + new_rhs[1]
                                    productions_changed = True
                                    break

                    if rhs[1] in terminals:
                        if rhs[1] not in new_rules.values():
                            new_var = unused_symbols[len(unused_symbols) - 1]
                            variables.append(new_var)
                            unused_symbols.pop()
                            new_rules[new_var] = rhs[1]
                            new_rhs = new_rhs[0] + str(new_var)
                            productions_changed = True
                        else:
                            for new_rules_lhs, new_rules_rhs in new_rules.items():
                                if new_rules_rhs == rhs[1]:
                                    new_rhs = new_rhs[0] + str(new_rules_lhs)
                                    productions_changed = True
                                    break

            new_productions.append(new_rhs)

        if productions_changed:
            rules[lhs] = new_productions

    for lhs, rhs_list in new_rules.items():
        rules[lhs] = list(rhs_list)

    return rules, variables, terminals, unused_symbols


def convert_to_cnf(variables, terminals, start_var, rules):
    # If the start_var exists on rhs it creates
    # a new rule called S0 that goes to start_var
    exit_loop = False
    for lhs, rhs_list in rules.items():
        for production in rhs_list:
            if start_var in production:
                rules['S0'] = [start_var]
                variables.append('S0')
                exit_loop = True
                break
        if exit_loop:
            break

    # Removes epsilon(lambda) from grammar
    while True:
        null_exists = False
        for lhs, rhs_list in rules.items():
            for production in rhs_list:
                if production == '0':
                    null_exists = True
                    break
            if null_exists:
                break
        if null_exists:
            remove_epsilon(rules)
        else:
            break

    # Removes unit productions
    remove_unit_productions(rules, variables)

    # Removes rules with empty productions
    empty_rules = []
    for lhs, rhs_list in rules.items():
        if len(rhs_list) == 0:
            empty_rules.append(lhs)
    for rule in empty_rules:
        rules.pop(rule)
        variables.remove(rule)

    # We use unused symbols later to create new grammar rules
    unused_symbols = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    unused_symbols = list(x for x in unused_symbols)
    for symbol in variables:
        if symbol in unused_symbols:
            unused_symbols.remove(symbol)

    # Removes productions with length more than 2 and converts
    # every production to a new one with length 2
    while True:
        more_than_len2 = False
        for rhs_list in rules.values():
            for rhs in rhs_list:
                if len(rhs) > 2:
                    more_than_len2 = True
                    break
            if more_than_len2:
                break
        if more_than_len2:
            convert_to_len2(variables, rules, unused_symbols)
        else:
            break

    # Removes productions that have 2 concatenated terminals
    # or 1 terminal concatenated with a variable
    remove_nonsingle_terminals(rules, variables, terminals, unused_symbols)

    # Removes repeated rules
    while True:
        repeated_rule = ''
        repeated_rules_found = False
        for lhs, rhs_list in rules.items():
            for lhs2, rhs_list2 in rules.items():
                if lhs != lhs2 and rhs_list == rhs_list2:
                    repeated_rules_found = True
                    repeated_rule = lhs2
                    break
            if repeated_rules_found:
                break
        if repeated_rules_found:
            rules.pop(repeated_rule)
            variables.remove(repeated_rule)
        else:
            break

    return rules


def parse(string, rules, variables, start_var):
    # Parses the string using cyk parsing table
    string_len = len(string)
    cyk_table = [[[] for x in range(string_len)] for y in range(string_len)]

    i = 0
    while i < string_len:
        for variable in variables:
            if string[i] in rules[variable]:
                cyk_table[i][i].append(variable)
        i += 1

    l = 1
    while l < string_len:
        i = 0
        while i < string_len - l:
            j = i + l
            k = i
            while k < j:
                for lhs, rhs_list in rules.items():
                    for rhs in rhs_list:
                        if len(rhs) == 2:
                            if rhs[0] in cyk_table[i][k] and rhs[1] in cyk_table[k + 1][j]:
                                if lhs not in cyk_table[i][j]:
                                    cyk_table[i][j].append(lhs)
                k += 1
            i += 1
        l += 1

    if start_var in cyk_table[0][string_len - 1]:
        return True
    return False


def main():
    variables, terminals, start_var, rules = read_grammar('Grammar.txt')
    convert_to_cnf(variables, terminals, start_var, rules)
    print('Enter your strings(type "end" to terminate):')
    while True:
        input_string = input()
        if input_string == 'end':
            break
        else:
            if parse(input_string, rules, variables, start_var):
                print('The input string is accepted.')
            else:
                print('The input string is not accepted.')


if __name__ == '__main__':
    main()
