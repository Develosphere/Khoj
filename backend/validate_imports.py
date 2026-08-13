"""
Validation script to check Investigation Engine imports without running FastAPI.
This validates the code structure is correct.
"""

import sys
import ast
from pathlib import Path

def validate_file(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    """Validate all Investigation Engine files."""
    base_dir = Path(__file__).parent
    
    files_to_check = [
        # AI clients
        base_dir / "app" / "ai" / "gemini.py",
        base_dir / "app" / "ai" / "openrouter.py",
        
        # Prompts
        base_dir / "app" / "ai" / "prompts" / "evidence_prompt.py",
        base_dir / "app" / "ai" / "prompts" / "timeline_prompt.py",
        base_dir / "app" / "ai" / "prompts" / "theory_prompt.py",
        base_dir / "app" / "ai" / "prompts" / "summary_prompt.py",
        
        # Services
        base_dir / "app" / "services" / "source_collector.py",
        base_dir / "app" / "services" / "evidence_engine.py",
        base_dir / "app" / "services" / "timeline_engine.py",
        base_dir / "app" / "services" / "theory_engine.py",
        base_dir / "app" / "services" / "summary_engine.py",
        base_dir / "app" / "services" / "investigation_orchestrator.py",
        
        # Models
        base_dir / "app" / "models" / "source.py",
        base_dir / "app" / "models" / "evidence.py",
        base_dir / "app" / "models" / "timeline.py",
        base_dir / "app" / "models" / "theory.py",
        base_dir / "app" / "models" / "summary.py",
        
        # Schemas
        base_dir / "app" / "schemas" / "source.py",
        base_dir / "app" / "schemas" / "evidence.py",
        base_dir / "app" / "schemas" / "timeline.py",
        base_dir / "app" / "schemas" / "theory.py",
        base_dir / "app" / "schemas" / "summary.py",
        
        # API endpoints
        base_dir / "app" / "api" / "v1" / "endpoints" / "source.py",
        base_dir / "app" / "api" / "v1" / "endpoints" / "timeline.py",
        base_dir / "app" / "api" / "v1" / "endpoints" / "theory.py",
        base_dir / "app" / "api" / "v1" / "endpoints" / "summary.py",
        base_dir / "app" / "api" / "v1" / "endpoints" / "investigations.py",
    ]
    
    errors = []
    valid_count = 0
    
    for filepath in files_to_check:
        if not filepath.exists():
            errors.append(f"❌ Missing file: {filepath.relative_to(base_dir)}")
            continue
        
        is_valid, error = validate_file(filepath)
        if is_valid:
            valid_count += 1
            print(f"✓ {filepath.relative_to(base_dir)}")
        else:
            errors.append(f"❌ {filepath.relative_to(base_dir)}: {error}")
    
    print(f"\n{'='*60}")
    print(f"Validation Results: {valid_count}/{len(files_to_check)} files valid")
    print(f"{'='*60}\n")
    
    if errors:
        print("Errors found:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("✅ All Investigation Engine files have valid Python syntax!")
        sys.exit(0)

if __name__ == "__main__":
    main()
