from random import choice

def getRandomKey(limit=4):
    aplhabets = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"

    characterSet = aplhabets + digits

    randomKey = ''
    for _ in range(0, limit):
        randomKey = randomKey + choice(characterSet)

    return randomKey