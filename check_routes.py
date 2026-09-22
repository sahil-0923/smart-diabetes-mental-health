lines = open('app.py', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if '@app.route' in l and ('"/' + '"' in l or "'/'" in l):
        print(i, l.strip())
        print("NEXT:", lines[i+1].strip())
