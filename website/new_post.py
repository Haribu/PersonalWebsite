import os
import argparse
import re
from datetime import datetime

# Path to the blog content directory
BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', 'blog')

def create_post(title, summary, category=None, external_link=None, featured=False):
    """Generates a new blog post folder with index.md and a placeholder for header.png."""
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)
        
    # Generate a URL-friendly slug using regex for performance
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    post_dir = os.path.join(BLOG_DIR, slug)
    filepath = os.path.join(post_dir, 'index.md')

    if os.path.exists(post_dir):
        print(f"Error: A post folder '{slug}/' already exists.")
        return
    
    os.makedirs(post_dir)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    frontmatter = f"""---
title: "{title}"
date: "{date_str}"
summary: "{summary}"
"""
    if category:
        frontmatter += f"category: \"{category}\"\n"
    if external_link:
        frontmatter += f"external_link: \"{external_link}\"\n"
    if featured:
        frontmatter += f"featured: true\n"
    
    frontmatter += """---

![Post header image](./header.png)

Write your post content here!
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        
    print(f"Success! Created new blog post at: {post_dir}/")
    print(f"  - Add your header image as: {post_dir}/header.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new folder-based blog post.")
    parser.add_argument("title", help="The title of the new blog post")
    parser.add_argument("--summary", "-s", default="A short summary of this post.", help="A 1-2 sentence description for the blog list page.")
    parser.add_argument("--category", "-c", default=None, help="Optional category (e.g., speaking, writing, event)")
    parser.add_argument("--external_link", "-l", default=None, help="Optional external link URL")
    parser.add_argument("--featured", "-f", action="store_true", help="Flag to feature this post in the showcase")
    
    args = parser.parse_args()
    create_post(args.title, args.summary, args.category, args.external_link, args.featured)
