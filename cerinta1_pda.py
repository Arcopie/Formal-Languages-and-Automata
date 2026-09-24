

from collections import deque

LAMBDA = "lambda"


def citeste_pda(linii):
    idx = 0
    stari = set(linii[idx].split())
    idx += 1
    alfabet = set(linii[idx].split())
    idx += 1
    nr_tranzitii = int(linii[idx])
    idx += 1

    # tranzitii[(stare, simbol_citit, simbol_varf)] = [(stare_urm, sir_push), ...]
    # Pentru aceeasi cheie pot exista mai multe iesiri => nedeterminism.
    tranzitii = {} #tranzitiile si comportamentul automatului
    for _ in range(nr_tranzitii):
        stare, simbol, varf, urm, push = linii[idx].split()
        idx += 1
        #  stare curenta,simbolul citit, simboul din varful stivei
        cheie = (stare, simbol, varf)

        #caut cheia in dictionar si daca nu o gasesc o adaug
        #+stare_destinatie,elementele de pus pe stiva
        #                       starea urmatoare(q1) ,   sirul de inlocuit de pe stiva("ZA")
        tranzitii.setdefault(cheie, []).append((urm, push))

    stare_initiala = linii[idx]
    idx += 1
    simbol_init = linii[idx]
    idx += 1
    stari_finale = set(linii[idx].split())
    idx += 1
    mod = linii[idx]
    idx += 1
    cuvant = linii[idx]
    if cuvant == LAMBDA:
        cuvant = ""

    return tranzitii, stare_initiala, simbol_init, stari_finale, mod, cuvant



#push pe stiva
def aplica_push(stiva, push):
    rest = stiva[1:] # pop varful actual
    if push == LAMBDA: # nu adaugam nimic
        return rest
    return tuple(reversed(push)) + rest


#verific pda ul accepta cuvantul printr-un mod
def este_acceptata(stare, idx, stiva, cuvant, stari_finale, mod):
    tot_consumat = (idx == len(cuvant)) #am citit tot cuvantul
    if mod == "stare_finala":
        return tot_consumat and stare in stari_finale
    if mod == "stiva_goala":
        return tot_consumat and len(stiva) == 0
    if mod == "ambele":
        return tot_consumat and stare in stari_finale and len(stiva) == 0
    return False


#prin bfs explorez toate drumurile pe care le poate parcurge automatul
#si incerc sa gasesc un drum valid
def simuleaza(tranzitii, stare_init, simbol_init, cuvant, stari_finale, mod):
    #pun in coada configuratie initiala
    #(q0, 0, (Z,))
    coada = deque([(stare_init, 0, (simbol_init,))])
    vizitate = set()#configuratiile marcate ca sa nu le reiau de2 ori

    while coada:#cat timp coada nu e vida sau nu am citit tot cuvantul
        stare, idx, stiva = coada.popleft()#configuratia din varful cozii
        #stiva = tuplu cu valorile adaugate ex: (A,A,Z)

        # sar peste configuratiile deja vizitate
        if (stare, idx, stiva) in vizitate:
            continue
        #altfel o marchez
        vizitate.add((stare, idx, stiva))

        if este_acceptata(stare, idx, stiva, cuvant, stari_finale, mod):
            return True
        if len(stiva) == 0:
            #ramura nu este buna, trec la urmatoarea configuratie din coada
            continue
        varf = stiva[0]

        #lista in care retinem toate drumurile pe care le poate lua de unde suntem curent
        aplicabile = []
        #adaug tranzitiile posibile
        if idx < len(cuvant):
            #extrag starea urmatoare si ce trebuie pus inapoi pe stiva
            for urm, push in tranzitii.get((stare, cuvant[idx], varf), []):
                #adaug miscarea in lista aplicabile, indexul creste(folosesc litera)
                aplicabile.append((urm, idx + 1, push))
        #adaug si tranzitiile lambda in lista( indexul ramane neschimbat, nu folosesc litere)
        for urm, push in tranzitii.get((stare, LAMBDA, varf), []):  # tranzitii lambda
            aplicabile.append((urm, idx, push))

        #pentru fiecare tranzitie aplicabila calculez noua stiva
        for urm, idx_nou, push in aplicabile:
            noua = aplica_push(stiva, push)
            coada.append((urm, idx_nou, noua))

    return False#coada vida fara acceptare




with open("1input.txt", "r") as file:
    brute = file.readlines()
linii = [linie.strip() for linie in brute if linie.strip() != ""]

tranzitii, stare_init, simbol_init, stari_finale, mod, cuvant = citeste_pda(linii)
with open("1output.txt", "w") as file:
    print("Acceptat" if simuleaza(tranzitii, stare_init, simbol_init, cuvant, stari_finale, mod) else "Respins", file=file)
