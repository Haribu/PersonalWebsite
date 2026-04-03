import csv
import yaml
import re
from datetime import datetime

CSV_FILE = r'C:\Users\hazcl\Projects\PersonalWebsite\.tmp\Personal Website Feedback - Showcase.csv'
YAML_FILE = r'C:\Users\hazcl\Projects\PersonalWebsite\website\content\showcase.yaml'

# Maps CSV Section values to YAML category values
CATEGORY_MAP = {
    'Public Speaking': 'speaking',
    'Events Hosted': 'event',
    'Publications': 'writing',
}

URL_PATTERN = re.compile(r'https?://\S+')


def extract_url(text: str) -> tuple[str, str]:
    """Extract the first URL from text, returning (url, text_without_url)."""
    match = URL_PATTERN.search(text)
    if match:
        url = match.group(0).rstrip('.,;)')
        cleaned = text[:match.start()].rstrip(' ,;:') + text[match.start() + len(url):].lstrip(' ,;')
        cleaned = cleaned.strip()
        return url, cleaned
    return '', text


def parse_date(date_str: str) -> str:
    """Parse DD/MM/YYYY to YYYY-MM-DD. Returns None if blank."""
    date_str = date_str.strip()
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None


def build_title(details: str, outcomes: str) -> str:
    """Use details as the title (strip any embedded URL)."""
    _, clean = extract_url(details)
    return clean.strip() or details.strip()


def build_content(details: str, outcomes: str) -> str:
    """Build the content/summary field from outcomes (or fall back to details), URL stripped."""
    text = outcomes.strip() if outcomes.strip() else details.strip()
    _, clean = extract_url(text)
    return clean.strip() or text.strip()


def get_external_link(details: str, outcomes: str) -> str:
    """Extract URL from details first, then outcomes."""
    url, _ = extract_url(details)
    if url:
        return url
    url, _ = extract_url(outcomes)
    return url


def main():
    entries = []

    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            primary = row.get('Showcase Section (Primary)', '').strip()
            details = row.get('Details', '').strip()
            outcomes = row.get('Outcomes', '').strip()
            date_raw = row.get('Date', '').strip()

            # Skip rows with no primary section or no details
            if not primary or not details:
                continue

            category = CATEGORY_MAP.get(primary)
            if category is None:
                print(f'  [WARN] Unknown section: {primary!r}')
                continue

            date = parse_date(date_raw)
            external_link = get_external_link(details, outcomes)
            title = build_title(details, outcomes)
            content = build_content(details, outcomes)
            summary = content

            entry = {
                'title': title,
                'category': category,
                'featured': False,
                'content': content,
            }
            if date:
                entry['date'] = date
            if summary and summary != title:
                entry['summary'] = summary
            if external_link:
                entry['external_link'] = external_link

            entries.append(entry)

    # Sort: entries with dates come first (newest first), then undated entries
    dated = sorted([e for e in entries if 'date' in e], key=lambda x: x['date'], reverse=True)
    undated = [e for e in entries if 'date' not in e]
    all_entries = dated + undated

    with open(YAML_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(all_entries, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    print(f'Done! Wrote {len(all_entries)} entries to {YAML_FILE}')


if __name__ == '__main__':
    main()
