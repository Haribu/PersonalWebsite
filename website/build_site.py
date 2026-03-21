import os
import markdown
import frontmatter
import yaml
from jinja2 import Environment, FileSystemLoader
import shutil
from datetime import datetime

# GitHub Pages serves from a subpath (/PersonalWebsite). Local uses root (/).
BASE_URL = '/PersonalWebsite' if os.environ.get('GITHUB_ACTIONS') else ''
DOMAIN = 'https://harrymclaren.github.io'
SITE_URL = f"{DOMAIN}{BASE_URL}"

# Define paths
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(SITE_DIR, 'content')
TEMPLATE_DIR = os.path.join(SITE_DIR, 'templates')
PUBLIC_DIR = os.path.join(SITE_DIR, 'public')
ASSETS_DIR = os.path.join(SITE_DIR, 'assets')

def setup_public_dir():
    """Ensure public directory exists and copy assets over."""
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR)
        
    public_assets = os.path.join(PUBLIC_DIR, 'assets')
    if os.path.exists(public_assets):
        shutil.rmtree(public_assets)
    shutil.copytree(ASSETS_DIR, public_assets)

    # Copy .well-known directory for security.txt, etc.
    well_known_src = os.path.join(SITE_DIR, '.well-known')
    well_known_dest = os.path.join(PUBLIC_DIR, '.well-known')
    if os.path.exists(well_known_src):
        if os.path.exists(well_known_dest):
            shutil.rmtree(well_known_dest)
        shutil.copytree(well_known_src, well_known_dest)

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
            
            import re
            img_match = re.search(r'<img[^>]+src="([^">]+)"', html_content)
            thumbnail = img_match.group(1).replace('{{ base_url }}', BASE_URL) if img_match else ''

            # Approximate reading time: 200 words per minute
            word_count = len(re.sub(r'<[^>]+>', '', html_content).split())
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
                'current_url': external_link if external_link else f'/blog/{out_filename}',
                'content': html_content.replace('{{ base_url }}', BASE_URL)
            }
            posts.append(post_meta)
            
            # Render individual post
            final_html = post_template.render(**post_meta, base_url=BASE_URL, site_url=SITE_URL, og_type="article")
            
            # Save output
            output_dir = os.path.join(PUBLIC_DIR, 'blog')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(os.path.join(output_dir, out_filename), 'w', encoding='utf-8') as f:
                f.write(final_html)

    # Output the blog index page
    # Sort posts by date descending
    posts.sort(key=lambda x: x['date'], reverse=True)
    blog_posts = [p for p in posts if p.get('category') not in ['speaking', 'writing', 'event']]
    blog_index_html = blog_list_template.render(title="Blog", posts=blog_posts, base_url=BASE_URL, site_url=SITE_URL, current_url="/blog.html", og_type="website")
    with open(os.path.join(PUBLIC_DIR, 'blog.html'), 'w', encoding='utf-8') as f:
        f.write(blog_index_html)
        
    return posts

def build_pages(posts=[]):
    """Build root-level pages (Home, About, Contact)."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    
    pages = ['index.html', 'advisory.html', 'career.html', 'contact.html', 'showcase.html']
    
    for page in pages:
        try:
            template = env.get_template(page)
            current_url = "/" if page == "index.html" else f"/{page}"
            title_map = {"index.html": "Home", "advisory.html": "Advisory", "career.html": "Career", "contact.html": "Contact", "showcase.html": "Showcase"}
            page_title = title_map.get(page)
            if page == 'index.html':
                final_html = template.render(base_url=BASE_URL, site_url=SITE_URL, current_url=current_url, recent_posts=posts[:2], og_type="website")
            elif page == 'showcase.html':
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
                
                # Single pass bucketing
                featured_posts, speaking_posts, writing_posts, event_posts = [], [], [], []
                for p in showcase_posts:
                    if p.get('featured'):
                        featured_posts.append(p)
                    else:
                        cat = p.get('category')
                        if cat == 'speaking': speaking_posts.append(p)
                        elif cat == 'writing': writing_posts.append(p)
                        elif cat == 'event': event_posts.append(p)
                
                final_html = template.render(
                    base_url=BASE_URL, site_url=SITE_URL, current_url=current_url, title=page_title, 
                    featured_posts=featured_posts, speaking_posts=speaking_posts, writing_posts=writing_posts, event_posts=event_posts, og_type="website")
            elif page == 'career.html':
                career_yaml_path = os.path.join(CONTENT_DIR, 'career.yaml')
                career_data = {}
                if os.path.exists(career_yaml_path):
                    with open(career_yaml_path, 'r', encoding='utf-8') as f:
                        career_data = yaml.safe_load(f) or {}
                # Extract out for direct loop access in template
                final_html = template.render(
                    base_url=BASE_URL, site_url=SITE_URL, current_url=current_url, title=page_title, 
                    career_timeline=career_data.get('timeline', []),
                    career_awards=career_data.get('awards', []),
                    career_community=career_data.get('community', []),
                    career_education=career_data.get('education', []),
                    career_certifications=career_data.get('certifications', []),
                    og_type="website")
            else:
                final_html = template.render(base_url=BASE_URL, site_url=SITE_URL, current_url=current_url, title=page_title, og_type="website")
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
