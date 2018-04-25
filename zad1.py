#@author = Krystian Krakowski
import string
from itertools import combinations

allvariables = string.ascii_letters + "01"
alloperators = "()~&|^>="
myvariables = set()
precedences = {"(":6,")":6,"~":5,"^":4,"&":3,"|":2,">":1,"=":0} #Korzystam ze standardowych priorytetow, w niektorych opcjach ^ ma mniejszy priorytet niz &

# Sprawdza czy wejscie jest poprawne
def checkifcorrect(expression):
    global myvariables
    myvariables = set()
    myvariables.clear()
    checksyntax = True

    #Sprawdza czy wykorzystujemy dozwolone znaki
    for i in expression:
        if i not in allvariables + alloperators:
            checksyntax = False

    #Sprawdza czy nawiasowanie jest dobrze zrobione
    sum = 0
    for i in expression:
        if i == "(":
            sum += 1
        elif i == ")":
            sum -= 1

        if sum < 0: checksyntax = False; break

    if sum != 0: checksyntax = False

    #Sprawdza czy operatory i zmienne spelniaja zalozenia logicznego zdania
    flag = 0
    for i in expression:
        if flag == 0:
            if (i=="~") | (i=="("): pass
            elif (i==")") | (i in alloperators[2:]): return False
            else: flag = 1; myvariables.add(i)
        elif flag == 1:
            if i in alloperators[2:]: flag = 0
            elif i == ")": pass
            else: return False

    #Sortuje uzyskane zmienne (nie powtarzaja sie)
    myvariables = sorted(myvariables)

    return checksyntax & flag==1

#Dokonuje odwrotnej notacji polski dla zdania logicznego
def rpn(expression):
    stack = []
    line = []

    for i in expression:
        if i not in alloperators: line.append(i) #Jezeli i jest zmienna dodaj do linii
        elif i == "(": stack.append(i) #Jezeli mamy ( to wrzuc na stos
        elif i == ")": #Jezeli mamy ) to do linii dodawaj to co bylo miedzy nawiasami
            while stack[-1] != "(": line.append(stack.pop())
            stack.pop()
        else: #Dla pozostalych operatorow
            while len(stack) > 0:
                if (stack[-1] != "(") & ((precedences[i] < precedences[stack[-1]]) | (
                        (precedences[i] == precedences[stack[-1]]) & (stack[-1] != "~"))):
                    line.append(stack.pop()) #Dodawaj do linii zrzucone ze stosu znaki wedlug waznosci
                else:
                    break
            stack.append(i)

    while len(stack)>0: line.append(stack.pop())

    return line

#Dokonuje obliczen na odwrotnej notacji polskiej - wypisuje wartosc
def reverse_rpn(expression, varevaluation):
    stack = []

    for i in expression:
        if i == "&": stack[-2] &= stack[-1]; stack.pop()
        elif i == "|": stack[-2] |= stack[-1]; stack.pop()
        elif i == "^": stack[-2] ^= stack[-1]; stack.pop()
        elif i == "~": stack[-1] = not stack[-1]
        elif i == ">": stack[-2] = stack[-1] or (not stack[-2]); stack.pop()
        elif i == "=": stack[-2] = (stack[-2]==stack[-1]); stack.pop()
        elif i == "0": stack.append(False)
        elif i == "1": stack.append(True)
        else: stack.append(varevaluation[i])

    return stack.pop()

#Korzystajac z algorytmu Quine-McCluskey'a tworzy minterms'y
def minterms(expression):
    myminterms = set()
    sizeofmyvariables = len(myvariables)
    expand = 1<<sizeofmyvariables
    varevaluation = {}
    bitmask = ""
    i = 0

    #Tworzy maske bitowa i dla niej wylicza wartosc wyrazenia
    while i<expand:
        temp = i
        varevaluation.clear()
        bitmask = ""
        for j in myvariables:
            varevaluation[j] = (temp%2 == 1)
            bitmask+=str(temp%2)
            temp=temp//2

        if reverse_rpn(expression,varevaluation):
            myminterms.add((1<<i, bitmask))

        i+=1

    return myminterms

#Wyznaczam wszystkie prime implicants
def prime_implicants(myminterms):
    myprime_implicants = set()

    while 1:
        used = set()
        notused = set()
        count = 0
        bitmask = ""

        #Dla kazdej dwojki mintermsow (takze tych nowych) sprawdza ktore z nich roznia sie tylko jednym bitem
        for i, j in combinations(myminterms,2):
            count = 0
            bitmask = ""
            for k in range(len(myvariables)):
                if(i[1][k]!=j[1][k]): count+=1

            if count==1:
                for k in range(len(myvariables)):
                    if i[1][k]!=j[1][k]: bitmask+=str("-")
                    else: bitmask+=i[1][k]
                notused.add((i[0]|j[0],bitmask))
                used.add(i)
                used.add(j)

        #Nieuzywane mintermsy uznaje za prime implicants
        for i in myminterms:
            if i not in used:
                myprime_implicants.add(i)

        myminterms = notused

        if len(myminterms) == 0: break

    return myprime_implicants

#Wybiera te prime implicants, ktore pokryja w calosci tabele, oraz beda najlepsza opcja
def min_of_prime_implicants(myprime_implicants, myminterms):
    myminterms_bitmask = 0
    for i, _ in myminterms:
        myminterms_bitmask |= i

    myprime_implicants_bitmask = 0
    for i in range(len(myminterms)):
        for j in combinations(myprime_implicants,i+1):
            myprime_implicants_bitmask = 0

            for k, _ in j:
                myprime_implicants_bitmask |= k

            if myprime_implicants_bitmask == myminterms_bitmask: return j

#Sprowadza wszystko do postaci typu string (ukrucone wyrazenie logiczne)
def to_string(mysmallest_prime_implicants):
    string = ""
    for i in range(len(mysmallest_prime_implicants)):
        for j in range(len(myvariables)):
            if mysmallest_prime_implicants[i][1][j] == "0":
                string += ("~" + myvariables[j] + "&")
            elif mysmallest_prime_implicants[i][1][j] == "1":
                string += (myvariables[j] + "&")
        string = string[:-1]
        string += "|"
    string = string[:-1]

    return string

#Glowny algorytm wykonujacy skracanie wyrazenia
def Quine_McCluskey(expression):
    expression = expression.replace(" ","")
    if(not checkifcorrect(expression)): return "Zle wejscie"
    expression = rpn(expression)

    myminterms = minterms(expression)

    if len(myvariables) == 0: return str(reverse_rpn(expression))
    if len(myminterms) == 0: return "0" #Wszystko falsz
    if len(myminterms) == 1<<len(myvariables): return "1" #Wszystko prawda

    return to_string(min_of_prime_implicants(prime_implicants(myminterms), myminterms))

if __name__ == "__main__":
    print(Quine_McCluskey("~~a&b>d&c&~c"))
    print(Quine_McCluskey("a&b&c=b|c"))
    print(Quine_McCluskey("a^b"))
