def position_initiale(n):
    """ int -> POSITION
        Hypothèse : n > 0
        définit la position de départ pour n colonnes avec 4 graines dans chaque case.
    """
    position = dict()  # initialisation
    position['plateau'] = [4] * 2 * n  # on met 4 graines dans chaque case
    position['dimension'] = n  # le nombre de colonnes du plateau
    position['trait'] = 'SUD'  # le joueur qui doit jouer: 'SUD' ou 'NORD'
    position['butin'] = {'SUD': 0, 'NORD': 0}  # graines prises par chaque joueur
    position['fin'] = False  #ou SUD ou NORD
    return position


def affichage(position):
    """ POSITION ->
        affiche la position de façon textuelle
    """
    print('* * * * * * * * * * * * * * * * * * * *')
    n = position['dimension']
    buffer = 'col:'
    for i in range(n):
        buffer += ' ' + str(i + 1).rjust(2) + ' \t'
    print(buffer)
    print('\t\tNORD (prises: ' + str(position['butin']['NORD']) + ')')
    print('< - - - - - - - - - - - - - - -')
    buffer = ''
    for i in range(2 * n - 1, n - 1, -1):  # indices n..(2n-1) pour les cases NORD
        buffer += '\t[' + str(position['plateau'][i]).rjust(2) + ']'
    print(buffer)
    buffer = ''
    for i in range(0, n):  # indices 0..(n-1) pour les cases SUD
        buffer += '\t[' + str(position['plateau'][i]).rjust(2) + ']'
    print(buffer)
    print('- - - - - - - - - - - - - - - >')
    print('\t\tSUD (prises: ' + str(position['butin']['SUD']) + ')')
    print('-> camp au trait: ' + position['trait'])


def _duplique(position):
    """ POSITION -> POSITION
        retourne une copie dupliquée de la position
        (qui peut être alors modifiée sans altérer l'originale).
    """
    import copy
    leclone = dict()
    leclone['plateau'] = copy.deepcopy(position['plateau'])
    leclone['dimension'] = position['dimension']
    leclone['trait'] = position['trait']
    leclone['butin'] = copy.deepcopy(position['butin'])
    leclone['fin'] = position['fin']
    return leclone


def _est_correct(position, coup):
    """il y a des pierres"""
    n = position['dimension']
    assert 1 <= coup <= n
    
    if position['trait'] == 'SUD':
        ind = coup - 1
    else:
        ind = 2 * n - coup
    return position['plateau'][ind] > 0


def _est_affame(position, joueur):
    return not any(_plateau(position, joueur))


def _est_legale(position):
    return not _est_affame(position, position['trait'])


def _plateau(position, joueur):
    n = position['dimension']
    shift = n if joueur == 'NORD' else 0
    return position['plateau'][shift: shift + n]


def _pierres_restantes(position):
    return sum(position['plateau'])


def _est_terminale(position):
    """Seuil score atteint ou pas de coup possible"""
    n = position['dimension']
    seuil = 4 * (n-1) + 1 #il peut y avoir des bouclages sinon
    if position['butin']['SUD'] >= seuil or position['butin']['NORD'] >= seuil:
        return True
    return not any(effectue_si_valide(position, i, computeEndOfGame=False) for i in range(1, n + 1))


