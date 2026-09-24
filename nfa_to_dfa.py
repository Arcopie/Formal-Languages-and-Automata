LAMBDA = "lambda"

# Stiva si parcurgere dfs si retin starile accesibile din lambda miscari
def lambda_inchidere(stare, tranzitii):
    rezultat = {stare}
    stiva = [stare]

    while stiva:
        curenta = stiva.pop()

        for urmatoare in tranzitii[curenta].get(LAMBDA, set()):
            if urmatoare not in rezultat:
                rezultat.add(urmatoare)
                stiva.append(urmatoare)

    return rezultat

# nfa -> dfa
def construieste_dfa(stari_nfa, alfabet, tranzitii_nfa, start_nfa, finale_nfa):
    #retin inchiderea fiecarei stari
    inchideri = {}
    for stare in stari_nfa:
        inchideri[stare] = lambda_inchidere(stare, tranzitii_nfa)


    start_dfa = frozenset(inchideri[start_nfa]) #stare initiala a dfa este inchiderea starii init din nfa
    stari_dfa = [start_dfa] #prima stare din lista este startul
    tranzitii_dfa = {}

    pozitie = 0#pt parcurgere stari_dfa
    while pozitie < len(stari_dfa):

        stare_dfa = stari_dfa[pozitie]
        tranzitii_dfa[stare_dfa] = {} #dictionar pt starea curenta

        #luam fiecare simbol si calculez tranzitie dfa pe acel simbol
        for simbol in alfabet:
            destinatie = set()#multimea starilor nfa atinse

            for stare_nfa in stare_dfa:
                #obtinem fiecare stare_nfa atinsa mergam pe simbolul curent
                #si adaug in destinatie
                for stare_atinsa in tranzitii_nfa[stare_nfa].get(simbol, set()):
                    destinatie.update(inchideri[stare_atinsa])

            destinatie = frozenset(destinatie)
            tranzitii_dfa[stare_dfa][simbol] = destinatie

            if destinatie not in stari_dfa:
                stari_dfa.append(destinatie)

        pozitie += 1

    #stare finala in dfa <=> intersectia cu stari finale nfa are
    #cel putin o stare
    finale_dfa = set()
    for stare_dfa in stari_dfa:
        if stare_dfa & finale_nfa:
            finale_dfa.add(stare_dfa)

    return stari_dfa, tranzitii_dfa, start_dfa, finale_dfa

#starile care nu pot fi atinse din starea init
def elimina_inaccesibile(stari_dfa, alfabet, tranzitii_dfa, start_dfa, finale_dfa):
    accesibile = {start_dfa}
    coada = [start_dfa]

    pozitie = 0
    while pozitie < len(coada):
        stare = coada[pozitie]

        for simbol in alfabet:
            urmatoare = tranzitii_dfa[stare][simbol]
            if urmatoare not in accesibile:
                accesibile.add(urmatoare)
                coada.append(urmatoare)

        pozitie += 1

    stari_noi = [stare for stare in stari_dfa if stare in accesibile]
    finale_noi = finale_dfa & accesibile

    return stari_noi, tranzitii_dfa, start_dfa, finale_noi

#cauta clasa de echivalenta a unei stari
#(pt moore)
def gaseste_clasa(stare, clase):
    for i in range(len(clase)):
        if stare in clase[i]:
            return i
    return -1

