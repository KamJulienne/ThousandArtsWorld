# -*- coding: utf-8 -*-
"""
JSFuck encoder in Python.
Encodes arbitrary strings into JSFuck expressions that eval to the original string.
Based on the standard JSFuck encoding scheme.
"""

# Core primitives
ZERO = '+[]'
ONE = '+!![]'
TWO = '!![]+!![]'
THREE = '!![]+!![]+!![]'
FOUR = '!![]+!![]+!![]+!![]'
FIVE = '!![]+!![]+!![]+!![]+!![]'
SIX = '!![]+!![]+!![]+!![]+!![]+!![]'
SEVEN = '!![]+!![]+!![]+!![]+!![]+!![]+!![]'
EIGHT = '!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]'
NINE = '!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]'
TEN = f'[{ONE}]+[{ZERO}]'

NUMBERS = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]

FALSE = '![]'
TRUE = '!![]'
UNDEFINED = '[][[]]'
NAN = '+[![]]'

# String sources
STR_FALSE = f'({FALSE}+[])'
STR_TRUE = f'({TRUE}+[])'
STR_UNDEFINED = f'({UNDEFINED}+[])'
STR_NAN = f'({NAN}+[])'
STR_OBJECT_OBJECT = '([]+{})'
STR_1E100 = f'(+!![]+({ONE}+{ZERO}+{ZERO}))'  # 1e100 as a number
STR_INFINITY = f'(({ONE}/{ZERO})+[])'  # "Infinity"

# Mapping of characters to their source string and index
# We use multiple sources for efficiency
CHAR_MAP = {}

def _num(n):
    """Convert integer to JSFuck number expression."""
    if n < 10:
        return NUMBERS[n]
    return f'({"+".join(NUMBERS[int(d)] for d in str(n))})'

def _index_access(base, idx):
    """Access character at index in string."""
    if idx < 10:
        return f'({base})[{NUMBERS[idx]}]'
    return f'({base})[{_num(idx)}]'

def _build_char_map():
    """Build mapping from character to shortest JSFuck expression."""
    sources = [
        (STR_FALSE, 'false'),
        (STR_TRUE, 'true'),
        (STR_UNDEFINED, 'undefined'),
        (STR_OBJECT_OBJECT, '[object Object]'),
        (STR_NAN, 'NaN'),
        (STR_1E100, '1e+100'),  # Not reliable, skip
        (STR_INFINITY, 'Infinity'),
    ]
    
    for src_expr, src_str in sources:
        for i, ch in enumerate(src_str):
            expr = _index_access(src_expr, i)
            if ch not in CHAR_MAP or len(expr) < len(CHAR_MAP[ch]):
                CHAR_MAP[ch] = expr
    
    # For digits and other chars not covered, use fromCharCode approach
    # We can also build numbers as strings

def _build_char_map():
    """Build mapping from character to shortest JSFuck expression."""
    CHAR_MAP.clear()
    
    # Sources in order of preference
    sources = [
        (STR_FALSE, 'false'),
        (STR_TRUE, 'true'),
        (STR_UNDEFINED, 'undefined'),
        (STR_OBJECT_OBJECT, '[object Object]'),
        (STR_NAN, 'NaN'),
        (STR_INFINITY, 'Infinity'),
    ]
    
    for src_expr, src_str in sources:
        for i, ch in enumerate(src_str):
            expr = _index_access(src_expr, i)
            if ch not in CHAR_MAP or len(expr) < len(CHAR_MAP[ch]):
                CHAR_MAP[ch] = expr
    
    # Add numeric characters via coercion: (+(n)) + [] gives string "n"
    for n in range(10):
        ch = str(n)
        expr = f'({NUMBERS[n]}+[])'
        if ch not in CHAR_MAP or len(expr) < len(CHAR_MAP[ch]):
            CHAR_MAP[ch] = expr
    
    # For remaining characters, we'll use fromCharCode
    # Build "String" constructor: ([]+[]).constructor → accessed via
    # "constructor" is in "[object Object]"[11:]
    # Actually, we can use []+[] for empty string, then .constructor for String
    
    _EMPTY_STR = '[]+[]'
    
    # String.fromCharCode = ([]+[])["constructor"]["fromCharCode"]
    # "constructor" → from "[object Object]"
    CONSTRUCTOR_STR = 'constructor'
    FROMCHARCODE_STR = 'fromCharCode'
    
    # Build constructor access
    constructor_chars = []
    for ch in CONSTRUCTOR_STR:
        constructor_chars.append(CHAR_MAP.get(ch, f'({CHAR_MAP.get(ch.lower(), STR_UNDEFINED)})'))
    constructor_expr = f'({"+".join(constructor_chars)})'
    
    # Build fromCharCode access
    fc_chars = []
    for ch in FROMCHARCODE_STR:
        fc_chars.append(CHAR_MAP.get(ch, ''))
    fc_expr = f'({"+".join(fc_chars)})'
    
    # String.fromCharCode
    CHAR_MAP['__FROMCHARCODE__'] = f'(({_EMPTY_STR})[{constructor_expr}][{fc_expr}])'
    
    return CHAR_MAP

def _from_char_code(char_code):
    """Generate JSFuck expression for String.fromCharCode(code)."""
    return f'({CHAR_MAP["__FROMCHARCODE__"]}({_num(char_code)}))'

def jsfuck_encode(text):
    """Encode a string into JSFuck expression."""
    _build_char_map()
    
    parts = []
    for ch in text:
        if ch in CHAR_MAP and not ch.startswith('_'):
            parts.append(CHAR_MAP[ch])
        else:
            parts.append(_from_char_code(ord(ch)))
    
    return '+'.join(parts)

def jsfuck_wrap(expression, assign_to=None):
    """Wrap JSFuck expression so it can be eval'd. 
    Returns JS code that when executed produces the value.
    If assign_to is provided, assigns to that variable.
    """
    if assign_to:
        return f'{assign_to}=eval({expression})'
    return f'eval({expression})'

# ---- Optimized alternative: only JSFuck-encode a small key ----
def jsfuck_encode_compact(text):
    """More compact version using Function constructor to reduce size."""
    _build_char_map()
    
    # Strategy: encode each character, but use fromCharCode for non-common chars
    # Build a function body that returns the string
    
    parts = []
    for ch in text:
        if ch in CHAR_MAP and not ch.startswith('_'):
            parts.append(CHAR_MAP[ch])
        else:
            parts.append(_from_char_code(ord(ch)))
    
    return '+'.join(parts)


if __name__ == '__main__':
    # Test with a small string
    test = "hello"
    encoded = jsfuck_encode(test)
    print(f"Encoding '{test}':")
    print(f"Length: {len(encoded)} chars")
    print(f"Ratio: {len(encoded)/len(test):.1f}x")
    print()
    
    test2 = "a1b2c3d4e5f6a7b8"  # 16-char hex key
    encoded2 = jsfuck_encode(test2)
    print(f"Encoding '{test2}':")
    print(f"Length: {len(encoded2)} chars")
    print(f"Ratio: {len(encoded2)/len(test2):.1f}x")
