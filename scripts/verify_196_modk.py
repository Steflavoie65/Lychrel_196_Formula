# verify_196_modk.py
# Vérifie exhaustivement l'existence de vecteurs de carry c_i dans {0,..,2^k-1}
# satisfaisant les contraintes palindromiques et 0<=b_i<=9 pour 196 (représentation canonique)

from itertools import product

def digits(n):
    return list(map(int, str(n)))

def exists_carries_for_k(a, k):
    # a: digits MSB->LSB
    d = len(a)
    maxc = 2**k
    # We'll consider carries c_0..c_d (where c_d is possible overflow)
    # We enumerate c_0..c_d in range(maxc)
    # To reduce space, we can note c_0 is in [0,maxc-1], but typical carries are small; still we brute-force.
    count = 0
    # limit total enumerations to avoid excessive time
    limit = 5_000_000
    rng = range(maxc)
    for cvec in product(rng, repeat=d+1):
        count += 1
        if count > limit:
            return None, 'limit'
        # interpret cvec as c_0..c_d with LSB indexing? We'll stick to paper indexing: c_i is carry-out from position i where i indexes positions from least-significant side.
        # But a is MSB->LSB; pair at LSB index j is a[d-1-j] + a[j]
        ok = True
        b = [None]*d
        for j in range(d):
            c_prev = cvec[j-1] if j-1 >= 0 else 0
            s = a[d-1-j] + a[j] + c_prev
            cj = cvec[j]
            bj = s - 10*cj
            if not (0 <= bj <= 9):
                ok = False
                break
            b[j] = bj
        if not ok:
            continue
        # require c_d == cvec[d]
        # check palindromic constraint on resulting digits b (LSB->MSB stored in b list)
        b_msb = b[::-1]
        if b_msb == b_msb[::-1]:
            return cvec, 'found'
    return None, 'none'

if __name__ == '__main__':
    a = digits(196)
    results = {}
    for k in range(1,6):
        print(f'Checking k={k} (carries in 0..{2**k-1}) ...')
        cvec, status = exists_carries_for_k(a,k)
        results[k] = (status, cvec)
        print('  ->', status)
        if status == 'found':
            print('     example cvec (c_0..c_d):', cvec)
            break
    print('\nSummary:')
    for k,(status,cvec) in results.items():
        print(f'k={k}: {status}', 'example='+str(cvec) if cvec else '')
