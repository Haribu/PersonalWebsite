import csv
import yaml
import re
from datetime import datetime

CSV_FILE = r'C:\Users\hazcl\Projects\PersonalWebsite\.tmp\Personal Website Feedback - Career.csv'
YAML_FILE = r'c:\Users\hazcl\Projects\PersonalWebsite\website\content\career.yaml'

def extract_bold(text):
    match = re.search(r'\*\*(.*?)\*\*', text)
    if match:
        extracted = match.group(1).strip()
        rest = text.replace(match.group(0), '').strip(' -').strip()
        return extracted, rest
    return text, ""

def extract_year(date_str):
    # Try to extract a 4 digit year
    match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if match:
        return match.group(0)
    return date_str

def match_logo(company):
    c = company.lower()
    if 'tesco' in c: return 'logo_tesco.svg'
    if 'senseon' in c: return 'logo_senseon.svg'
    if 'adarma' in c: return 'logo_adarma.svg'
    if 'ecs' in c: return 'logo_adarma.svg'
    return ''

def main():
    data = {"timeline": [], "awards": [], "community": [], "education": [], "certifications": []}

    awards_dict = {}
    community_dict = {}
    education_dict = {}
    cert_dict = {}

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_type = row.get('Type', '').strip()
            date = row.get('Date', '').strip()
            org = row.get('Organisation', '').strip()
            detail = row.get('Detail', '').strip()

            if not row_type:
                continue

            if row_type == 'Employment History':
                lines = [line.strip() for line in org.split('\n') if line.strip()]
                if len(lines) >= 2:
                    company = lines[0]
                    title = lines[-1]
                else:
                    company = org
                    title = ""
                
                logo = match_logo(company)
                bullets = [b.strip() for b in detail.split('\n') if b.strip()]
                if not bullets:
                    bullets = [detail]

                data["timeline"].append({
                    "title": title,
                    "company": company,
                    "logo": logo,
                    "date": date,
                    "bullets": bullets
                })

            elif row_type == 'Honors & Awards':
                title_text, rest = extract_bold(detail)
                year = extract_year(date)
                if org not in awards_dict:
                    awards_dict[org] = []
                # Combine title and rest if rest is important, but standard was just short title
                # Let's include rest as well, or just title if short
                awards_dict[org].append({
                    "title": title_text,
                    "year": year
                })

            elif row_type == 'Community':
                title_text, rest = extract_bold(detail)
                if not title_text:
                    title_text = org
                desc = date
                if rest:
                    desc += " - " + rest
                
                # The section is better to be group based, maybe org?
                # Actually, some orgs have many entries (Splunk).
                if org not in community_dict:
                    community_dict[org] = []
                community_dict[org].append({
                    "title": title_text,
                    "desc": desc
                })

            elif row_type == 'Education':
                title_text, rest = extract_bold(detail)
                desc = date
                if rest:
                    desc += " - " + rest
                
                if org not in education_dict:
                    education_dict[org] = []
                education_dict[org].append({
                    "title": title_text,
                    "desc": desc
                })

            elif row_type == 'Certifications':
                title_text, rest = extract_bold(detail)
                if org not in cert_dict:
                    cert_dict[org] = []
                cert_dict[org].append(title_text)

    # Convert dicts back to lists
    for org, entries in awards_dict.items():
        data["awards"].append({
            "org": org,
            "icon": "circle-check",
            "entries": entries
        })

    for section, entries in community_dict.items():
        data["community"].append({
            "section": section,
            "icon": "heart",
            "entries": entries
        })

    for org, entries in education_dict.items():
        data["education"].append({
            "org": org,
            "icon": "book",
            "entries": entries
        })

    for org, badges in cert_dict.items():
        data["certifications"].append({
            "org": org,
            "badges": badges
        })

    with open(YAML_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    
    print("YAML conversion complete!")

if __name__ == "__main__":
    main()
