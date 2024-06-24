def fizzbuzz():
    for i in range(1, 10):
        if i % 3 == 0 and i % 5 == 0:
            print(f"{i}", "is a fizzbuzz")
        if i % 3 == 0:
            print(f"{i}", "is a fizz")
        if i % 5 == 0:
            print(f"{i}", "is a buzz")


print(fizzbuzz())
