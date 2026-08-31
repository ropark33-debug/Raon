import random

score = 0

print("소수 덧셈/뺄셈 문제")
print("총 10문제")
print("=" * 30)

for num in range(1, 11):

    op = random.choice(["+", "-"])

    while True:
        a = random.randint(10, 999) / 100
        b = random.randint(10, 999) / 100

        a_int = int(round(a * 100))
        b_int = int(round(b * 100))

        if op == "+":
            # 받아올림 발생
            if (a_int % 10) + (b_int % 10) >= 10 or \
               ((a_int // 10) % 10) + ((b_int // 10) % 10) >= 10:
                answer = round(a + b, 2)
                break

        else:
            if a < b:
                a, b = b, a
                a_int, b_int = b_int, a_int

            # 받아내림 발생
            if (a_int % 10) < (b_int % 10) or \
               ((a_int // 10) % 10) < ((b_int // 10) % 10):
                answer = round(a - b, 2)
                break

    print(f"\n[{num}번 문제]")

    print(f"  {a:>5.2f}")
    print(f"{op} {b:>5.2f}")
    print("--------")

    user = float(input("답: "))

    if round(user, 2) == answer:
        print("⭕ 정답!")
        score += 1
    else:
        print(f"❌ 오답! 정답은 {answer:.2f}")

print("\n" + "=" * 30)
print(f"최종 점수 : {score}/10")