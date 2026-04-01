import os
import re
import markdown
import frontmatter
import yaml
from jinja2 import Environment, FileSystemLoader
import shutil
from datetime import datetime
import hashlib
import base64

# Compiled Regex for HTML parsing
IMG_REGEX = re.compile(r'<img[^>]+src="([^">]+)"')
TAG_REGEX = re.compile(r'<[^>]+>')
SCRIPT_REGEX = re.compile(r'<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)
CSP_META_REGEX = re.compile(r'<meta[^>]+http-equiv=["\']Content-Security-Policy["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE)

# Custom Domain configuration (served from root /)
BASE_URL = ''
DOMAIN = 'https://harrymclaren.co.uk'
SITE_URL = f"{DOMAIN}{BASE_URL}"

# CSP Configuration
CSP_BASE = "default-src 'self'; script-src 'self' https://unpkg.com {hashes}; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; frame-src 'self' https://docs.google.com; upgrade-insecure-requests;"

def calculate_csp_hashes(html_content):
    """Find all inline scripts and return their SHA-256 hashes formatted for CSP."""
    # Find all inline scripts (excluding elements with src attribute) using shared regex
    inline_scripts = SCRIPT_REGEX.findall(html_content)
    hashes = []
    for script in inline_scripts:
        sha256_hash = hashlib.sha256(script.encode('utf-8')).digest()
        base64_hash = base64.b64encode(sha256_hash).decode('utf-8')
        hashes.append(f"'sha256-{base64_hash}'")
    return " ".join(hashes)

def render_with_csp(template, **context):
    """Render a template once, then find and inject script hashes into a placeholder."""
    # Single Pass: Render with a stable placeholder
    rendered = template.render(**context, csp_policy="__CSP_POLICY_PLACEHOLDER__")
    hashes = calculate_csp_hashes(rendered)
    
    # Inject calculated hashes into the placeholder
    final_policy = CSP_BASE.format(hashes=hashes)
    return rendered.replace("__CSP_POLICY_PLACEHOLDER__", final_policy)

# Define paths
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
WEBSITE_DIR = os.path.join(ROOT_DIR, 'website')

CONTENT_DIR = os.path.join(WEBSITE_DIR, 'content')
TEMPLATE_DIR = os.path.join(WEBSITE_DIR, 'templates')
PUBLIC_DIR = os.path.join(WEBSITE_DIR, 'public')
ASSETS_DIR = os.path.join(WEBSITE_DIR, 'assets')

def setup_public_dir():
    """Ensure public directory exists and copy assets over."""
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR)
        
    public_assets = os.path.join(PUBLIC_DIR, 'assets')
    if os.path.exists(public_assets):
        shutil.rmtree(public_assets)
    shutil.copytree(ASSETS_DIR, public_assets)

    # Copy .well-known directory for security.txt, etc.
    well_known_src = os.path.join(WEBSITE_DIR, '.well-known')
    well_known_dest = os.path.join(PUBLIC_DIR, '.well-known')
    if os.path.exists(well_known_src):
        if os.path.exists(well_known_dest):
            shutil.rmtree(well_known_dest)
        shutil.copytree(well_known_src, well_known_dest)

    # Generate CNAME file for GitHub Pages Custom Domain binding
    cname_path = os.path.join(PUBLIC_DIR, 'CNAME')
    with open(cname_path, 'w', encoding='utf-8') as f:
        f.write('harrymclaren.co.uk\n')

def build_blog():
    """Convert .md files in content/blog to .html files in public/blog."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    post_template = env.get_template('post.html')
    blog_list_template = env.get_template('blog_list.html')
    
    blog_content_dir = os.path.join(CONTENT_DIR, 'blog')
    if not os.path.exists(blog_content_dir):
        os.makedirs(blog_content_dir)
        
    posts = []
    
    # Initialize markdown converter once
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'codehilite'])

    # Process each markdown file
    for filename in os.listdir(blog_content_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(blog_content_dir, filename)
            
            # Extract frontmatter and content
            post_data = frontmatter.load(filepath)
            
            # Convert markdown to html
            html_content = md.convert(post_data.content)
            md.reset()  # Reset the markdown instance for the next use
            
            out_filename = filename.replace('.md', '.html')
            
            img_match = IMG_REGEX.search(html_content)
            thumbnail = img_match.group(1).replace('{{ base_url }}', BASE_URL) if img_match else ''

            # Approximate reading time: 200 words per minute
            word_count = len(TAG_REGEX.sub('', html_content).split())
            read_time = max(1, word_count // 200)

            # Store post metadata for the index page
            external_link = post_data.get('external_link', '')
            post_meta = {
                'title': post_data.get('title', 'Untitled'),
                'date': post_data.get('date', datetime.now().strftime("%Y-%m-%d")),
                'summary': post_data.get('summary', ''),
                'category': post_data.get('category', ''),
                'external_link': external_link,
                'featured': post_data.get('featured', False),
                'thumbnail': thumbnail,
                'read_time': read_time,
                'url': external_link if external_link else f'{BASE_URL}/blog/{out_filename}',
                'current_url': f'/blog/{out_filename}',
                'content': html_content.replace('{{ base_url }}', BASE_URL)
            }
            posts.append(post_meta)
            
            # Render individual post with dynamic CSP
            final_html = render_with_csp(post_template, **post_meta, base_url=BASE_URL, site_url=SITE_URL, og_type="article")
            
            # Save output
            output_dir = os.path.join(PUBLIC_DIR, 'blog')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(os.path.join(output_dir, out_filename), 'w', encoding='utf-8') as f:
                f.write(final_html)

    # Output the blog index page
    posts.sort(key=lambda x: x['date'], reverse=True)
    blog_posts = [p for p in posts if p.get('category') not in ['speaking', 'writing', 'event']]
    blog_index_html = render_with_csp(blog_list_template, title="Transmission Log", posts=blog_posts, base_url=BASE_URL, site_url=SITE_URL, current_url="/blog.html", og_type="website")
    with open(os.path.join(PUBLIC_DIR, 'blog.html'), 'w', encoding='utf-8') as f:
        f.write(blog_index_html)
        
    return posts

# --- Helper Functions ---
MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def parse_start_date(date_str):
    """Extract a sortable start date from strings like 'Jan 2018 - Present', '2016-2021', '2026'."""
    if not date_str:
        return datetime(1900, 1, 1)
    date_str = str(date_str).strip()
    
    # Handle compound ranges: take only the start portion
    start_part = date_str.split(' - ')[0].split(' – ')[0].strip()
    
    # Try "Mon YYYY" format (e.g., "Jan 2018")
    parts = start_part.split()
    if len(parts) == 2:
        month_str = parts[0].lower().rstrip('.')
        if month_str in MONTH_MAP and parts[1].isdigit():
            return datetime(int(parts[1]), MONTH_MAP[month_str], 1)
    
    # Try plain year (e.g., "2016" or from "2016-2021")
    if start_part[:4].isdigit():
        return datetime(int(start_part[:4]), 1, 1)
    
    return datetime(1900, 1, 1)

def sort_section_chronologically(sections):
    """Sort sections and their entries by start date, newest first."""
    for section in sections:
        entries = section.get('entries', [])
        entries.sort(key=lambda e: parse_start_date(e.get('date', '')), reverse=True)
    # Sort sections by the most recent entry date
    def section_sort_key(sec):
        entries = sec.get('entries', [])
        if not entries:
            return datetime(1900, 1, 1)
        return max(parse_start_date(e.get('date', '')) for e in entries)
    sections.sort(key=section_sort_key, reverse=True)
    return sections

def _build_showcase_data():
    """Load and process showcase.yaml data for the showcase page."""
    showcase_yaml_path = os.path.join(CONTENT_DIR, 'showcase.yaml')
    showcase_posts = []
    if os.path.exists(showcase_yaml_path):
        with open(showcase_yaml_path, 'r', encoding='utf-8') as f:
            showcase_posts = yaml.safe_load(f) or []
    
    # Initialize markdown converter once
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'codehilite'])
    for p in showcase_posts:
        if p.get('content'):
            p['content'] = md.convert(p['content']).replace('{{ base_url }}', BASE_URL)
            md.reset()
    
    # Group by year for initial render balance
    from collections import defaultdict
    showcase_by_year = defaultdict(list)
    featured_posts = []
    
    # Sort posts by date descending first
    showcase_posts.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    for p in showcase_posts:
        if p.get('featured'):
            featured_posts.append(p)
        else:
            date_str = p.get('date', '')
            if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
                year = date_str[:4]
            else:
                year = "Archive"
            showcase_by_year[year].append(p)
    
    # Convert to sorted list of years (descending, but Archive at the end)
    years_only = [y for y in showcase_by_year.keys() if y.isdigit()]
    sorted_years = sorted(years_only, reverse=True)
    if "Archive" in showcase_by_year:
        sorted_years.append("Archive")
    
    grouped_showcase = [{"year": year, "posts": showcase_by_year[year]} for year in sorted_years]
    
    # Calculate counts for each category
    counts = {
        'all': len(showcase_posts),
        'speaking': sum(1 for p in showcase_posts if p.get('category') == 'speaking'),
        'writing': sum(1 for p in showcase_posts if p.get('category') == 'writing'),
        'event': sum(1 for p in showcase_posts if p.get('category') == 'event')
    }
    
    return featured_posts, grouped_showcase, counts

def _build_career_data():
    """Load and process career.yaml data for the career page."""
    career_yaml_path = os.path.join(CONTENT_DIR, 'career.yaml')
    career_data = {}
    if os.path.exists(career_yaml_path):
        with open(career_yaml_path, 'r', encoding='utf-8') as f:
            career_data = yaml.safe_load(f) or {}

    community_data = career_data.get('community', [])
    education_data = career_data.get('education', [])
    sort_section_chronologically(community_data)
    sort_section_chronologically(education_data)
    
    return career_data, community_data, education_data

def build_pages(posts=[]):
    """Build root-level pages (Home, About, Contact)."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    pages = ['index.html', 'advisory.html', 'career.html', 'contact.html', 'showcase.html']
    
    for page in pages:
        try:
            template = env.get_template(page)
            current_url = "/" if page == "index.html" else f"/{page}"
            title_map = {
                "index.html": None, 
                "advisory.html": "Strategic Advisory", 
                "career.html": "Career & Experience", 
                "contact.html": "Contact", 
                "showcase.html": "Showcase & Contributions"
            }
            page_title = title_map.get(page)
            
            ctx = {
                'base_url': BASE_URL,
                'site_url': SITE_URL,
                'current_url': current_url,
                'title': page_title,
                'og_type': "website"
            }

            if page == 'index.html':
                ctx['recent_posts'] = posts[:2]
            elif page == 'showcase.html':
                featured_posts, grouped_showcase, counts = _build_showcase_data()
                ctx.update({
                    'featured_posts': featured_posts,
                    'grouped_showcase': grouped_showcase,
                    'counts': counts
                })
            elif page == 'career.html':
                career_data, community_data, education_data = _build_career_data()
                ctx.update({
                    'career_timeline': career_data.get('timeline', []),
                    'career_awards': career_data.get('awards', []),
                    'career_community': community_data,
                    'career_education': education_data,
                    'career_certifications': career_data.get('certifications', [])
                })

            final_html = render_with_csp(template, **ctx)
            
            with open(os.path.join(PUBLIC_DIR, page), 'w', encoding='utf-8') as f:
                f.write(final_html)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Skipping {page}, error: {e}")

    return [p for p in pages if os.path.exists(os.path.join(PUBLIC_DIR, p))]


def build_sitemap_and_robots(posts, pages):
    """Generate sitemap.xml and robots.txt based on generated posts and pages."""
    sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    
    # Add pages
    for page in pages:
        url_path = "" if page == "index.html" else f"/{page}"
        sitemap_lines.append(f'  <url>\n    <loc>{SITE_URL}{url_path}</loc>\n    <changefreq>weekly</changefreq>\n  </url>')
        
    # Add blog index
    sitemap_lines.append(f'  <url>\n    <loc>{SITE_URL}/blog.html</loc>\n    <changefreq>weekly</changefreq>\n  </url>')
    
    # Add posts
    for post in posts:
        if post["current_url"].startswith('http'):
            continue
        sitemap_lines.append(f'  <url>\n    <loc>{SITE_URL}{post["current_url"]}</loc>\n    <lastmod>{post["date"]}</lastmod>\n  </url>')
        
    sitemap_lines.append('</urlset>\n')
    
    with open(os.path.join(PUBLIC_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_lines))
        
    robots_txt = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(PUBLIC_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots_txt)

if __name__ == "__main__":
    print("Building static site for Harry McLaren...")
    setup_public_dir()
    posts = build_blog()
    pages = build_pages(posts)
    build_sitemap_and_robots(posts, pages)
    print("Site built successfully in the /public directory!")
