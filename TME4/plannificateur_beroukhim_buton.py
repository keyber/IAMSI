import numpy as np
import subprocess
import argparse
import csv


class Planning:
    def __init__(self, ne, nj):
        self.ne = ne
        self.nj = nj
        self.equipes = range(ne)
        self.jours = range(nj)
        self._test_codage_decodage(100)
    
    def get_var_number(self):
        return self.ne ** 2 * self.nj
    
    def codage(self, j, x, y):
        """match jour j, entre x à dom et y ext"""
        return j * self.ne ** 2 + x * self.ne + y + 1
    
    def decodage(self, k):
        """return j, x, y"""
        k = k - 1
        return k // (self.ne ** 2), (k // self.ne) % self.ne, k % self.ne
    
    def _test_codage_decodage(self, nbRepet):
        for _ in range(nbRepet):
            x = np.random.randint(self.ne)
            y = np.random.randint(self.ne)
            j = np.random.randint(self.nj)
            jP, xP, yP = self.decodage(self.codage(j, x, y))
            assert (jP, xP, yP) == (j, x, y)
    
    def contraintes_pas_deux_match(self):
        """C1 au plus un match par jour par équipe
        nb contraintes = ne * nj * (2ne - 2) (2ne - 3) / 2"""
        res = []
        for x in self.equipes:
            for j in self.jours:
                #au plus un match à dom ou ext
                list_match = [self.codage(j, x, y) for y in self.equipes if y != x]
                list_match += [self.codage(j, y, x) for y in self.equipes if y != x]
                res += au_plus_un(list_match)
        return res
    
    def _test_match_jour(self):
        assert len(self.contraintes_pas_deux_match()) == self.ne * self.nj * (self.ne - 1) * (2 * self.ne - 3)
    
    def contraintes_tous_les_match(self):
        """C2 toutes les équipes doivent jouer contre tout le monde,
        une fois à domicile et une fois à l'extérieur"""
        contraintes = []
        for e_dom in self.equipes:
            for e_ext in self.equipes:
                if e_dom != e_ext:
                    list_match = [self.codage(j, e_dom, e_ext) for j in self.jours]
                    contraintes += au_moins_un(list_match)
                    contraintes += au_plus_un(list_match)
        return contraintes
    
    def contraintes_pas_soi_meme(self):
        """C3 qqsoit jour qqsoit équipe, elle ne doit pas jouer contre elle-même"""
        contraintes = []
        for e in self.equipes:
            for j in self.jours:
                k = self.codage(j, e, e)
                contraintes.append("-" + str(k) + " 0")
        return contraintes
    
    def get_contraintes(self):
        contraintes = []
        contraintes += self.contraintes_pas_deux_match()
        contraintes += self.contraintes_tous_les_match()
        contraintes += self.contraintes_pas_soi_meme()
        return contraintes


def au_moins_un(list_var):
    """nb contraintes = 1"""
    return [" ".join(str(x) for x in list_var) + " 0"]


def au_plus_un(list_var):
    """nb contraintes = n * (n - 1) / 2"""
    n = len(list_var)
    res = []
    for i in range(n):
        for j in range(i + 1, n):
            res.append("-" + str(list_var[i]) + " -" + str(list_var[j]) + " 0")
    return res


#assert len(tous_les_match()) == 42


def ecriture_contraintes(path, planning, verbose):
    contraintes = planning.get_contraintes()
    if verbose:
        print("nb var", str(planning.get_var_number()),
              "nb contraintes", len(contraintes))
    
    with open(path, "w") as file:
        file.write("p cnf " + str(planning.get_var_number()) + " " + str(len(contraintes)) + "\n")
        for line in contraintes:
            file.write(line + "\n")


def execute_glucose(executable_path, contraintes_path):
    #éxecute glucose
    result = subprocess.run([executable_path, "-model", contraintes_path], stdout=subprocess.PIPE)
    
    #récupère la sortie
    result = result.stdout.decode("UTF-8")
    
    #cherche une ligne contenant "statisfiable"
    result = result.split("s SATISFIABLE")
    
    #non trouvé
    if len(result) < 2:
        raise ValueError("insatisfiable")
    
    #un modèle satisfaisant est écrit après
    result = result[-1]
    
    #enlève le caractère "v" du début de la ligne
    result = result[3:]
    
    #récupère la liste des variables
    result = result.split()
    
    #transforme les valeurs des variables en int
    return map(int, result)


def write_calendar(planning, variables, equipes, output_path, verbose):
    rencontres_par_jour = [[] for _ in range(planning.nj)]
    for var in variables:
        if var > 0:
            j, x, y = planning.decodage(var)
            rencontres_par_jour[j].append([str(j), equipes[x], equipes[y]])  #equipes[x] + " vs " + equipes[y])
    
    affiche = verbose and sum(len(r) for r in rencontres_par_jour) < 16
    
    with open(output_path, "w") as fichier_sortie:
        writer = csv.writer(fichier_sortie, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["jour", "domicile", "extérieur"])
        for rencontre_du_jour in rencontres_par_jour:
            for r in rencontre_du_jour:
                if affiche:
                    print(r)
                writer.writerow(r)


parser = argparse.ArgumentParser()
parser.add_argument('--ne', type=int, default=3)
parser.add_argument('--nj', type=int, default=6)
parser.add_argument('--equipes_path', type=str, default=None)
parser.add_argument('--contraintes_path', type=str, default="contraintes.cnf")
parser.add_argument('--glucose_path', type=str, default="../glucose-syrup-4.1/simp/glucose_static")
parser.add_argument('--sortie_planning', type=str, default="planning.csv")
parser.add_argument('--verbose', type=bool, default=True)


def main(params):
    if params.verbose:
        print("paramètres:", vars(params))
    
    if params.equipes_path is not None:
        with open(params.equipes_path) as f:
            equipes = list(map(lambda x: x.replace("\n", ""), f.readlines()))
    else:
        equipes = ["e" + str(i+1) for i in range(params.ne)]
    
    planning = Planning(params.ne, params.nj)
    
    ecriture_contraintes(params.contraintes_path, planning, params.verbose)
    
    try:
        variables = execute_glucose(params.glucose_path, params.contraintes_path)
    except ValueError as e:
        if params.verbose:
            print(e)  #non satisfiable
        return 0
    
    write_calendar(planning, variables, equipes, params.sortie_planning, params.verbose)
    
    if params.verbose:
        print("csv généré :", params.sortie_planning)
    
    return 1

if __name__ == '__main__':
    main(parser.parse_args())
