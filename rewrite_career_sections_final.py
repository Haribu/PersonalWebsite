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
    ("AI Security Essentials", "SANS Technology Institute (2025)"),
    ("Security Strategic Planning & Policy", "SANS Institute (2024)"),
    ("BSc Computer Security & Forensics", "Edinburgh Napier University (2014)"),
    ("BTEC Nat. Cert. IT Practitioner", "Wirral Metropolitan College (2009)"),
    ("School & Personal Development", "GCSEs & Highers, DofE (2002 - 2007)")
]

certifications = [
    ("Certified Board Advisor", "Connectd"),
    ("SABSA Chartered Architect (SCF)", "SABSA Institute"),
    ("Fellow Member (FCIIS)", "Chartered Institute of Information Security"),
    ("CISSP", "ISC2"),
    ("CISM", "ISACA"),
    ("MScEd", "Edinburgh Napier University"),
    ("Core Certified Consultant", "Splunk"),
    ("Certified Architect", "Splunk"),
    ("Certified Administrator", "Splunk"),
    ("Certified Power User", "Splunk"),
    ("Certified User", "Splunk"),
    ("GIAC SEC504", "SANS Institute"),
    ("Certified Solutions Architect", "Amazon Web Services"),
    ("Certified Cloud Practitioner", "Amazon Web Services"),
    ("CompTIA Security+", "CompTIA"),
    ("CompTIA Linux+", "CompTIA")
]

award_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>'
volunteer_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
edu_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>'
cert_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'

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
new_html += make_carousel("Community", volunteer, volunteer_svg, "glass-icon-cyan")
# Education no longer has glass-card-wide! It's perfectly uniform.
new_html += make_carousel("Education", education, edu_svg, "glass-icon-purple")
new_html += make_carousel("Certifications", certifications, cert_svg, "glass-icon-cyan")

new_html += bottom_part

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Updated successfully")
