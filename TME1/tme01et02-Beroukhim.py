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
    n = position['dimension']
    if coup < 1 or coup > n:
        return False
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


def est_terminale(position):
    n = position['dimension']
    seuil = 4 * n + 1
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

    if computeEndOfGame and est_terminale(nouvelle_pos):
        #fin et score J1 < seuil => pas de coup possible pour J2 => J1 ramasse tout
        if nouvelle_pos['butin'][trait] < nouvelle_pos['dimension'] * 4 + 1:
            nouvelle_pos['butin'][trait] += _pierres_restantes(position)

            nouvelle_pos['fin'] = max('SUD', 'NORD', key=lambda x: nouvelle_pos['butin'][x])

    return nouvelle_pos


def effectue_si_valide(position, coup, computeEndOfGame=True):
    if not _est_correct(position, coup):
        return False
    res = _joue_un_coup(position, coup, computeEndOfGame)
    if _est_legale(res):
        return res
    return False


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


def gen_coups(position):
    n = position['dimension']
    return ((c, p) for (c, p) in
            ((i, effectue_si_valide(position, i)) for i in range(1, n + 1))
            if p)


def genere_un_coup(position):
    import random
    coups = [x[0] for x in gen_coups(position)]
    if coups:
        return random.choice(coups)
    #pas de coup possible
    return 0


def partie_aleatoire(taille, campCPU):
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
            coup = genere_un_coup(position)
            assert coup
            print("IA joue", coup)
            position = effectue_si_valide(position, coup)
        
        affichage(position)
        tourJoueur = not tourJoueur
    
    print("SCORE", position['butin'])


def num_12(position, joueur):
    return len(list(x for x in _plateau(position, joueur) if 0 < x < 3))


def evalue(position):
    if position['fin']:
        return 99 if position['fin'] == 'SUD' else -99
    return (2 * position['butin']['SUD'] + num_12(position, 'SUD')
            - 2 * position['butin']['NORD'] - num_12(position, 'NORD'))


def minmax(position, depth):
    """depth en demi coups
    return (coup, val)"""
    if depth == 0 or est_terminale(position):
        return -1, evalue(position)
    possib = (minmax(c[1], depth - 1) for c in gen_coups(position))
    
    if position['trait'] == 'SUD':
        c, v = max(possib, key=lambda x: x[1])
    else:
        c, v = min(possib, key=lambda x: x[1])
    
    return c, v

for d in range(7):
    print(d, minmax(position_initiale(6), d))

