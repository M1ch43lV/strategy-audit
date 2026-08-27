import os, json



levels = set()

whys = set()



for f in os.listdir('results'):

    if f.endswith('.json'):

        try:

            data = json.load(open(os.path.join('results', f), encoding='utf-8'))

            for k, v in data.get('runs', {}).items():

                if v.get('level'):

                    levels.add(v['level'])

                if v.get('why'):

                    whys.add(v['why'])

        except Exception:

            pass



print("Levels:", levels)

print("Whys:", whys)

