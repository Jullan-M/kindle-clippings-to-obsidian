import re


def getvalidfilename(filename):
    import unicodedata

    clean = unicodedata.normalize("NFKD", filename)
    clean = re.sub(r"[()'?!:]", "", clean)
    return clean


def longest_common_substring_len(a: str, b: str) -> int:
    """
    DP O(len(a)*len(b)) time, O(min(len(a),len(b))) memory.
    Returns length of the longest contiguous substring shared by a and b.
    """
    if not a or not b:
        return 0

    # Ensure b is the shorter
    if len(b) > len(a):
        a, b = b, a

    prev = [0] * (len(b) + 1)
    best = 0

    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur

    return best
