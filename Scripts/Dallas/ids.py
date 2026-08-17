import csv
from collections import defaultdict

cip_year = 2024
projects = defaultdict(int)

with open(r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\\"+str(cip_year)+".csv", "r", newline="",
    encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        project = row[4]
        projects[project.split(' - ')[0]] += 1

    print(projects)