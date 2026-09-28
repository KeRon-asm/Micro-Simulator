#SPLIT TURNS STRINGS -> LISTS
#JOIN TURNS LISTS -> STRINGS
def get_num_variables():
    while True:
        try:
            number_of_variables = int(input("How many input variables? Must be >=2\n"))
            if number_of_variables < 2:
                print("Error: n must be 2 or greater.")
            else:
                return number_of_variables
        except ValueError:
            print("Error, n must be a positive integer larger than 1.")
def get_truth_table(n):
    rows = 2**n
    #Product of sums when there's more 1's than 0's for output, generally
    print(f"\nEnter the truth table, it should be ({rows} rows.)")
    print(f"Format each row as inputs followed by output, like this:")
    print(f"0 0 1 (inputs: 0,0 -> outputs: 1)\n")
    
    table = []
    for i in range(rows):
        while True:
            raw = input(f"Row {i}: ").strip().split()
            if len(raw) == n+1:
                table.append(raw)
                break
            else:
                print(f"Error: Expected {n} inputs + 1 output = {n+1} values.")
                
    return table
def validate_truth_table(table, n):
    rows = 2**n
    seen_inputs = set()
    #record the table in a set so as to prevent duplicate rows
    
    #This logic is how the table can be edited
    for i, row, in enumerate(table):
        inputs = row[:n]
        output = row[n]
        
    #check to ensure each row is entirely in binary
        for val in row:
            if val not in ("0", "1"):
                print(f"Error: Row {i} contains invalid value '{val}', must be 0 or 1.")
                return False
    #check each input combination appears only once
        input_key = tuple(inputs)
        if input_key in seen_inputs:
            print(f"Error: Row {i} is a duplicate input combination {inputs}.")
            return False
        seen_inputs.add(input_key)

    #check if table is full and complete
    expected = set()
    for i in range(rows):
        combo = tuple(format(i, f'0{n}b')) # this will convert i to a binary string, and then a tuple
        expected.add(combo)
        
    if seen_inputs != expected:
        missing = expected - seen_inputs
        print(f"What was expected:{expected}\nWhat was received: {seen_inputs}")
        print(f"Error: Missing input combinations: {[list(m) for m in missing]}") #list comprehension
        return False
    
    #if all this goes well, the Truth table should be valid
    
    print("\nTruth table is valid.")
    return True    
'''
n = get_num_variables()
table = get_truth_table(n)

print("\nTruth table received:")
for row in table:
    print(" ".join(row))
is_valid = validate_truth_table(table,n)
print(f"\nTruth table is {is_valid}.")
'''

def get_form():
    #User should be able to select SOP or POS
    while True:
        form = input("\nSelect form: SOP or POS: ").upper().strip()
        if form in ("SOP", "POS"):
            return form
        print(f"Error: Please enter SOP or POS")
def get_variable_names(n):
    #Convert truth tables to variable names
    return [chr(65 + i) for i in range(n)] #list comprehension
def build_for_sop(table, n):
    '''
    SOP builds from the 1's in output, the minterms. The output will look like ABC+A'BC+ABC'
    etc etc.
    So any row that has an output of 0 should be ignored, and any row that has an input of 0
    needs to be flipped to the complement. This should mean:
    -Don't use rows with an output of 0
    -If an input is 0, generate the letter + " ' ", for the complement
    '''
    variables = get_variable_names(n)
    minterms = []
    equation_terms = []
    
    for row in table:
        inputs = row[:n]
        output = row[n]
        if output == "1":
            # Minterm index
            index = int("".join(inputs),2) #The 2 argument here allows conversion of binary numbers to decimal
            minterms.append(index)
            
            #build product
            term_parts = []
            for i, bit in enumerate(inputs):
                if bit == "0":
                    term_parts.append(variables[i] + "'") #This creates the complement
                else:
                    term_parts.append(variables[i])
            equation_terms.append("".join(term_parts))
            
    equation =  " + ".join(equation_terms) if equation_terms else "0" #Truthiness
    return equation, minterms
