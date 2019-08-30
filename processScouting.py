import pandas as pd

scouting = pd.read_csv('Scouting/March 23 2019.txt', sep='\t')

print(scouting[0:10])

print(scouting.columns)

teamStats = {}

for r in scouting.iterrows():
    print(r[1])
    break