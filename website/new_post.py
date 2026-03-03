import os
import argparse
from datetime import datetime

# Path to the blog content directory
BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', 'blog')

def create_post(title, summary):
    """Generates a new Markdown file with the required frontmatter."""
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)
        
    # Generate a URL-friendly filename slug
    slug = "".join(c if c.isalnum() else "-" for c in title.lower())
    # Remove consecutive hyphens
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-") + '.md'
    
    filepath = os.path.join(BLOG_DIR, slug)
    
    if os.path.exists(filepath):
        print(f"Error: A post with the filename '{slug}' already exists.")
        return
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    frontmatter = f"""---
title: "{title}"
date: "{date_str}"
summary: "{summary}"
---

Write your post content here!
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        
    print(f"Success! Created new blog post draft at: {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new markdown blog post with frontmatter.")
    parser.add_argument("title", help="The title of the new blog post")
    parser.add_argument("--summary", "-s", default="A short summary of this post.", help="A 1-2 sentence description for the blog list page.")
    
    args = parser.parse_args()
    create_post(args.title, args.summary)
