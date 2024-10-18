import random

ar = []
for i in range(10):
    ar.append(random.randint(1,10))

for i in range(5):
    with open(f"Isro/public/arrayTxt/test{i}.txt", "w") as file:
        for num in ar:
            file.write(f"{num} ")