# Eliminam starile de echivalente
#( de la un anumit punct cele 2 stari dun in aceeasi stare
#desi au drum diferit)
def minimizeaza_moore(stari_dfa, alfabet, tranzitii_dfa, start_dfa, finale_dfa):

    nefinale = set(stari_dfa) - finale_dfa
    clase = []
    #impartim partitii in finale si nefinale
    if nefinale:
        clase.append(nefinale)
    if finale_dfa:
        clase.append(finale_dfa)

    while True:
        clase_noi = []

        for clasa in clase:
            grupe = {}#dictionar de grupuri bazat pe semnaturi

            for stare in clasa:

                semnatura = []
                #semnatura= tuplu cu indexul clasei destinatie
                #pt fiecare simbol
                #doua stari cu aceeasi semnatura => sunt echivalente
                for simbol in alfabet:
                    destinatie = tranzitii_dfa[stare][simbol]
                    semnatura.append(gaseste_clasa(destinatie, clase))

                #grupez starile cu aceeasi semnatura
                semnatura = tuple(semnatura)
                if semnatura not in grupe:
                    grupe[semnatura] = set()
                grupe[semnatura].add(stare)

            #fiecare grup devine o noua clasa(partitie)
            for grupa in grupe.values():
                clase_noi.append(grupa)
        #partitia nu s a schimbat, break, am term
        if {frozenset(clasa) for clasa in clase} == {frozenset(clasa) for clasa in clase_noi}:
            break

        clase = clase_noi

    #clasa cu starea initiala e prima
    clase.sort(
        key=lambda clasa: -1 if start_dfa in clasa
        else
            min(stari_dfa.index(stare) for stare in clasa)
    )

    #pt fiecare stare dfa tinem minte indexul clasei de echivalenta
    clasa_pentru_stare = {}
    for i in range(len(clase)):
        for stare in clase[i]:
            clasa_pentru_stare[stare] = i

    #calculam starea init a dfa ului minim
    start_minim = clasa_pentru_stare[start_dfa]
    finale_minim = set()
    tranzitii_minim = {}

    #din fiecare partitie luam cate o stare
    for i in range(len(clase)):
        reprezentant = next(iter(clase[i]))
        tranzitii_minim[i] = {}

        if clase[i] & finale_dfa:
            finale_minim.add(i)#stare fin daca contine o stare fin din dfa

        #urmatoarea stare se calc: tranzitia clasei k pe simbol
        for simbol in alfabet:
            destinatie = tranzitii_dfa[reprezentant][simbol]
            tranzitii_minim[i][simbol] = clasa_pentru_stare[destinatie]

    return clase, tranzitii_minim, start_minim, finale_minim




with open("nfa_to_dfa_input.txt", "r") as fisier:
    linii = fisier.read().splitlines()

stari_nfa = linii[0].split()
alfabet = linii[1].split()
nr_tranzitii = int(linii[2])

tranzitii_nfa = {}
for stare in stari_nfa:
    tranzitii_nfa[stare] = {}

for i in range(nr_tranzitii):
    sursa, destinatie, simbol = linii[3 + i].split()

    if simbol not in tranzitii_nfa[sursa]:
        tranzitii_nfa[sursa][simbol] = set()

    tranzitii_nfa[sursa][simbol].add(destinatie)

start_nfa = linii[3 + nr_tranzitii]
finale_nfa = set(linii[4 + nr_tranzitii].split())

stari_dfa, tranzitii_dfa, start_dfa, finale_dfa = construieste_dfa(
    stari_nfa, alfabet, tranzitii_nfa, start_nfa, finale_nfa
)

nume_dfa = {}
for i in range(len(stari_dfa)):
    nume_dfa[stari_dfa[i]] = "Q" + str(i)

stari_dfa, tranzitii_dfa, start_dfa, finale_dfa = elimina_inaccesibile(
    stari_dfa, alfabet, tranzitii_dfa, start_dfa, finale_dfa
)

tranzitii_dfa_output = []
for stare in stari_dfa:
    for simbol in alfabet:
        tranzitii_dfa_output.append(
            (
                nume_dfa[stare],
                nume_dfa[tranzitii_dfa[stare][simbol]],
                simbol,
            )
        )

clase, tranzitii_minim, start_minim, finale_minim = minimizeaza_moore(
    stari_dfa, alfabet, tranzitii_dfa, start_dfa, finale_dfa
)

nume_minim = []
for i in range(len(clase)):
    nume_minim.append("M" + str(i))

output = []

output.append("DFA MINIM")
output.append(" ".join(nume_minim))
output.append(" ".join(alfabet))
output.append(str(len(clase) * len(alfabet)))

for i in range(len(clase)):
    for simbol in alfabet:
        output.append(
            nume_minim[i]+ " " + nume_minim[tranzitii_minim[i][simbol]] + " " + simbol
        )

output.append(nume_minim[start_minim])
output.append(" ".join(nume_minim[i] for i in range(len(clase)) if i in finale_minim))

with open("nfa_to_dfa_output.txt", "w") as fisier:
    fisier.write("\n".join(output))
