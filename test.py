from cython_levenshtein import levenshtein

# Test Levenshtein function
s1 = "kitten"
s2 = "sitting"
distance = levenshtein(s1, s2)
print(f"Levenshtein distance: {distance}")
