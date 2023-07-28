import math


def search_fare(dist, ftype):
    """Search the fare corresponding to the currently traveled distance"""
    with open(f"res/fare/{ftype}.csv", 'r') as file:
        with open(f"res/fare/{ftype}.csv", 'r') as filecp:
            for _ in range(len([0 for _ in filecp])):
                line = file.readline().strip()
                line = line.split(';')
                if line == ['']:
                    # Buffer lines
                    continue
                if math.ceil(dist) in range(int(line[0]), int(line[1]) + 1):
                    return int(line[2])
            return None