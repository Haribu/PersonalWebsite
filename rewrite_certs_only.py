import os

html_path = 'website/templates/career.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

split_marker = '<h2 class="career-section-title">Certifications</h2>'
parts = content.split(split_marker)
if len(parts) != 2:
    print("Error splitting")
    exit(1)

top_part = parts[0]

bottom_parts = parts[1].split('</section>')
bottom_part = '\n</section>' + bottom_parts[1]

providers = {
    "Connectd": ["Certified Board Advisor"],
    "SABSA Institute": ["Chartered Architect (SCF)"],
    "Chartered Institute of Information Security": ["Fellow Member (FCIIS)"],
    "ISC2": ["CISSP"],
    "ISACA": ["CISM"],
    "Edinburgh Napier University": ["MScEd"],
    "Splunk": [
        "Core Certified Consultant",
        "Certified Architect",
        "Certified Administrator",
        "Certified Power User",
        "Certified User"
    ],
    "SANS Institute / GIAC": ["GIAC SEC504"],
    "Amazon Web Services": [
        "Solutions Architect Associate",
        "Cloud Practitioner"
    ],
    "CompTIA": ["Security+", "Linux+"]
}

cert_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'

new_html = top_part + '<h2 class="career-section-title">Certifications</h2>\n        <div class="glass-grid">\n'

for provider, certs in providers.items():
    new_html += f'''            <div class="glass-card card-cyan">
                <div class="glass-header" style="margin-bottom: 0.5rem;">
                    <div class="glass-icon-cyan">{cert_svg}</div>
                    <h3 class="glass-title">{provider}</h3>
                </div>
                <div class="glass-cert-stack mt-auto" style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: auto;">
'''
    for cert in certs:
        new_html += f'                    <span class="cert-badge" style="padding: 0.4rem 0.8rem; font-size: 0.85rem; margin: 0;">{cert}</span>\n'
    new_html += '                </div>\n            </div>\n'

new_html += '        </div>\n    </div>\n' + bottom_part

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Updated successfully")
