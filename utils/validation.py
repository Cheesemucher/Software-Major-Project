import re

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$") 

def sanitise_inputs(*inputs) -> list: # Dunno what type hint to do for args
    sanitised_inputs = []
    
    for input in inputs:
        sanitised_inputs.append(re.escape(input))

    return sanitised_inputs

