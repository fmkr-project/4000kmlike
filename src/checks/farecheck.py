import os



"""
Check the correctness of the fare files structure
"""

for filepath in os.listdir('res/fare/'):
    with open(f"res/fare/{filepath}", 'r') as file:
        last = -1
        with open(f"res/fare/{filepath}", 'r') as f:
            for i in range(len([0 for _ in f])-1):
                line = file.readline().strip()
                line = line.split(';')
                if int(line[0]) != last + 1 and i != 0:
                    raise ValueError(f"in file {filepath}: expected {last+1} but found {int(file.readline().split(';')[0])}")
                last = int(line[1])