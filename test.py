#sert juste a faire des tests de tout petit code

import emoji

print(emoji.emojize("heudhegd: :plus:"))
print(emoji.emojize(":magnifying_glass_tilted_left:"))
print(emoji.emojize(":pancakes:"))

print(emoji.emojize("heudhegd: :half star:"))
print(emoji.emojize("heudhegd: :dots:"))
print(emoji.emojize("heudhegd: :star_half:"))
print(emoji.emojize("heudhegd: :half_star:"))
print(emoji.emojize("heudhegd: :star_half:"))
print(emoji.emojize("heudhegd: :hollow star:"))


def decoupeur(text):
    a = ""
    result = []
    for i in range(len(text)):
        print(text[i])
        if text[i] in [",",";",":"]:
            result.append(a)
            a = ""
        else:
            a = a + text[i]
    if a not in [",",";",":"]:
        result.append(a)
    for _ in result:
        if "" in result:
            result.remove("")
    return result


print(decoupeur("hello,de;dheudhue,dede:dedefesa,"))
print(decoupeur(",;dede;:dede"))