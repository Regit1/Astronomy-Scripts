import csv
import sys

str = sys.argv[1]
with open(str, mode='r', encoding='ascii') as file:
    reader = csv.reader(file,delimiter=' ')
    next(reader)

    for row in reader:
        with open('output.ascii', mode='a', encoding='ascii') as file:
            file.write(f"{row[2]} {row[3]}\n")

with open(str, mode = 'w', encoding= 'ascii') as file:
    pass


with open('output.ascii', mode='r', encoding='ascii') as file:
    reader = csv.reader(file,delimiter=' ')

    for row in reader:
        with open(str, mode='a', encoding='ascii') as file:
            file.write(f"{row[0]} {row[1]}\n")

with open('output.ascii', mode = 'w', encoding= 'ascii') as file:
    pass