def _joue_un_coup(position, coup, computeEndOfGame):
    """ POSITION * COUP -> POSITION
        Hypothèse: coup est correct.

        Cette fonction retourne la position obtenue une fois le coup joué.
    """
    nouvelle_pos = _duplique(position)  # on duplique pour ne pas modifier l'original
    n = nouvelle_pos['dimension']
    trait = nouvelle_pos['trait']
    # on transforme coup en indice
    if trait == 'SUD':
        indice_depart = coup - 1
    else:
        indice_depart = 2 * n - coup
    # retrait des graines de la case de départ
    nbGraines = nouvelle_pos['plateau'][indice_depart]
    nouvelle_pos['plateau'][indice_depart] = 0
    # on sème les graines dans les cases à partir de celle de départ
    indice_courant = indice_depart
    while nbGraines > 0:
        indice_courant = (indice_courant + 1) % (2 * n)
        if (indice_courant != indice_depart):  # si ce n'est pas la case de départ
            nouvelle_pos['plateau'][indice_courant] += 1  # on sème une graine
            nbGraines -= 1
    # la case d'arrivée est dans le camp ennemi ?
    if (trait == 'NORD'):
        estChezEnnemi = (indice_courant < n)
    else:
        estChezEnnemi = (indice_courant >= n)
    # réalisation des prises éventuelles
    while estChezEnnemi and (nouvelle_pos['plateau'][indice_courant] in range(2, 4)):
        nouvelle_pos['butin'][trait] += nouvelle_pos['plateau'][indice_courant]
        nouvelle_pos['plateau'][indice_courant] = 0
        indice_courant = (indice_courant - 1) % (2 * n)
        if (trait == 'NORD'):
            estChezEnnemi = (indice_courant < n)
        else:
            estChezEnnemi = (indice_courant >= n)
    # mise à jour du camp au trait
    if trait == 'SUD':
        nouvelle_pos['trait'] = 'NORD'
    else:
        nouvelle_pos['trait'] = 'SUD'
    
    if computeEndOfGame and _est_terminale(nouvelle_pos):
        #fin et score J1 < seuil => pas de coup possible pour J2 => J1 ramasse tout
        if nouvelle_pos['butin'][trait] < (nouvelle_pos['dimension']-1) * 4 + 1:
            nouvelle_pos['butin'][trait] += _pierres_restantes(nouvelle_pos)
            
        nouvelle_pos['fin'] = max('SUD', 'NORD', key=lambda x: nouvelle_pos['butin'][x])
    
    return nouvelle_pos


def effectue_si_valide(position, coup, computeEndOfGame=True):
    """return False ou position obtenue"""
    if not _est_correct(position, coup):
        return False
    res = _joue_un_coup(position, coup, computeEndOfGame)
    if _est_legale(res):
        return res
    return False


def gen_coups(position):
    """retourne la liste des (coup, position_atteinte) jouables à ce tour pour le joueur au trait
    choisir un bol avec un nombre de pierres non nul
    pas le droit de tout manger ou de laisser vide le côté adverse
    on peut s'affamer nous même
    """
    n = position['dimension']
    return ((c, p) for (c,p) in ((i, effectue_si_valide(position, i)) for i in range(1, n + 1)) if p)


def _test_gen_coups():
    p = position_initiale(6)
    p['plateau'] = [1,0,1,0,0,0,0,0,0,0,0,1]
    p['trait']='NORD'
    p['butin']['NORD']=24
    print(_plateau(p, 'NORD'))
    print(_plateau(p, 'SUD'))
    
    print(p['plateau'])
    for i in gen_coups(p):
        print(i)

#_test_gen_coups()
#assert 0

def partie_humains():
    position = position_initiale(int(input("taille plateau ")))
    affichage(position)
    while not position['fin']:
        p2 = False
        while not p2:
            coup = input("coup joueur " + position['trait'])
            p2 = coup.isdigit() and effectue_si_valide(position, int(coup))
            if not p2:
                print("coup non valide")
        position = p2
        affichage(position)
    
    print("SCORE", position['butin'])


def partie_cpu(taille, AI, campCPU):
    """IA: random, minmax ou alphabeta
    depth utilisé pour minmax et alphabeta uniquement"""
    position = position_initiale(taille)
    affichage(position)
    tourJoueur = campCPU == "NORD"
    while not position['fin']:
        if tourJoueur:
            p2 = False
            while not p2:
                coup = input("coup joueur ")
                p2 = coup.isdigit() and effectue_si_valide(position, int(coup))
                if not p2:
                    print("coup non valide")
            position = p2
        else:
            coup = AI(position)[0]
            assert coup
            print("IA joue", coup)
            position = effectue_si_valide(position, coup)
        
        affichage(position)
        tourJoueur = not tourJoueur
    
    print("SCORE", position['butin'])


def partie_cpu_cpu(taille, AISUD, AINORD):
    """IA: random, minmax ou alphabeta, avec une depth fixée
    n'affiche rien
    retourne 1 si SUD gagne"""
    position = position_initiale(taille)
    while not position['fin']:
        ai = AISUD if position['trait']=='SUD' else AINORD
        coup = ai(position)[0]
        position = effectue_si_valide(position, coup)
    return 1 if position['fin']=='SUD' else 0


