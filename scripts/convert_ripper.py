#!/usr/bin/env python3
"""Convert AssetRipper YAML assets to recipesByBuilding.json + ResourcesList_Grouped.json"""
import os, sys, json, re
from collections import defaultdict

RIPPER = "ripper"
ASSETS = os.path.join(RIPPER, "ExportedProject", "Assets", "MonoBehaviour")

def read_asset(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def extract_field(content, field_name):
    m = re.search(rf'^  {field_name}:\s*(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else None

def extract_product(content):
    m = re.search(r'producedGood:\s*\n\s*amount:\s*(\d+)\s*\n\s*good:.*?guid:\s*([0-9a-fA-F]{32})', content)
    return (int(m.group(1)), m.group(2).lower()) if m else (None, None)

def extract_grade_guid(content):
    m = re.search(r'grade:.*?guid:\s*([0-9a-fA-F]{32})', content)
    return m.group(1).lower() if m else None

def extract_production_time(content):
    m = re.search(r'productionTime:\s*([\d.]+)', content)
    return float(m.group(1)) if m else None

def extract_ingredients(content):
    """Extract requiredGoods as list of {guid: amount} slots."""
    m = re.search(r'requiredGoods:\s*\n', content)
    if not m:
        return [], []
    
    block_start = m.end()
    next_field = re.search(r'^  \w+:', content[block_start:], re.MULTILINE)
    block_end = block_start + next_field.start() if next_field else len(content)
    block = content[block_start:block_end]
    
    slots_guids = []
    slots_amounts = []
    for goods_m in re.finditer(r'goods:\s*\n((?:\s+-.*\n?)+)', block):
        goods_block = goods_m.group(1)
        guids = [g.lower() for g in re.findall(r'guid:\s*([0-9a-fA-F]{32})', goods_block)]
        amounts = [int(a) for a in re.findall(r'amount:\s*(\d+)', goods_block)]
        if guids:
            slots_guids.append(guids)
            slots_amounts.append(amounts)
    return slots_guids, slots_amounts

def build_guid_index():
    guid_to_file = {}
    for root, dirs, files in os.walk(ASSETS):
        for f in files:
            if f.endswith('.meta'):
                with open(os.path.join(root, f)) as mf:
                    gm = re.search(r'guid:\s*([0-9a-fA-F]{32})', mf.read())
                if gm:
                    ap = os.path.join(root, f[:-5])
                    if os.path.exists(ap):
                        guid_to_file[gm.group(1).lower()] = ap
    return guid_to_file

def main():
    print("Indexing...")
    guid_to_file = build_guid_index()
    print(f"  {len(guid_to_file)} assets")
    
    # Good names
    good_names = {}
    for guid, path in guid_to_file.items():
        c = read_asset(path)
        cid = extract_field(c, 'consoleId')
        if cid:
            good_names[guid] = cid
    
    # Grades
    grade_stars = {}
    for guid, path in guid_to_file.items():
        c = read_asset(path)
        nm = extract_field(c, 'm_Name')
        if nm in ('Grade0', 'Grade1', 'Grade2', 'Grade3'):
            grade_stars[guid] = int(nm[-1])
    
    print(f"  {len(good_names)} goods, {len(grade_stars)} grades")
    
    # Parse recipes
    recipes = []
    for guid, path in guid_to_file.items():
        c = read_asset(path)
        if 'producedGood:' not in c or 'requiredGoods:' not in c:
            continue
        
        amt, prod_guid = extract_product(c)
        if not prod_guid:
            continue
        
        pname = good_names.get(prod_guid, f"?{prod_guid[:6]}")
        gguid = extract_grade_guid(c)
        stars = grade_stars.get(gguid, 0) if gguid else 0
        tm = extract_production_time(c)
        ig, ia = extract_ingredients(c)
        
        ings = []
        for si, sg in enumerate(ig):
            sa = ia[si] if si < len(ia) else [1]*len(sg)
            slot = {}
            for i, g in enumerate(sg):
                slot[good_names.get(g, f"?{g[:6]}")] = sa[i] if i < len(sa) else 1
            if slot:
                ings.append(slot)
        
        recipes.append({
            'product': pname, 'amount': amt, 'stars': stars,
            'time': tm, 'ingredients': ings
        })
    
    print(f"\n{len(recipes)} recipes total\n")
    
    # Print summary grouped by product
    by_product = defaultdict(list)
    for r in recipes:
        by_product[r['product']].append(r)
    
    for product, recs in sorted(by_product.items()):
        for r in recs:
            ings_str = ' | '.join(
                '/'.join(f'{n}({a})' for n, a in s.items())
                for s in r['ingredients']
            )
            print(f"  {product} {r['stars']}★ {r['time']}s: [{ings_str}]")

if __name__ == "__main__":
    main()
