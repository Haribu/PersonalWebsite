import sys
import hashlib
import base64

# Compiled Regex for HTML parsing (Synced with build_site.py)
SCRIPT_REGEX = re.compile(r'<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)
CSP_META_REGEX = re.compile(r'<meta[^>]+http-equiv=["\']Content-Security-Policy["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE)

# Define paths
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
PUBLIC_DIR = os.path.join(ROOT_DIR, 'website', 'public')

def get_html_files(directory):
    """Recursively fetch all .html files generated in the public folder."""
    html_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def verify_file(filepath):
    """Read an HTML file, compute the sha256 of inline scripts, and check if it exists in the CSP."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract Content-Security-Policy meta tag
    csp_match = CSP_META_REGEX.search(html)

    # If no CSP is strictly enforced, we skip (Though ideally every page has one)
    if not csp_match:
        return True

    csp_content = csp_match.group(1)
    
    # Extract script-src directive
    script_src_match = re.search(r'script-src\s+([^;]+)', csp_content)
    if not script_src_match:
        return True

    script_src = script_src_match.group(1)

    # Find all inline scripts using shared regex pattern
    inline_scripts = SCRIPT_REGEX.findall(html)

    passes = True
    for idx, script_content in enumerate(inline_scripts):
        # Javascript engine whitespace matters. Hash the exact innerHTML content block.
        sha256_hash = hashlib.sha256(script_content.encode('utf-8')).digest()
        base64_hash = base64.b64encode(sha256_hash).decode('utf-8')
        csp_hash_string = f"'sha256-{base64_hash}'"

        if csp_hash_string not in script_src:
            print(f"[ERROR] {os.path.basename(filepath)} - Inline script #{idx+1} violation!")
            print(f"        Computed Hash: {csp_hash_string}")
            passes = False
            
    return passes

def main():
    if not os.path.exists(PUBLIC_DIR):
        print(f"[ERROR] Public directory not found at {PUBLIC_DIR}. Ensure build_site.py executed properly.")
        sys.exit(1)

    html_files = get_html_files(PUBLIC_DIR)
    
    if not html_files:
        print("[WARNING] No HTML files found to inspect.")
        sys.exit(0)

    print(f"🔒 Starting CSP Hash Verification across {len(html_files)} static targets...")
    
    all_passed = True
    for filepath in html_files:
        if not verify_file(filepath):
            all_passed = False
            
    if all_passed:
        print("[SUCCESS] Content-Security-Policy verification complete. 0 Vulnerabilities detected.")
        sys.exit(0)
    else:
        print("[FATAL] CSP Verification Failed! Aborting server build deployment immediately.")
        sys.exit(1)

if __name__ == '__main__':
    main()
