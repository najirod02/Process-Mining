import numpy as np
cimport numpy as np

# Levenshtein distance function using NumPy for efficient array manipulations
def levenshtein(str s1, str s2):
    cdef int len1 = len(s1)
    cdef int len2 = len(s2)
    cdef int i, j
    cdef int cost

    # Create NumPy arrays for dynamic programming table
    cdef np.ndarray[int] dp_prev = np.arange(len2 + 1, dtype=np.int32)
    cdef np.ndarray[int] dp_curr = np.zeros(len2 + 1, dtype=np.int32)

    for i in range(1, len1 + 1):
        dp_curr[0] = i
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp_curr[j] = min(dp_prev[j] + 1,  # Deletion
                             dp_curr[j - 1] + 1,  # Insertion
                             dp_prev[j - 1] + cost)  # Substitution
        # Swap the rows for the next iteration
        dp_prev[:] = dp_curr[:]

    return dp_curr[len2]
