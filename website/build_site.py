import os
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
import shutil
from datetime import datetime

# GitHub Pages serves from a subpath (/PersonalWebsite). Local uses root (/).
BASE_URL = '/PersonalWebsite' if os.environ.get('GITHUB_ACTIONS') else ''

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

def build_blog():
    """Convert .md files in content/blog to .html files in public/blog."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    post_template = env.get_template('post.html')
    blog_list_template = env.get_template('blog_list.html')
    
    blog_content_dir = os.path.join(CONTENT_DIR, 'blog')
    if not os.path.exists(blog_content_dir):
        os.makedirs(blog_content_dir)
        
    posts = []

    # Process each markdown file
    for filename in os.listdir(blog_content_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(blog_content_dir, filename)
            
            # Extract frontmatter and content
            post_data = frontmatter.load(filepath)
            
            # Markdown config (fenced code, tables)
            md = markdown.Markdown(extensions=['fenced_code', 'tables', 'codehilite'])
            html_content = md.convert(post_data.content)
            
            out_filename = filename.replace('.md', '.html')
            
            import re
            img_match = re.search(r'<img[^>]+src="([^">]+)"', html_content)
            thumbnail = img_match.group(1).replace('{{ base_url }}', BASE_URL) if img_match else ''

            # Approximate reading time: 200 words per minute
            word_count = len(re.sub(r'<[^>]+>', '', html_content).split())
            read_time = max(1, word_count // 200)

            # Store post metadata for the index page
            post_meta = {
                'title': post_data.get('title', 'Untitled'),
                'date': post_data.get('date', datetime.now().strftime("%Y-%m-%d")),
                'summary': post_data.get('summary', ''),
                'thumbnail': thumbnail,
                'read_time': read_time,
                'url': f'{BASE_URL}/blog/{out_filename}',
                'content': html_content.replace('{{ base_url }}', BASE_URL)
            }
            posts.append(post_meta)
            
            # Render individual post
            final_html = post_template.render(**post_meta, base_url=BASE_URL)
            
            # Save output
            output_dir = os.path.join(PUBLIC_DIR, 'blog')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(os.path.join(output_dir, out_filename), 'w', encoding='utf-8') as f:
                f.write(final_html)

    # Output the blog index page
    # Sort posts by date descending
    posts.sort(key=lambda x: x['date'], reverse=True)
    blog_index_html = blog_list_template.render(title="Blog", posts=posts, base_url=BASE_URL)
    with open(os.path.join(PUBLIC_DIR, 'blog.html'), 'w', encoding='utf-8') as f:
        f.write(blog_index_html)
        
    return posts

def build_pages(posts=[]):
    """Build root-level pages (Home, About, Contact)."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    
    pages = ['index.html', 'advisory.html', 'career.html', 'contact.html']
    
    for page in pages:
        try:
            template = env.get_template(page)
            if page == 'index.html':
                final_html = template.render(base_url=BASE_URL, recent_posts=posts[:2])
            else:
                final_html = template.render(base_url=BASE_URL)
            with open(os.path.join(PUBLIC_DIR, page), 'w', encoding='utf-8') as f:
                f.write(final_html)
        except Exception as e:
            print(f"Skipping {page}, template not found yet.")

if __name__ == "__main__":
    print("Building static site for Harry McLaren...")
    setup_public_dir()
    posts = build_blog()
    build_pages(posts)
    print("Site built successfully in the /public directory!")
