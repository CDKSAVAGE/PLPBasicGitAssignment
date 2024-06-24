def odds_even(start, end):
    for i in range(start, end):
        if i % 2 == 0:
            print(i, "even")
        else:
            print(i, "odd")


fast = 15
last_digit = 30
print(odds_even(fast, last_digit))
