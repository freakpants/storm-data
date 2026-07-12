#!/usr/bin/env python3
"""
Extract recipe data from Against the Storm asset bundle.
Processes the bundle in chunks to avoid memory issues.
"""
import os, sys, json
from collections import defaultdict

GAME_BASE = "/mnt/d/SteamLibrary/steamapps/common/Against the Storm"
DATA_DIR = os.path.join(GAME_BASE, "Against_the_Storm_Data")
AA_DIR = os.path.join(DATA_DIR, "StreamingAssets", "aa", "StandaloneWindows64")

def find_main_bundle():
    for f in os.listdir(AA_DIR):
        if f.startswith("defaultlocalgroup") and f.endswith(".bundle"):
            return os.path.join(AA_DIR, f)
    return None

def main():
    sys.path.insert(0, "/home/freakpants/.local/lib/python3.12/site-packages")
    from UnityPy import Environment
    
    bundle = find_main_bundle()
    if not bundle:
        print("Bundle not found!")
        sys.exit(1)
    
    print(f"Bundle: {os.path.basename(bundle)}")
    print(f"Size: {os.path.getsize(bundle) / (1024**3):.2f} GB")
    print("Loading...")
    sys.stdout.flush()
    
    try:
        env = Environment(bundle)
        print(f"Loaded! {len(env.objects)} objects total")
        
        # Count types
        types = defaultdict(int)
        for obj in env.objects:
            types[obj.type.name] += 1
        
        print("\nObject types:")
        for t, c in sorted(types.items(), key=lambda x: -x[1])[:20]:
            print(f"  {t}: {c}")
        
        # Look for MonoBehaviours with recipe-related names
        recipe_like = []
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                try:
                    data = obj.read()
                    if hasattr(data, 'm_Name'):
                        name = str(data.m_Name)
                        # Look for recipe/building/good related objects
                        lower = name.lower()
                        if any(kw in lower for kw in ['recipe', 'good_', 'building_', 'product', 'ingredient']):
                            recipe_like.append((name, obj.path_id))
                except:
                    pass
        
        print(f"\nRecipe-like MonoBehaviours: {len(recipe_like)}")
        for name, pid in recipe_like[:30]:
            print(f"  {name} (path_id={pid})")
        
        env = None
        
    except MemoryError:
        print("MemoryError! Bundle too large.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
