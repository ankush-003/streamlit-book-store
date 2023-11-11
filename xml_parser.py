import xml.etree.ElementTree as ET

# Parse XML file
tree = ET.parse('data.xml')
root = tree.getroot()

# Print root tag
# print(root.tag)
data_store = {}

def store_data(table, data_store):
    data_store[table.tag] = []
    for row in table:
        data = {}
        for val in row:
            data[val.tag] = val.text
        data_store[table.tag].append(data)

# Print all child tags
for child in root:
    # print(child.tag)
    store_data(child, data_store)

print(data_store)

