#!/usr/bin/env python3
"""
🔧 PATTERN ANALYTICS CLEANUP SCRIPT (Conservative)
Fixes specific formatting issues without breaking functionality
"""

import re
import os

def fix_pattern_analytics():
    """Conservative fix for pattern_analytics.py formatting"""
    file_path = "/Users/johnbozza/Library/Mobile Documents/com~apple~CloudDocs/Benson Bot/pattern_analytics.py"
    
    print("🔧 Starting conservative pattern_analytics.py cleanup...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"  📊 Processing {len(lines)} lines...")
    
    fixed_lines = []
    changes_count = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # 1. Fix trailing whitespace (W291) - remove trailing spaces/tabs
        line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
        
        # 2. Fix blank lines with whitespace (W293) - empty lines should be completely empty
        if line.strip() == '' and len(line.rstrip()) > 0:
            line = '\n' if line.endswith('\n') else ''
        
        # 3. Fix f-strings missing placeholders (F541) - convert to regular strings
        if 'f"' in line and '{' not in line:
            line = line.replace('f"', '"')
        if "f'" in line and '{' not in line:
            line = line.replace("f'", "'")
        
        # 4. Fix bare except statements (E722)
        if line.strip() == 'except:':
            line = line.replace('except:', 'except Exception:')
        
        # Track changes
        if line != original_line:
            changes_count += 1
        
        fixed_lines.append(line)
    
    # 5. Ensure file ends with newline (W292)
    if fixed_lines and not fixed_lines[-1].endswith('\n'):
        fixed_lines[-1] += '\n'
        changes_count += 1
    
    # Write the fixed content
    print(f"  💾 Writing fixes ({changes_count} lines modified)...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"  ✅ Conservative cleanup completed!")
    print(f"  🎯 Modified {changes_count} lines")
    
    return True

if __name__ == "__main__":
    try:
        success = fix_pattern_analytics()
        print("\n🏆 CONSERVATIVE CLEANUP COMPLETED!")
        print("✨ Fixed trailing whitespace, blank line whitespace, f-strings, and bare except")
        print("🔍 Run flake8 again to check remaining issues")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        print("💡 Manual fixes may be required")