import os

filepath = 'website/templates/advisory.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

sec_start = content.find('<section>') + len('<section>\n')
op_start = content.find('    <h2 class="tidir-title gradient-text">Operating Principles</h2>')
serv_start = content.find('    <div class="advisory-grid">')
meth_start = content.find('    <h2 class="tidir-title gradient-text">The TIDIR Methodology</h2>')
pill_start = content.find('    <h2 class="portfolio-title gradient-text">Core Advisory Pillars</h2>')
net_start = content.find('    <h2 class="portfolio-title gradient-text">Expert Networks')

header = content[:sec_start]
op_block = content[op_start:serv_start]
serv_block = content[serv_start:meth_start]
meth_block = content[meth_start:pill_start]
pill_block = content[pill_start:net_start]
tail = content[net_start:]

# Rename the section
op_block = op_block.replace('>Operating Principles</h2>', '>Leadership Values</h2>')

# Reorder: Services -> Pillars -> Values -> Methodology -> Networks
new_content = header + serv_block + pill_block + op_block + meth_block + tail

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Refactoring complete.")