def build_for_pos(table, n):
    """
    POS is similar, but builds from 0's in the output, the maxterms.
    Any row with an output of 1 should be ignored, and any input that is 1, should be complemented.
    -Use only the rows with 1
    -If an input is 1, generate the letter + "'" for the complement
    """
    
    variables = get_variable_names(n)
    maxterms = []
    equation_terms = []
    
    for row in table:
        inputs = row[:n] #
        output = row[n]
        
        if output == "0":
            index = int("".join(inputs),2)
            maxterms.append(index)
            
            term_parts = []
            for i, bit in enumerate(inputs):
                if bit == "1":
                    term_parts.append(variables[i] + "'") #complement
                else:
                    term_parts.append(variables[i])
            equation_terms.append("(" + " + ".join(term_parts)+ ")")
    equation = " * ".join(equation_terms) if equation_terms else "1"
    return equation, maxterms
def get_gray_code(n):
    '''
    gray code works by flipping one bit at a time 
    so 00 -> 01 -> 11 -> 10
    this could be built recursively, but that's difficult, so I may try the mathematical formula
    G(n) = n XOR (n>>1)
    much simpler
    might be even easier to hard code it
    if n == 2:
    return ["00", "01", "11", "10"]
    n == 3:
    return ["000","001,"011", "010","110","111","101","100"]
    n==4 
    return ["0000","0001", "0011",""]
    this is undesirable, but maybe not so bad for building the kmap
    '''
    gray_code = []
    for i in range(2**n):
        gray = i ^ (i>>1)
        gray_code.append(format(gray, f'0{n}b'))
    return gray_code

def build_kmap(table,n):
    '''
    If the truth table is a dictionary, with the inputs as a key, and the output as a value
    It would be easy to look up the rows. Might be easier to hard code this part, though
    '''
    if n == 2:
        row_vars = ["0", "1"]
        col_vars = ["0", "1"]
    elif n == 3:
        row_vars = ["0", "1"]
        col_vars = ["00","01", "11", "10"]
    elif n == 4:
        row_vars = ["00","01", "11", "10"]
        col_vars = ["00","01", "11", "10"]
    #Build a grid as a matrix!
    truth_dict = {}
    for row in table:
        key = tuple(row[:n])
        truth_dict[key] = row[n]
    grid = []
    for r in row_vars:
        row_out = []
        for c in col_vars:
            key = tuple(r+c)
            row_out.append(truth_dict[key])
        grid.append(row_out)
        
    return grid, row_vars, col_vars
def display_kmap(grid, row_vars, col_vars, n):
    #ASCII art is a nuisance.
    variables = get_variable_names(n)
    
    if n == 2:
        row_label = variables[0]
        col_label = variables[1]
    elif n == 3:
        row_label = variables[0]
        col_label = variables[1] + variables[2]
    elif n == 4:
        row_label = variables[0] + variables[1]
        col_label = variables[2] + variables[3]
        
    # Header
    print(f"\nK-Map ({row_label}{col_label}):")
    header = f"{'':>6}"
    for c in col_vars:
        header += f"{col_label} = {c}".center(12)
    print(header)
    
    # Print rows
    for i, r in enumerate(row_vars):
        row_str = f"{row_label} = {r}".ljust(6) #Certified ASCII art function
        for val in grid[i]:
            row_str += f"{val}".center(12) # ^^^
        print(row_str)
    
    
#grouping algorithm
"""
Rules for valid kmap groups:
1. Must contain cells in the span of power of 2
2. Must be rectangular
3. Groups can wrap around edges (top->bottom, left->)
4. Always find the largest groups
5. Every target cell must be covered at least once
"""    
#Find all target cells
def get_target_cells(grid, form):
    if form == "SOP":
        target = "1"
    else:
        target = "0"
    cells = []
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == target:
                cells.append((r,c))
    return cells

def find_all_groups(grid,cells, n):
    num_rows = len(grid)
    num_cols = len(grid[0])
    target_set = set(cells)
    valid_groups = []
    sizes = [1,2,4,8]
    
    valid_heights = [h for h in sizes if h <= num_rows]
    valid_widths = [w for w in sizes if w <= num_cols]
    
    for height in valid_heights:
        for width in valid_widths:
            for r in range(num_rows):
                 for c in range(num_cols):
                     group = []
                     for dr in range(height):
                         for dc in range(width):
                             row = (r + dr) % num_rows #Logic for wraparound
                             col = (c + dc) % num_cols #more logic for more wrapping around
                             group.append((row, col))
                             
                     group_set = set(group)
                    # only keep if all cells are target cells
                    
                    # logic to avoid duplication
                     if group_set.issubset(target_set):
                        if group_set not in [set(g) for g in valid_groups]:
                            valid_groups.append(group)
    return valid_groups
                    

