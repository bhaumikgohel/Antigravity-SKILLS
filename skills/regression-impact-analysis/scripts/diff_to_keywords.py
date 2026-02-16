import sys
import re

def parse_git_diff_to_modules(diff_text):
    """
    Extracts module names or file paths from a standard git diff.
    Useful for mapping code changes to test modules.
    """
    # Look for lines starting with '+++ b/' which indicate the new file path
    module_pattern = re.compile(r'^\+\+\+ b/(.*)$', re.MULTILINE)
    matches = module_pattern.findall(diff_text)
    
    modules = set()
    for match in matches:
        # Get the first two directory parts as the 'module'
        parts = match.split('/')
        if len(parts) > 1:
            modules.add(f"{parts[0]}/{parts[1]}")
        else:
            modules.add(parts[0])
            
    return sorted(list(modules))

if __name__ == "__main__":
    test_diff = """
    --- a/src/auth/login.py
    +++ b/src/auth/login.py
    @@ -10,3 +10,4 @@
    """
    print(f"Impacted Modules/Paths: {parse_git_diff_to_modules(test_diff)}")
