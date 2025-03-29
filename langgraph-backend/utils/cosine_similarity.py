# cosine_similarity.py
def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude_a = sum(a * a for a in vec1) ** 0.5
    magnitude_b = sum(b * b for b in vec2) ** 0.5
    return dot_product / (magnitude_a * magnitude_b) if magnitude_a and magnitude_b else 0