def select_minimum_groups(valid_groups, cells):
    uncovered = set(cells) #cells unchecked
    selected_groups = []
    
    #sort them by size, taking the largest first, because bigger groups need more simplification
    sorted_groups = sorted(valid_groups, key=len, reverse=True)
    
    for group in sorted_groups:
        group_set = set(group)
        
        if group_set & uncovered:
            selected_groups.append(group)
            uncovered -= group_set
            
        if not uncovered:
            break
    return selected_groups
def derive_simplified_expression(selected_groups, row_vars, col_vars, variables, form):
    terms = []
    
    for group in selected_groups:
        # need full input combination for each cell in group
        input_combos = []
        for (r,c) in group:
            combo = row_vars[r] + col_vars[c] #combine row and col bits into full input
            input_combos.append(combo)

        n = len(input_combos[0])
        term_parts = []
        
        for i in range(n):
            bits = set(combo[i] for combo in input_combos) #collect all values for variable i
            
            if len(bits) == 1:
                bit = bits.pop()
                if form == "SOP":
                    if bit == "1":
                        term_parts.append(variables[i]) #uncomplemented
                    else:
                        term_parts.append(variables[i] + "'")
                else:
                    if bit == "0":
                        term_parts.append(variables[i]) #uncomplemented
                    else:
                        term_parts.append(variables[i] + "'")
                #if len(bits) == 2, the variable changes, so it's eliminated
        if form == "SOP":
            if term_parts:
                terms.append("".join(term_parts))
            else:
                terms.append("1")
        else:
            if term_parts:
                terms.append("(" + " + ".join(term_parts)+ ")") #sum term (A + B')
            else:
                terms.append("0")
             
    if form == "SOP":
        return " + ".join(terms) if terms else "0"
    else:
        return " * ".join(terms) if terms else "1"
    
def validate_simplified(simplified_expr, table, n, form):
    variables = get_variable_names(n)
    all_match = True
    
    for row in table:
        inputs = row[:n]
        expected = int(row[n])
        
        expr = simplified_expr
        
        #substitute actual values for variables
        for i, var in enumerate(variables):
            val = int(inputs[i])
            complement = 1-val
            expr = expr.replace(var + "'", str(complement))
            expr = expr.replace(var, str(val))
        # handle implicit AND between literals in SOP terms
        if form == "SOP":
            sop_terms = expr.split(" + ")
            new_terms = []
            for term in sop_terms:
                new_terms.append(" and ".join(list(term)))
            expr = " or ".join(new_terms)
            
        # convert POS operatorsfor for eval
        if form == "POS":
            expr = expr.replace(" + ", " or ")
            expr = expr.replace(" * ", " and ")
            expr = expr.replace(")(", ") and (")

        #eval

        result = int(bool(eval(expr)))
        
        if result != expected:
            print(f"Mismatch at inputs {inputs}: got {result}, expected {expected}")
            all_match = False
            
    if all_match:
        print(f"\nValidation passed!")
    else:
        print(f"\nValidation failed!")
    return all_match            
            
    
n = get_num_variables()
table = get_truth_table(n)
if validate_truth_table(table, n):
    form = get_form()
    if form == "SOP":
        equation, terms = build_for_sop(table, n)
        print(f"\nCanonical SOP: F = {equation}")
        print(f"Minterms: m{terms}")
    else:
        equation, terms = build_for_pos(table, n)
        print(f"\nCanonical POS: F = {equation}")
        print(f"Maxterms: M{terms}")
    grid, row_vars, col_vars = build_kmap(table, n)
    display_kmap(grid, row_vars, col_vars, n)
    cells = get_target_cells(grid, form)
    valid_groups = find_all_groups(grid, cells, n)
    selected_groups = select_minimum_groups(valid_groups, cells)
    variables = get_variable_names(n)
    simplified = derive_simplified_expression(selected_groups, row_vars, col_vars, variables, form)
    print(f"\nSimplified Expression: F = {simplified}")
    validate_simplified(simplified, table, n, form)
