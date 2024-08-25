def generate_rm_commands(items, index=0, current_string=""):
    # Base case: if index is out of range, return the current string
    if index >= len(items):
        return current_string
    
    # Append the rm command for the current item to the string
    current_string += f"rm {items[index]} -rf \n"
    
    # Recursive case: process the next item
    return generate_rm_commands(items, index + 1, current_string)


def generate_rm_commands_ii(item):
    
    return f"rm {item} -rf \n "