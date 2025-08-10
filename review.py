def bayesian_score(m, C, n, R):
    if R is None:
        return None
    return ((m * C) + (n * R)) / (m + n)
