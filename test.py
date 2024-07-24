import json


with open('../data/input1.json') as f:
    input1 = json.load(f)

with open('../data/input2.json') as f:
    input2 = json.load(f)

z = input1["x"] + input2["y"]

# Write the result to output.json
with open('../data/output.json', 'w') as f:
    json.dump({'z': z}, f)