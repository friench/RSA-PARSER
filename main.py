from internal.AnticaptchaSolver import AntiCaptchaSolver
from RSA import RSA

if __name__ == '__main__':
    rsa = RSA("25 (3).xls", None, None, None, 1, AntiCaptchaSolver("28122411ff422bb5c7bbca11604d9b4d"))

    rsa.start(True)
