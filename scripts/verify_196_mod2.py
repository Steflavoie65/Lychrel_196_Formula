# verify_196_mod2.py
# Vérifie exhaustivement les vecteurs de carry modulo 2 pour l'addition 196 + rev(196)
# Conventions: représentation canonique sans zéros de tête, digits indexés left-to-right a0..ad-1

def digits(n):
    return list(map(int, str(n)))

def reverse_digits(d):
    return d[::-1]


def check_carries_mod2(a):
    # a: digits left-to-right, a[0] is MSB
    d = len(a)
    # We'll perform addition position-wise from least-significant side.
    # Indexing: i from 0..d-1 where i=0 is MSB in paper, but carries are computed from LSB.
    # For simplicity, use indices from LSB: j=0..d-1 corresponds to a[d-1-j]
    
    # Precompute pair sums without carries
    pair = [a[d-1-j] + a[j] for j in range(d)]  # j=0 LSB pair (a_{d-1} + a_0)

    valid_palindromes = []

    # c_j are carries after computing position j (LSB indexing), c_{-1}=0
    # For modulo 2 check we enumerate c_j in {0,1} for j=0..d-1, and also consider possible overflow c_{d}
    from itertools import product
    for c_bits in product([0,1], repeat=d+1):
        # c_bits[j] is carry c_j for j=0..d (c_d is overflow)
        c = list(c_bits)
        if c[0] != 0:
            # c_0 corresponds to carry after least-significant digit; but our c_{-1}=0 must hold as incoming
            pass
        # Now compute s_j = pair[j] + c_{j-1}
        ok = True
        b = [None]*d
        for j in range(d):
            s = pair[j] + (c[j-1] if j-1 >=0 else 0)
            # c_j should equal floor(s/10) mod 2? Actually c_j is an integer carry (0 or 1) we enumerated
            # Check digit value b_j = s - 10*c_j in Z
            bj = s - 10*c[j]
            if not (0 <= bj <= 9):
                ok = False
                break
            b[j] = bj
        if not ok:
            continue
        # Now b is digits LSB->MSB; build full number digits MSB->LSB
        b_msb_to_lsb = b[::-1]
        # Check palindromic: b_msb_to_lsb == reversed(b_msb_to_lsb)
        if b_msb_to_lsb == b_msb_to_lsb[::-1]:
            # Record carry vector in MSB indexing for readability
            # Convert c (LSB indexing) to c_msbs where c_msbs[i] = c_{i} using original paper indexing is tricky
            valid_palindromes.append((c, b_msb_to_lsb))
    return valid_palindromes

if __name__ == '__main__':
    a = digits(196)
    res = check_carries_mod2(a)
    if not res:
        print('Aucune configuration de carry modulo 2 (avec reps en {0,1}) ne produit un palindrome pour 196 (représentation canonique).')
    else:
        print('Configurations palindromiques trouvées:')
        for c,b in res:
            print('c (LSB->MSB):', c, 'produit digits', b)
