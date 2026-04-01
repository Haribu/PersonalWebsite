import os
import yaml
import sys
import re

# Define paths
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
CONTENT_DIR = os.path.join(ROOT_DIR, 'website', 'content')

def lint_yaml_file(filepath):
    """Try to load a YAML file and report errors."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as exc:
        error_msg = f"[YAML ERROR] {os.path.relpath(filepath, ROOT_DIR)}: "
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            error_msg += f"Error at line {mark.line + 1}, column {mark.column + 1}: {exc.problem}"
            if hasattr(exc, 'context'):
                 error_msg += f" (Context: {exc.context})"
        else:
            error_msg += str(exc)
        return False, error_msg

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"[ERROR] Content directory not found at {CONTENT_DIR}")
        sys.exit(1)

    yaml_files = []
    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                yaml_files.append(os.path.join(root, file))

    if not yaml_files:
        print("[WARNING] No YAML content files found to lint.")
        sys.exit(0)

    print(f"🔍 Linting {len(yaml_files)} content files...")
    
    errors = []
    for filepath in yaml_files:
        success, error = lint_yaml_file(filepath)
        if not success:
            errors.append(error)

    if errors:
        print("\n--- Linting Failures ---")
        for error in errors:
            print(error)
        print("\n[FATAL] Content linting failed. Please fix the YAML errors before building.")
        sys.exit(1)
    else:
        print("[SUCCESS] All content files passed YAML validation.")
        sys.exit(0)

if __name__ == '__main__':
    main()
