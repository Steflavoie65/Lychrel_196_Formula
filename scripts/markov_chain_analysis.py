#!/usr/bin/env python3
"""
Analyse de la chaîne de Markov des retenues pour l'orbite de 196
"""

def reverse_add_with_carries(n):
    """Applique T(n) = n + reverse(n) et retourne les retenues"""
    digits = list(map(int, str(n)))
    d = len(digits)
    rev_digits = digits[::-1]
    
    result = []
    carries = [0] * (d + 1)  # c[-1] = 0, c[d] = retenue finale
    output_digits = []
    
    # Calcul de l'addition avec retenues
    for i in range(d):
        total = digits[i] + rev_digits[i] + carries[i]
        output_digit = total % 10
        carries[i + 1] = total // 10
        output_digits.append(output_digit)
    
    # Gestion de la retenue finale
    if carries[d] > 0:
        output_digits.append(carries[d])
    
    result_number = int(''.join(map(str, output_digits[::-1])))
    return result_number, carries[:d+1]

def get_carry_state(n, k=3):
    """Extrait l'état des retenues modulo 2^k"""
    _, carries = reverse_add_with_carries(n)
    # Prend les k premières retenues (modulo 2)
    carry_bits = [c % 2 for c in carries[:k]]
    return tuple(carry_bits)

def analyze_markov_chain(start=196, iterations=1000, k=3):
    """Analyse la chaîne de Markov des états de retenues"""
    print(f"Analyse de la chaîne de Markov des retenues (mod 2^{k})")
    print(f"Sur {iterations} itérations")
    print("=" * 50)
    
    current = start
    states_visited = set()
    transitions = {}
    state_sequence = []
    
    # Parcours de l'orbite
    for i in range(iterations):
        current_state = get_carry_state(current, k)
        state_sequence.append(current_state)
        states_visited.add(current_state)
        
        # Calcul de l'état suivant
        current, _ = reverse_add_with_carries(current)
        next_state = get_carry_state(current, k)
        
        # Enregistrement de la transition
        if current_state not in transitions:
            transitions[current_state] = set()
        transitions[current_state].add(next_state)
    
    # Analyse des résultats
    print(f"📊 États visités: {len(states_visited)}")
    print(f"🔗 Transitions uniques: {sum(len(v) for v in transitions.values())}")
    
    # Vérification de l'absorption
    print("\n🔍 Analyse des classes récurrentes:")
    
    # Trouver les états qui se transforment en eux-mêmes
    absorbing_states = []
    for state, next_states in transitions.items():
        if state in next_states:
            absorbing_states.append(state)
    
    if absorbing_states:
        print(f"✅ {len(absorbing_states)} états absorbants trouvés:")
        for state in absorbing_states[:5]:  # Affiche les 5 premiers
            print(f"   État {state} → lui-même")
    else:
        print("❌ Aucun état absorbant pur détecté")
    
    # Vérifier s'il existe une classe fermée
    closed_sets = find_closed_sets(transitions)
    if closed_sets:
        print(f"\n✅ {len(closed_sets)} classe(s) fermée(s) détectée(s):")
        for i, closed_set in enumerate(closed_sets[:3]):  # Affiche les 3 premières
            print(f"   Classe {i+1}: {len(closed_set)} états")
    else:
        print("\n❌ Aucune classe fermée détectée")
    
    # Fréquence des états
    state_freq = {}
    for state in state_sequence:
        state_freq[state] = state_freq.get(state, 0) + 1
    
    print(f"\n📈 État le plus fréquent: {max(state_freq.items(), key=lambda x: x[1])}")
    
    return states_visited, transitions, state_sequence

def find_closed_sets(transitions):
    """Trouve les ensembles fermés dans la chaîne de Markov"""
    all_states = set(transitions.keys())
    closed_sets = []
    
    for state in all_states:
        # Suivre les transitions à partir de cet état
        reachable = set()
        to_explore = {state}
        
        while to_explore:
            current = to_explore.pop()
            reachable.add(current)
            if current in transitions:
                for next_state in transitions[current]:
                    if next_state not in reachable:
                        to_explore.add(next_state)
        
        # Vérifier si c'est fermé
        if reachable.issubset(transitions.keys()):
            is_closed = True
            for s in reachable:
                if not transitions[s].issubset(reachable):
                    is_closed = False
                    break
            
            if is_closed and reachable not in closed_sets:
                closed_sets.append(reachable)
    
    return closed_sets

def check_obstruction_states(transitions):
    """Vérifie si les états obstructifs forment une classe fermée"""
    print("\n" + "=" * 50)
    print("VÉRIFICATION DES ÉTATS OBSTRUCTIFS")
    print("=" * 50)
    
    # Un état est considéré obstructif s'il mène à une obstruction modulo 2
    # Pour simplifier, on considère que tous les états avec retenues non-symétriques sont obstructifs
    obstruction_states = set()
    
    for state in transitions:
        # Vérifier la symétrie des retenues
        if len(state) > 1:
            # Un état est obstructif si les retenues ne sont pas symétriques
            is_symmetric = all(state[i] == state[len(state)-1-i] for i in range(len(state)//2))
            if not is_symmetric:
                obstruction_states.add(state)
    
    print(f"🔍 {len(obstruction_states)} états obstructifs identifiés")
    
    # Vérifier si c'est une classe fermée
    if obstruction_states:
        is_closed = True
        for state in obstruction_states:
            if not transitions[state].issubset(obstruction_states):
                is_closed = False
                print(f"❌ L'état {state} sort de la classe obstructive")
                break
        
        if is_closed:
            print("✅ Les états obstructifs forment une classe fermée!")
        else:
            print("❌ Les états obstructifs ne forment pas une classe fermée")
    
    return obstruction_states

if __name__ == "__main__":
    # Analyse avec différentes tailles d'état
    for k in [2, 3, 4]:
        print(f"\n{'='*60}")
        print(f"ANALYSE AVEC k = {k} (retenues modulo 2^{k})")
        print('='*60)
        
        states, transitions, sequence = analyze_markov_chain(iterations=1000, k=k)
        obstruction_states = check_obstruction_states(transitions)
        
        if obstruction_states and all(transitions[state].issubset(obstruction_states) for state in obstruction_states):
            print("🎉 STRUCTURE MARKOVIENNE VALIDÉE!")
            print("Les états obstructifs forment une classe récurrente absorbante.")