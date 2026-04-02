from phone_normalizer import apply_changes, normalize_tw, process_node

test_cases = [
    "02-27550888",
    "(04)22281111",
    "0912345678",
    "+886-2-27550888",
    "0800-080-365",
    "0800-080-123",
    "tel:+886912345678",
    "not-a-number",
    "02-12345678 ; 0912-345-678",  # semicolon-separated
    "02-27550888#123",             # extension via #
    "04-22281111#56",              # extension via #
    "02-27550888 ext. 9",          # extension via ext.
    "0912345678,5",                # extension via comma (PBX pause)
]

print("Single number normalization:")
for t in test_cases:
    print(f"  {t!r:35} -> {normalize_tw(t)!r}")

print()
print("Node tag processing:")
sample_nodes = [
    {"name": "Some Shop", "phone": "02-27550888"},
    {"name": "Cafe", "phone": "0912345678", "contact:phone": "tel:+886912345678"},
    {"name": "Bad Data", "phone": "not-a-number"},
    {"name": "Multi", "phone": "02-12345678 ; 0912-345-678"},
]
for node in sample_nodes:
    changes = process_node(node)
    updated = apply_changes(node, changes)
    print(f"  {node['name']}: {changes if changes else '(no changes)'}")
    if changes:
        print(f"    before: { {k: v for k, v in node.items() if k != 'name'} }")
        print(f"    after:  { {k: v for k, v in updated.items() if k != 'name'} }")
