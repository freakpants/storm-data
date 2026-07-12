#!/usr/bin/env python3
"""Fix unknown entries in recipesByBuilding.json by fetching missing data via AssetRipper API.
Usage: python3 scripts/fix_unknowns.py [port]
"""
import urllib.request, json, urllib.parse, sys, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 54348
BASE = f"http://172.29.224.1:{PORT}"
CI = 6

def fetch(pid, ci=CI):
    p = {'C': {'B': {'P': []}, 'I': ci}, 'D': pid}
    url = f"{BASE}/Assets/Json?Path={urllib.parse.quote(json.dumps(p, separators=(',', ':')))}"
    with urllib.request.urlopen(url, timeout=3) as r:
        return json.loads(r.read())

def main():
    recipe_file = "src/data/recipesByBuilding.json"
    with open(recipe_file) as f:
        data = json.load(f)

    # Find all unknown entries (Product is {"?": ...})
    unknown_pids = set()
    for building, entries in data.items():
        for e in entries:
            if list(e['Product'].keys())[0] == '?':
                unknown_pids.add(e['RecipePID'])

    print(f"Unknown PIDs: {sorted(unknown_pids)}")

    if not unknown_pids:
        print("No unknowns!")
        return

    # Fetch each unknown recipe
    for pid in sorted(unknown_pids):
        print(f"  Fetching PID {pid}...")
        d = fetch(pid)
        s = d.get('m_Structure', d)
        gp = s.get('grade', {}).get('m_PathID', 0)
        tm = s.get('productionTime', 0)

        # Look up grade star
        try:
            gd = fetch(gp)
            grade = int(gd.get('m_Name', 'Grade0')[-1])
        except:
            grade = 0

        # Determine product
        if 'servedNeed' in s:
            sn_pid = s['servedNeed']['m_PathID']
            nd = fetch(sn_pid)
            product_name = nd.get('m_Name', f'Service_{sn_pid}')
            product_pid = sn_pid

            # Parse ingredients - handle both array and single-object formats
            req = s.get('requiredGoods', [])
            if isinstance(req, dict):
                req = [req]  # single slot wrapped as object
            ings = []
            for slot in req:
                sl = {}
                for ing in slot.get('goods', []):
                    ipid = ing['good']['m_PathID']
                    try:
                        ig = fetch(ipid)
                        iname = (ig.get('m_Structure', ig).get('consoleId')
                                 or ig.get('consoleId')
                                 or f'Good_{ipid}')
                    except:
                        iname = f'Good_{ipid}'
                    sl[iname] = ing.get('amount', 1)
                if sl:
                    ings.append(sl)

        elif 'water' in s and 'amount' in s:
            # RainCatcher recipes
            wpid = s['water']['m_PathID']
            try:
                wd = fetch(wpid)
                product_name = (wd.get('m_Structure', wd).get('consoleId')
                                or wd.get('consoleId')
                                or wd.get('m_Name')
                                or f'Water_{wpid}')
            except:
                product_name = f'Water_{wpid}'
            product_pid = wpid
            ings = []

        elif 'producedGood' in s:
            pg = s['producedGood']
            ppid = pg['good']['m_PathID']
            try:
                pg_data = fetch(ppid)
                product_name = pg_data.get('m_Structure', pg_data).get('consoleId') or pg_data.get('consoleId') or f'Good_{ppid}'
            except:
                product_name = f'Good_{ppid}'
            product_pid = ppid
            ings = []
        else:
            print(f"    WARNING: PID {pid} has unknown recipe type!")
            continue

        # Update all entries with this RecipePID
        for building, entries in data.items():
            for e in entries:
                if e['RecipePID'] == pid:
                    e['Product'] = {product_name: e['Product'].get('?', 1)}
                    e['ProductPID'] = product_pid
                    e['Time'] = tm
                    e['Grade'] = grade
                    e['GradePID'] = gp
                    # Add ingredient data
                    for i, slot in enumerate(ings):
                        e[f'Ingredient_{i+1}'] = slot
                    print(f"    Fixed {building}: {product_name} ({grade}star)")

    # Save
    os.rename(recipe_file, recipe_file + '.bak')
    with open(recipe_file, 'w') as f:
        json.dump(data, f, indent=2)

    # Verify
    remaining = sum(1 for v in data.values() for e in v if list(e['Product'].keys())[0] == '?')
    total = sum(len(v) for v in data.values())
    print(f"\nDone! {total} recipes, {remaining} unknown (was {len(unknown_pids)} recipes)")

if __name__ == '__main__':
    main()
