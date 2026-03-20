import os

html_path = 'website/templates/career.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

split_marker = '<h2 class="career-section-title">Honors & Awards</h2>'
parts = content.split(split_marker)
if len(parts) != 2:
    print("Error splitting")
    exit(1)

top_part = parts[0]
# To correctly reconstruct after Certifications
# Find where the main container ends. It ends exactly before footer include.
bottom_part = '    </div>\n    <div class="divider"></div>\n</main>\n\n{% include "footer.html" %}\n'

awards = [
    ("Napier Alumni Excellence Award", "Edinburgh Napier University (2024)"),
    ("Discovered, Not Found", "SenseOn (2022) - Contribution to product discovery"),
    ("Adarma Champion", "Adarma Security (2020)"),
    ("Adarma Most Valuable Player", "Adarma Security (2019)"),
    ("Cyber Evangelist of the Year", "Scottish Cyber Awards (2018)"),
    ("Security Professional Under 30", "Security Excellence Awards (2018)"),
    ("Outstanding People Award", "ECS (2017) - Splunk Enablement Programme"),
    ("Best New Cyber Talent", "Scottish Cyber Awards (2016)"),
    ("Outstanding People Award", "ECS (2015) - Dedication to a Customer"),
    ("University Medal", "Edinburgh Napier University (2014)"),
]

volunteer = [
    ("Cyber Scotland Connect", "Co-founder (2018 - Present)"),
    ("CompTIA", "Certification Advisory Committee Member & Industry Specialist (2022 - Present)"),
    ("Nightline Association", "Board Trustee & Former IT/Training Coordinator (2011 - 2023)"),
    ("Edinburgh Napier University", "Associate Staff (2019 - 2026)"),
    ("Skills Development Scotland & South of Scotland Digital Skills Hub", "Industry Rep (2019 - 2023)"),
    ("Positive Realities", "Chairperson & Trustee (2015 - 2019)"),
    ("Splunk", "Edinburgh User Group Leader (2016 - 2021)"),
    ("Building Cyber Collective", "Advisor"),
    ("Journal of Cyber Security Technology", "Reviewer"),
    ("First Aid Africa", "Project Coordinator & Training Officer (2008 - 2010)")
]

education = [
    ("BSc (Hons) Computer Security & Forensics", "Edinburgh Napier University (First Class Honours, 2014)"),
    ("AI Security Essentials for Business Leaders", "SANS Technology Institute (2025)"),
    ("LDR514: Security Strategic Planning & Policy", "SANS Technology Institute (2024)"),
    ("BTEC Level 3 Nat. Cert. IT Practitioner", "Wirral Metropolitan College (Merit, 2009)"),
    ("School & Personal Development", "GCSEs & Highers, Duke of Edinburgh, Basic Expedition Leader (2002 - 2007)")
]

certifications = [
    "Connectd Certified Board Advisor",
    "SABSA Chartered Architect - Foundation (SCF)",
    "FCIIS",
    "CISSP",
    "CISM",
    "MScEd",
    "Splunk Core Certified Consultant",
    "Splunk Certified Architect",
    "Splunk Certified Administrator",
    "Splunk Certified Power User",
    "Splunk Certified User",
    "GIAC SEC504: Hacker Tools, Techniques, Exploits, and Incident Handling",
    "AWS Certified Solutions Architect – Associate",
    "AWS Certified Cloud Practitioner",
    "CompTIA Security+",
    "CompTIA Linux+"
]

award_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>'
volunteer_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
edu_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>'

new_html = top_part

def make_carousel(title, items, svg, icon_class, card_mod=""):
    html = f'    <div class="carousel-section">\n        <h2 class="career-section-title">{title}</h2>\n        <div class="horizontal-scroller">\n'
    for item in items:
        html += f'''            <div class="glass-card {card_mod}">
                <div class="glass-header">
                    <div class="{icon_class}">{svg}</div>
                    <h3 class="glass-title">{item[0]}</h3>
                </div>
                <p class="glass-desc">{item[1]}</p>
            </div>\n'''
    html += '        </div>\n    </div>\n\n'
    return html

new_html += make_carousel("Honors & Awards", awards, award_svg, "glass-icon-purple", "card-purple")
new_html += make_carousel("Volunteering & Community", volunteer, volunteer_svg, "glass-icon-cyan")
new_html += make_carousel("Education", education, edu_svg, "glass-icon-cyan", "glass-card-wide")

new_html += '    <div class="carousel-section">\n        <h2 class="career-section-title">Certifications</h2>\n        <div class="glass-cert-stack">\n'
for cert in certifications:
    new_html += f'            <span class="cert-badge">{cert}</span>\n'
new_html += '        </div>\n    </div>\n\n'

new_html += bottom_part

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Updated successfully")
