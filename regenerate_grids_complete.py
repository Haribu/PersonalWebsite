import os

html_path = 'website/templates/career.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

split_start = '<h2 class="career-section-title">Honors & Awards</h2>'
parts = content.split(split_start)
if len(parts) != 2:
    print("Error splitting at start")
    exit(1)

top_part = parts[0][:parts[0].rfind('<div class="carousel-section">')]

bottom_parts = parts[1].split('</section>')
if len(bottom_parts) < 2:
    print("Error splitting at end")
    exit(1)

bottom_part = '\n</section>' + bottom_parts[-1]

awards = {
    "Edinburgh Napier University": [
        ("Napier Alumni Excellence Award", "2024"),
        ("University Medal", "2014")
    ],
    "SenseOn": [
        ("Discovered, Not Found", "2022")
    ],
    "Adarma Security": [
        ("Adarma Champion", "2020"),
        ("Most Valuable Player", "2019")
    ],
    "Scottish Cyber Awards": [
        ("Cyber Evangelist of the Year", "2018"),
        ("Best New Cyber Talent", "2016")
    ],
    "Security Excellence Awards": [
        ("Security Professional Under 30", "2018")
    ],
    "ECS": [
        ("Outstanding People Award", "2017 & 2015")
    ]
}

community = {
    "Charities & Non-Profits": [
        ("Nightline Association", "Board Trustee & IT/Training Coordinator (2011 - 2023)"),
        ("Positive Realities", "Chairperson & Trustee (2015 - 2019)"),
        ("First Aid Africa", "Project Coordinator & Training Officer (2008 - 2010)")
    ],
    "Education & Academic": [
        ("Edinburgh Napier University", "Associate Staff (2019 - 2026)"),
        ("Journal of Cyber Security Technology", "Reviewer"),
        ("Skills Development Scotland", "Industry Rep for South of Scotland Digital Skills Hub")
    ],
    "Professional Bodies & Communities": [
        ("Cyber Scotland Connect", "Co-founder (2018 - Present)"),
        ("CompTIA", "Certification Advisory Committee Member (2022 - Present)"),
        ("Splunk", "Edinburgh User Group Leader (2016 - 2021)"),
        ("Building Cyber Collective", "Advisor")
    ]
}

education = {
    "SANS Technology Institute": [
        ("AI Security Essentials", "2025"),
        ("Security Strategic Planning & Policy", "2024")
    ],
    "Edinburgh Napier University": [
        ("BSc Computer Security & Forensics", "First Class Honours, 2014")
    ],
    "Wirral Metropolitan College": [
        ("BTEC Nat. Cert. IT Practitioner", "Merit, 2009")
    ],
    "School / General": [
        ("School & Personal Development", "GCSEs & Highers, DofE (2002 - 2007)")
    ]
}

certs = {
    "Connectd": ["Certified Board Advisor"],
    "SABSA Institute": ["Chartered Architect (SCF)"],
    "CIISec": ["Fellow Member (FCIIS)"],
    "ISC2": ["CISSP"],
    "ISACA": ["CISM"],
    "Edinburgh Napier University": ["MScEd"],
    "Splunk": ["Core Certified Consultant", "Certified Architect", "Certified Administrator", "Certified Power User", "Certified User"],
    "SANS / GIAC": ["GIAC SEC504"],
    "Amazon Web Services": ["Solutions Architect Associate", "Cloud Practitioner"],
    "CompTIA": ["Security+", "Linux+"]
}

award_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>'
volunteer_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
edu_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>'
cert_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'

new_html = top_part

def make_list_card_grid(title, groups, svg, icon_class, card_mod=""):
    out = f'    <div class="carousel-section">\n        <h2 class="career-section-title">{title}</h2>\n        <div class="glass-grid">\n'
    for issuer, items in groups.items():
        out += f'''            <div class="glass-card {card_mod}">
                <div class="glass-header" style="margin-bottom: 1rem;">
                    <div class="{icon_class}">{svg}</div>
                    <h3 class="glass-title">{issuer}</h3>
                </div>
                <div style="display: flex; flex-direction: column; gap: 1rem; margin-top: auto;">
'''
        for name, role in items:
            out += f'''                    <div>
                        <strong style="display: block; color: var(--text-primary); font-size: 0.95rem; margin-bottom: 0.15rem;">{name}</strong>
                        <span style="display: block; color: var(--text-secondary); font-size: 0.85rem; line-height: 1.3;">{role}</span>
                    </div>\n'''
        out += '                </div>\n            </div>\n'
    out += '        </div>\n    </div>\n\n'
    return out

def make_badge_card_grid(title, groups, svg, icon_class, card_mod=""):
    out = f'    <div class="carousel-section">\n        <h2 class="career-section-title">{title}</h2>\n        <div class="glass-grid">\n'
    for issuer, badges in groups.items():
        out += f'''            <div class="glass-card {card_mod}">
                <div class="glass-header" style="margin-bottom: 0.5rem;">
                    <div class="{icon_class}">{svg}</div>
                    <h3 class="glass-title">{issuer}</h3>
                </div>
                <div class="glass-cert-stack mt-auto" style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: auto;">
'''
        for b in badges:
            out += f'                    <span class="cert-badge" style="padding: 0.4rem 0.8rem; font-size: 0.85rem; margin: 0;">{b}</span>\n'
        out += '                </div>\n            </div>\n'
    out += '        </div>\n    </div>\n'
    return out

new_html += make_list_card_grid("Honors & Awards", awards, award_svg, "glass-icon-purple", "card-purple")
new_html += make_list_card_grid("Community", community, volunteer_svg, "glass-icon-cyan", "")
new_html += make_list_card_grid("Education", education, edu_svg, "glass-icon-purple", "card-purple")
new_html += make_badge_card_grid("Certifications", certs, cert_svg, "glass-icon-cyan", "")

new_html += bottom_part

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Updated successfully")
