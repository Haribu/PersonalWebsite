import os
import glob
import yaml
import frontmatter

# Define paths
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.join(SITE_DIR, 'content', 'blog')
SHOWCASE_YML = os.path.join(SITE_DIR, 'content', 'showcase.yaml')

SHOWCASE_CATEGORIES = ['speaking', 'writing', 'event']

def migrate():
    showcase_items = []
    files_to_delete = []

    for filepath in glob.glob(os.path.join(BLOG_DIR, '*.md')):
        try:
            post_data = frontmatter.load(filepath)
            category = post_data.get('category')
            
            if category in SHOWCASE_CATEGORIES:
                item = {
                    'title': post_data.get('title', 'Untitled'),
                    'date': post_data.get('date', ''),
                    'summary': post_data.get('summary', ''),
                    'category': category,
                    'external_link': post_data.get('external_link', ''),
                    'featured': post_data.get('featured', False),
                    'content': post_data.content.strip() if post_data.content else ''
                }
                
                # Filter out empty keys to keep YAML clean
                item = {k: v for k, v in item.items() if v != ''}
                
                showcase_items.append(item)
                files_to_delete.append(filepath)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    # Sort items by date descending
    showcase_items.sort(key=lambda x: x.get('date', ''), reverse=True)

    # Write to YAML
    with open(SHOWCASE_YML, 'w', encoding='utf-8') as f:
        yaml.dump(showcase_items, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"Migrated {len(showcase_items)} showcase items to {SHOWCASE_YML}")

    # Delete migrated files
    for filepath in files_to_delete:
        os.remove(filepath)
    
    print(f"Deleted {len(files_to_delete)} markdown files from content/blog/")

if __name__ == "__main__":
    migrate()
