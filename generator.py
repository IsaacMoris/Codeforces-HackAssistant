import random

def gen():
    t = 1
    mx_n = 1800
    mx_q = int(1e4)
    aaaa = int(1e8)

    while t > 0:
        t -= 1
        n = 2000
        print(n)
        order = list(range(1, 2 * n + 1))
        random.shuffle(order)
        for i in range(1, len(order)):
            u = order[i]
            v = order[random.randint(0, i - 1)]
            print(u, v)

gen()
