#!/usr/bin/env python3
"""Normalize all names across data files: strip spaces for consistency."""
import json

files = {
    'src/data/ResourcesList_Grouped.json': None,
    'src/data/recipesByBuilding.json': None,
    'src/data/goods_reference.json': None,
    'src/data/biomes.json': None,
}

for path in files:
    with open(path) as f:
        files[path] = json.load(f)

# Fix ResourcesList_Grouped.json
rl = files['src/data/ResourcesList_Grouped.json']
for g in rl['Goods']:
    g['Name'] = g['Name'].replace(' ', '')
    for recipe in g.get('Recipes', []):
        inp_list = recipe.get('Inputs', [])
        for i, name in enumerate(inp_list):
            inp_list[i] = name.replace(' ', '')

# Fix recipesByBuilding.json
rb = files['src/data/recipesByBuilding.json']
count = 0
for building, recipes in rb.items():
    for rec in recipes:
        if not isinstance(rec, dict):
            continue
        prod = rec.get('Product', {})
        if isinstance(prod, dict):
            for old in list(prod.keys()):
                new = old.replace(' ', '')
                if old != new:
                    prod[new] = prod.pop(old)
                    count += 1
        for key in list(rec.keys()):
            if key.startswith('Ingredient_') and not key.endswith('_PIDs'):
                slot = rec[key]
                if isinstance(slot, dict):
                    for old in list(slot.keys()):
                        new = old.replace(' ', '')
                        if old != new:
                            slot[new] = slot.pop(old)
                            count += 1

# Fix goods_reference.json
gr = files['src/data/goods_reference.json']
for g in gr:
    g['Name'] = g['Name'].replace(' ', '')

# Fix biomes.json - values are arrays of resource name strings
biomes = files['src/data/biomes.json']
bc = 0
for biome_name, resources in biomes.items():
    for i, name in enumerate(resources):
        new = name.replace(' ', '')
        if name != new:
            resources[i] = new
            bc += 1
if bc:
    print(f'Biomes: fixed {bc} names')

for path, data in files.items():
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

print(f'Done. Fixed {count} space-containing names.')
