import random

def print_vector(a):
    print(" ".join(map(str, a)))

def gen_vector1(n, l, r, mul=1):
    return [random.randint(l, r) * mul for _ in range(n)]

def gen_vector2(n, vv):
    m = len(vv)
    return [vv[random.randint(0, m - 1)] for _ in range(n)]

def gen():
    t = 30
    print(t)
    max_N = 10
    max_A = 30  # unused but included for parity

    for _ in range(t):
        n = random.randint(1, max_N)
        m = random.randint(1, max_N)
        print(f"{n} {m}")
        for _ in range(n):
            print_vector(gen_vector1(m, 0, 1))

        p1 = p2 = (1, 1)
        while p1 == p2:
            p1 = (random.randint(1, n), random.randint(1, m))
            p2 = (random.randint(1, n), random.randint(1, m))

        print(f"{p1[0]} {p1[1]}")
        print(f"{p2[0]} {p2[1]}")

# Run the generator
gen()