def num_12(position, joueur):
    """nombre de bols à 1 ou 2 pierres"""
    return len(list(x for x in _plateau(position, joueur) if 0 < x < 3))


def evalue(position):
    """retourne l'évaluation pour le camp SUD"""
    if position['fin']:
        return 99 if position['fin'] == 'SUD' else -99
    return (2 * position['butin']['SUD'] + num_12(position, 'SUD')
            - 2 * position['butin']['NORD'] - num_12(position, 'NORD'))


def ai_random(position):
    """renvoie un coup possible aléatoire"""
    import random
    coups = [x[0] for x in gen_coups(position)]
    if coups:
        return random.choice(coups), -1, {}
    
    raise RuntimeError("pas de coups possible")

"""
def _test_ai_rand(position):
    if not position['fin']:
        return _test_ai_rand(_joue_un_coup(position, ai_random(position)[0], True))
    return position
    
for i in range(10000):
    _test_ai_rand(position_initiale(i%5+2))
"""

def ai_minmax(position, depth):
    """depth en demi coups
    return (coup, val)"""
    leaf = 0
    
    def _rec(position, depth):
        nonlocal leaf
        if depth == 0 or position['fin']:
            leaf += 1
            return -1, evalue(position)
        
        #liste de (coups, éval)
        possib = ((c[0], _rec(c[1], depth - 1)[1]) for c in gen_coups(position))
        
        if position['trait'] == 'SUD':
            c, v = max(possib, key=lambda x: x[1])
        else:
            c, v = min(possib, key=lambda x: x[1])
        
        return c, v
    
    res_c, res_v = _rec(position, depth)
    
    return res_c, res_v, {'feuilles': leaf}


def ai_alphabeta(position, depth):
    """depth en demi coups"""
    leaf = 0
    cutoff_a = 0
    cutoff_b = 0
    
    def _rec(position, depth, alpha, beta):
        nonlocal leaf, cutoff_a, cutoff_b
        if depth == 0 or position['fin']:
            leaf += 1
            return -1, evalue(position)
        
        c_chosen = -1
        for c, p in gen_coups(position):
            v = _rec(p, depth - 1, alpha, beta)[1]
            
            if position['trait'] == 'SUD':
                if v > alpha:
                    alpha = v
                    c_chosen = c
                    if alpha >= beta:
                        cutoff_b += 1
                        return -1, alpha  #beta cut-off
            else:
                if v < beta:
                    beta = v
                    c_chosen = c
                    if alpha >= beta:
                        cutoff_a += 1
                        return -1, beta  #alpha cut-off
        
        return c_chosen, alpha if position['trait'] == 'SUD' else beta
    
    res_c, res_v = _rec(position, depth, float("-inf"), float("+inf"))
    return res_c, res_v, {'feuilles': leaf, 'alpha cut-off': cutoff_a, 'beta cut-off': cutoff_b}


def get_fixed_depth_ai(ai, depth):
    """depth en demi-coups"""
    return lambda x: ai(x, depth)


dMax = 6
print("alphabeta à partir de la position initiale pour une profondeur",dMax+1, ":")
print(ai_alphabeta(position_initiale(6), dMax+1)[2], "\n")

print("tableau des victoires en fonction de la profondeur des alphabeta s'affrontant")
print(end="S\\N " )
for d2 in range(1,dMax):
    print(d2, end=" - ")
print()
for d1 in range(1,dMax):
    print(d1, end=":  ")
    ia1 = get_fixed_depth_ai(ai_alphabeta, d1)
    for d2 in range(1,dMax):
        ia2 = get_fixed_depth_ai(ai_alphabeta, d2)
        print(partie_cpu_cpu(6, ia1, ia2), end=" | ")
    print()


n=100
print("\nratios victoire alphabeta vs random")
for d in range(1,4):
    print("depth", d, sum(partie_cpu_cpu(6, get_fixed_depth_ai(ai_alphabeta, d), ai_random)
                          for _ in range(n)), "%")
