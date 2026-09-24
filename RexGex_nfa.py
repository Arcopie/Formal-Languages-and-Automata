CONCAT = "."
LAMBDA = "lambda"

# ab devine a.b
# (a|b)c (a|b).c
# a*b a*.b
def adauga_concatenare(regex):

    regex = "".join(regex.split())#elimin spatii
    rezultat = ""

    for i in range(len(regex)):
        c = regex[i]

        rezultat += c

        if i + 1 < len(regex):
            urmator = regex[i + 1]
            #scriem . pentru concatenare intre simboluri unde este cazul
            poate_fi_sfarsit = c.isalnum() or c == ")" or c == "*"
            poate_fi_inceput = urmator.isalnum() or urmator == "("

            if poate_fi_sfarsit and poate_fi_inceput:
                rezultat += CONCAT

    return rezultat


def infix_in_postfix(regex):

    # Transformare in forma postfixata(operand operand operator)
    # a.b      -> ab.
    # a | b      -> ab |
    # a *       -> a *
    # (a | b).c  -> ab | c.

    prioritate = {
        "|": 1,
        ".": 2,
    }
    # a|b.c  devine a | (b.c)

    postfix = ""
    stiva = []#
 #tinem temporar operatorii in stiva

    for c in regex:
        #c e simbol => il punem direct in forma postfixata
        if c.isalnum():
            postfix += c
        #marcam un grup de simboluri
        elif c == "(":
            stiva.append(c)
        #final de grup de simboluri
        #scoatem operatorii de pe stiva pentru a genera forma postfixata
        elif c == ")":
            while stiva and stiva[-1] != "(":
                postfix += stiva.pop()

            stiva.pop()#facem pop la '(" pus anterior

        elif c == "*":
            postfix += c

        elif c == "|" or c == ".":
            #cat timp exista op in stiva si nu este (
            # si op din stiva are prioritate mai mare decat operatorul curent
            while stiva and stiva[-1] != "(" and prioritate[stiva[-1]] >= prioritate[c]:
                #scoatem op din stiva -> postfix
                postfix += stiva.pop()
            #ex a.b|c -> ab.c| se executa while ul
            #ex: a|b.c -> abc.| : nu se executa while ul si face doar stiva.append

            stiva.append(c)#punem op in stiva in caz ca vine altul cu prioritate mai mare

    while stiva:
        postfix += stiva.pop()

    return postfix



#simbol -> automat
#operator -> combinam automate
def construieste_thompson(postfix):

    # Pe stiva tinem perechi de forma (stare_initiala, stare_finala)
    #generate la fiecare pas, atunci cand intalnim un operand ne folosim de stiva pentru a genera noul automat
    # la final in vf stivei va fi starea initiala si starea finala

    stiva = []
    tranzitii = [] #
    nr_stari = 0

    for c in postfix:
        if c.isalnum():
            start = nr_stari
            nr_stari += 1

            final = nr_stari
            nr_stari += 1

            tranzitii.append((start, final, c))
            stiva.append((start, final))#punem automatul pentru 1 simbol pe stiva (ex:

        elif c == ".":
            #ex: ab.
            #pe stiva avem (2,3) pt b
            # si (0,1) pt a
            dreapta = stiva.pop()
            stanga = stiva.pop()

            # din 1 mergem in 2 cu lambda
            tranzitii.append((stanga[1], dreapta[0], LAMBDA))
            #pe stiva punem perechea (0,3)
            stiva.append((stanga[0], dreapta[1]))

        elif c == "|":
            dreapta = stiva.pop()
            stanga = stiva.pop()
            #creem 2 stari noi pt automatul de reuniune
            start = nr_stari
            nr_stari += 1
            final = nr_stari
            nr_stari += 1

            tranzitii.append((start, stanga[0], LAMBDA))
            tranzitii.append((start, dreapta[0], LAMBDA))
            tranzitii.append((stanga[1], final, LAMBDA))
            tranzitii.append((dreapta[1], final, LAMBDA))

            stiva.append((start, final))

        elif c == "*":
            automat = stiva.pop()

            start = nr_stari
            nr_stari += 1

            final = nr_stari
            nr_stari += 1
            #automat[0]-inceputul automatului
            #automat[1]- sfarsitul automatului
            #start-stare ajutatoare(pt repetare si iesire directa fara a folosi simbolul)
            #final-stare ajutatoare
            tranzitii.append((start, automat[0], LAMBDA))#intram in automat
            tranzitii.append((start, final, LAMBDA))#direct in stare finala(0 aparitii ale simbolului)
            tranzitii.append((automat[1], automat[0], LAMBDA))#din finalul automatului revenim la inceput(repetare)
            tranzitii.append((automat[1], final, LAMBDA))#finalul automatului -> starea destinatie

            stiva.append((start, final))

    start_final = stiva.pop()
    return nr_stari, tranzitii, start_final[0], start_final[1]


with open("RegEx_input.txt", "r") as fin:
    regex = fin.readline().strip()

regex = adauga_concatenare(regex)
postfix = infix_in_postfix(regex)
print(postfix)
nr_stari, tranzitii, start, final = construieste_thompson(postfix)

with open("RegEx_output.txt", "w") as fout:
    fout.write(str(nr_stari) + "\n")

    for stare in range(nr_stari):
        fout.write(str(stare))
        if stare + 1 < nr_stari:
            fout.write(" ")
    fout.write("\n")

    for sursa, destinatie, simbol in tranzitii:
        fout.write(f"{sursa} {destinatie} {simbol}\n")

    fout.write(f"{start} {final}\n")
