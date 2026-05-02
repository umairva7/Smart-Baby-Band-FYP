from dataset import discover_raw, _processed_path
rows = discover_raw()
counts = {}
for src, label in rows:
    corpus = "donateacry" if "donateacry" in str(src) else "babycrying"
    key = (label, corpus)
    counts[key] = counts.get(key, 0) + 1

for k, v in sorted(counts.items()):
    print(f"{k[0]:12} {k[1]:12} {v}")
