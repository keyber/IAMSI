import multiprocessing.pool
import plannificateur_beroukhim_buton as plannificateur

const_path = "./contraintes/"

def compute_lowest_duration(ne):
    # le parser est dupliqué pour le multiprocessing,
    # les modifications n'affectent donc pas les autres
    params = plannificateur.parser.parse_args()
    params.verbose = False
    params.ne = ne
    params.contraintes_path=const_path + "contrainte" + str(ne) + ".cnf"
    params.sortie_planning = "planning" + str(ne) + ".csv"
    
    # il faut au moins 1 jour par match d'une équipe
    # une équipe réalise 2 matchs contre chacune des (ne - 1) autres équipes
    nj = (ne - 1) * 2
    while 1:
        params.nj = nj
        
        #démarre unpreocessus et attend tout de suite qu'il finisse
        pool = multiprocessing.pool.ThreadPool(processes=1)
        async_result = pool.apply_async(plannificateur.main, (params,))
    
        try:
            res = async_result.get(timeout=10)
        except multiprocessing.context.TimeoutError:
            return ne, nj, "borne inf (timeOut)"
        if res:
            return ne, nj, "minimal"
        
        nj += 1
    
def main():
    import os
    if not os.path.isdir(const_path):
        os.mkdir(const_path)
    
    equipes = range(3,11)
    pool = multiprocessing.pool.Pool()
    resultat = pool.imap_unordered(compute_lowest_duration, equipes)
    for ne, nj, txt in resultat:
        print(ne, "équipes :", nj, "jours", txt)
    
if __name__ == '__main__':
    main()