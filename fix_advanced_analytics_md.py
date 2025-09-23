#!/usr/bin/env python3
"""
Fix all markdown linting issues in ADVANCED_ANALYTICS_SUMMARY.md
Addresses all 50 reported markdown linting errors systematically.
"""

import re

def fix_markdown_file(filepath):
    """Fix all markdown linting issues in the specified file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a heading line
        if line.strip().startswith('#'):
            # MD022: Ensure blank line before heading (except first line)
            if i > 0 and fixed_lines and fixed_lines[-1].strip():
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # MD022: Ensure blank line after heading
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith('#'):
                fixed_lines.append('')
        
        # Check if this is a list item
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            # MD032: Ensure blank line before list (if not already in a list)
            if (i > 0 and fixed_lines and fixed_lines[-1].strip() and 
                not fixed_lines[-1].strip().startswith('- ') and 
                not fixed_lines[-1].strip().startswith('* ') and
                not fixed_lines[-1].strip() == ''):
                fixed_lines.append('')
            
            # Add the list item
            fixed_lines.append(line)
            
            # Check for end of list - add blank line after if next line isn't a list item
            if (i + 1 < len(lines) and lines[i + 1].strip() and 
                not lines[i + 1].strip().startswith('- ') and 
                not lines[i + 1].strip().startswith('* ') and
                not lines[i + 1].strip().startswith('#')):
                
                # Look ahead to see if we need to add a blank line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                
                if j < len(lines) and not lines[j].strip().startswith('- ') and not lines[j].strip().startswith('* '):
                    # We're at the end of a list, ensure blank line follows
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        fixed_lines.append('')
        
        # Check for code blocks
        elif line.strip().startswith('```'):
            # MD031: Ensure blank line before code block
            if i > 0 and fixed_lines and fixed_lines[-1].strip():
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Find the closing code block
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                fixed_lines.append(lines[i])
                i += 1
            
            # Add closing code block line
            if i < len(lines):
                fixed_lines.append(lines[i])
            
            # MD031: Ensure blank line after code block
            if i + 1 < len(lines) and lines[i + 1].strip():
                fixed_lines.append('')
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # MD047: Ensure file ends with single newline
    result = '\n'.join(fixed_lines)
    if not result.endswith('\n'):
        result += '\n'
    elif result.endswith('\n\n'):
        # Remove extra newlines, keep only one
        result = result.rstrip('\n') + '\n'
    
    return result

if __name__ == "__main__":
    filepath = "ADVANCED_ANALYTICS_SUMMARY.md"
    
    print(f"🔧 Fixing markdown linting issues in {filepath}...")
    
    try:
        fixed_content = fix_markdown_file(filepath)
        
        # Write the fixed content back
        with open(filepath, 'w') as f:
            f.write(fixed_content)
        
        print("✅ Markdown linting issues fixed!")
        print("📋 Fixed issues:")
        print("   • MD022: Added proper blank lines around headings")
        print("   • MD032: Added proper blank lines around lists") 
        print("   • MD031: Fixed code block formatting")
        print("   • MD047: Ensured single trailing newline")
        
    except Exception as e:
        print(f"❌ Error fixing file: {e}")