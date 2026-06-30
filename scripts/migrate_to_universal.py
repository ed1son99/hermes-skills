#!/usr/bin/env python3
"""
migrate_to_universal.py — Migrate all SKILL.md files to universal cross-platform format.

Unified structure:
  skills/<category>/<name>/
  ├── SKILL.md              # Universal: name, description, triggers, platforms
  ├── mounts/
  │   ├── claude-code.yaml  # { category }
  │   ├── hermes.yaml       # { version, author, license, platforms, tags, ... }
  │   └── codex.yaml        # { interface, policy }
  ├── scripts/              # (unchanged)
  ├── references/           # (unchanged)
  └── templates/            # (unchanged)

Usage:
  python3 scripts/migrate_to_universal.py --dry-run     # Preview only
  python3 scripts/migrate_to_universal.py               # Execute migration
  python3 scripts/migrate_to_universal.py --verify      # Verify results
"""

import os
import re
import sys
import shutil
import shlex
from pathlib import Path
from collections import defaultdict
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
BACKUP_DIR = REPO_ROOT / ".migration_backup"

# ── Utility ──────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text. Returns (frontmatter_dict, body)."""
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    fm_text = parts[1].strip()
    body = parts[2].strip()
    fm = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            fm[key] = val
    return fm, body


def parse_frontmatter_full(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter with list support using simple heuristics."""
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    fm_text = parts[1].strip()
    body = parts[2].strip()
    fm = {}
    current_key = None
    current_list = []
    in_metadata = False
    metadata_path = []
    metadata = {}

    for line in fm_text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Check for metadata.hermes nesting via indentation
        if stripped.startswith('metadata:'):
            in_metadata = True
            continue
        if in_metadata and stripped.startswith('hermes:'):
            metadata_path = ['hermes']
            continue
        if in_metadata and metadata_path and stripped.startswith('  '):
            inner = stripped.strip()
            if ':' in inner and not inner.startswith('-'):
                k, _, v = inner.partition(':')
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k in ('tags', 'related_skills', 'related_docs'):
                    # Parse inline list [a, b, c]
                    fm[f'_hermes_{k}'] = parse_inline_list(v)
                else:
                    fm[f'_hermes_{k}'] = v
            continue

        # Check for prerequisites nesting
        if stripped.startswith('prerequisites:'):
            current_key = 'prerequisites'
            fm[current_key] = {}
            continue
        if current_key == 'prerequisites' and stripped.startswith('  '):
            inner = stripped.strip()
            if ':' in inner and not inner.startswith('-'):
                k, _, v = inner.partition(':')
                k = k.strip()
                v = v.strip()
                if v.startswith('['):
                    fm['prerequisites'][k] = parse_inline_list(v)
                else:
                    fm['prerequisites'][k] = v.strip('"').strip("'")
            continue
        else:
            current_key = None

        # Regular key: value
        if ':' in stripped:
            key, _, val = stripped.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith('[') and val.endswith(']'):
                fm[key] = parse_inline_list(val)
            else:
                fm[key] = val

    return fm, body


def parse_inline_list(val: str) -> list:
    """Parse [a, b, c] or [a,b,c] into a Python list."""
    val = val.strip('[]').strip()
    if not val:
        return []
    items = []
    for item in val.split(','):
        item = item.strip().strip('"').strip("'")
        if item:
            items.append(item)
    return items


def fmt_list(lst: list) -> str:
    """Format a Python list as YAML inline list [a, b, c]."""
    if not lst:
        return '[]'
    return '[' + ', '.join(lst) + ']'


def classify_frontmatter(fm: dict) -> str:
    """Classify the frontmatter format."""
    has_category = 'category' in fm
    has_triggers = 'triggers' in fm
    has_version = 'version' in fm
    has_author = 'author' in fm
    has_license = 'license' in fm
    has_platforms = 'platforms' in fm
    has_metadata = 'metadata' in fm or '_hermes_tags' in fm
    has_tags_toplevel = 'tags' in fm
    has_user_invocable = 'user-invocable' in fm

    if has_category and has_triggers:
        return 'claude-code'
    if has_version and has_author and has_license and has_platforms:
        return 'hermes-full'
    if has_version and has_metadata:
        return 'hermes-variant'
    if has_version and has_platforms and not has_metadata:
        return 'hermes-variant'
    if has_user_invocable:
        return 'user-invocable'
    if has_tags_toplevel and has_platforms:
        return 'hybrid-tags'
    if has_platforms and not has_version and not has_category:
        return 'platforms-only'
    if has_license and has_platforms:
        return 'hermes-variant'
    if len(fm) <= 2:
        return 'minimal'
    return 'hybrid'


# ── Trigger Synthesis ─────────────────────────────────────────────────

def synthesize_triggers(name: str, description: str, tags: list = None, existing_triggers: list = None) -> list:
    """Generate trigger keywords for skills that don't have explicit triggers."""
    if existing_triggers and len(existing_triggers) > 0:
        return existing_triggers[:15]

    triggers = []
    if tags is None:
        tags = []

    # 1. Skill name
    triggers.append(name)

    # 2. Tags
    for tag in tags:
        t = tag.strip().lower()
        if t not in triggers:
            triggers.append(t)

    # 3. Chinese keywords (2-4 char segments)
    chinese = re.findall(r'[一-鿿]{2,4}', description)
    for c in chinese[:6]:
        if c not in triggers:
            triggers.append(c)

    # 4. Capitalized English terms (tech names)
    eng = re.findall(r'\b[A-Z][a-zA-Z0-9]+(?:[ -][A-Z][a-zA-Z0-9]+)*\b', description)
    for e in eng[:4]:
        el = e.lower()
        if el not in triggers:
            triggers.append(el)

    # 5. Quoted text
    quoted = re.findall(r'[\"\'""]([^\"\'""]+)[\"\'""]', description)
    for q in quoted[:3]:
        ql = q.lower().strip()
        if ql not in triggers and len(ql) >= 2:
            triggers.append(ql)

    # Deduplicate, clean, limit
    seen = set()
    result = []
    for t in triggers:
        t = t.strip().rstrip(',.')
        if t and t not in seen and len(t) >= 2 and len(t) <= 80:
            seen.add(t)
            result.append(t)

    return result[:15]


# ── Format Migration ──────────────────────────────────────────────────

def migrate_skill(skill_path: Path, category: str, dry_run: bool = False) -> dict:
    """Migrate a single SKILL.md to universal format. Returns change report."""
    with open(skill_path, 'r') as f:
        content = f.read()

    fm, body = parse_frontmatter_full(content)
    fmt = classify_frontmatter(fm)

    skill_name = fm.get('name', '')
    skill_desc = fm.get('description', '')

    # ── Extract fields per source format ──
    # triggers
    if fmt == 'claude-code':
        triggers = fm.get('triggers', [])
        if isinstance(triggers, str):
            triggers = parse_inline_list(triggers)
    elif fmt in ('hermes-full', 'hermes-variant'):
        tags = fm.get('_hermes_tags', []) if '_hermes_tags' in fm else fm.get('tags', [])
        triggers = synthesize_triggers(skill_name, skill_desc, tags)
    elif fmt == 'hybrid-tags':
        tags = fm.get('tags', [])
        existing = fm.get('triggers', [])
        if isinstance(existing, str):
            existing = parse_inline_list(existing)
        triggers = synthesize_triggers(skill_name, skill_desc, tags, existing)
    else:
        triggers = synthesize_triggers(skill_name, skill_desc)

    # claude-code category
    cc_category = fm.get('category', category)

    # hermes fields
    h_version = fm.get('version', '1.0.0')
    h_author = fm.get('author', 'Hermes Agent')
    h_license = fm.get('license', 'MIT')
    h_platforms = fm.get('platforms', ['linux', 'macos', 'windows'])
    if isinstance(h_platforms, str):
        h_platforms = parse_inline_list(h_platforms)

    # hermes tags
    h_tags = fm.get('_hermes_tags', [])
    if not h_tags:
        h_tags = fm.get('tags', [])
    if isinstance(h_tags, str):
        h_tags = parse_inline_list(h_tags) if h_tags else []

    # hermes related_skills
    h_related = fm.get('_hermes_related_skills', [])
    if isinstance(h_related, str):
        h_related = parse_inline_list(h_related) if h_related else []

    h_homepage = fm.get('_hermes_homepage', fm.get('homepage', ''))

    # hermes prerequisites
    h_prereqs = fm.get('prerequisites', None)

    # codex fields
    codex_display_name = fm.get('display_name', skill_name)
    codex_short_desc = fm.get('short_description', skill_desc)
    codex_default_prompt = f"Use ${skill_name} to help with {skill_name.replace('-', ' ')} tasks."
    codex_allow_implicit = fm.get('user-invocable', 'true')
    if codex_allow_implicit == 'true':
        codex_allow_implicit = True
    elif codex_allow_implicit == 'false':
        codex_allow_implicit = False
    else:
        codex_allow_implicit = True

    # ── Read existing agents/openai.yaml if present ──
    agents_dir = skill_path.parent / "agents"
    openai_yaml = agents_dir / "openai.yaml"
    if openai_yaml.exists():
        try:
            with open(openai_yaml, 'r') as f:
                oa_content = f.read()
            oa_fm, _ = parse_frontmatter_full('---\n' + oa_content + '\n---')
            if 'interface' in oa_content:
                # Parse manually for nested structure
                for line in oa_content.split('\n'):
                    line = line.strip()
                    if line.startswith('display_name:'):
                        codex_display_name = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('short_description:'):
                        codex_short_desc = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('default_prompt:'):
                        codex_default_prompt = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('allow_implicit_invocation:'):
                        val = line.split(':', 1)[1].strip()
                        codex_allow_implicit = val == 'true'
        except Exception:
            pass

    # ── Build output ──
    # SKILL.md
    skill_md = f"""---
name: {skill_name}
description: {skill_desc}
triggers: {fmt_list(triggers)}
platforms: [claude-code, hermes, codex]
---

{body}
"""

    # mounts/claude-code.yaml
    cc_yaml = f"category: {cc_category}\n"

    # mounts/hermes.yaml
    h_lines = [
        f'version: "{h_version}"',
        f'author: {h_author}',
        f'license: {h_license}',
        f'platforms: {fmt_list(h_platforms)}',
        f'tags: {fmt_list(h_tags)}',
    ]
    if h_related:
        h_lines.append(f'related_skills: {fmt_list(h_related)}')
    if h_homepage:
        h_lines.append(f'homepage: {h_homepage}')
    if h_prereqs:
        h_lines.append('prerequisites:')
        for pk, pv in h_prereqs.items():
            if isinstance(pv, list):
                h_lines.append(f'  {pk}: {fmt_list(pv)}')
            else:
                h_lines.append(f'  {pk}: {pv}')
    hermes_yaml = '\n'.join(h_lines) + '\n'

    # mounts/codex.yaml
    codex_yaml = f"""interface:
  display_name: "{codex_display_name}"
  short_description: "{codex_short_desc}"
  default_prompt: "{codex_default_prompt}"
policy:
  allow_implicit_invocation: {str(codex_allow_implicit).lower()}
"""

    if dry_run:
        return {
            'path': str(skill_path),
            'format': fmt,
            'name': skill_name,
            'triggers': triggers,
            'changed': True,
        }

    # ── Write files ──
    skill_dir = skill_path.parent
    mounts_dir = skill_dir / "mounts"
    mounts_dir.mkdir(parents=True, exist_ok=True)

    with open(skill_path, 'w') as f:
        f.write(skill_md)

    with open(mounts_dir / "claude-code.yaml", 'w') as f:
        f.write(cc_yaml)

    with open(mounts_dir / "hermes.yaml", 'w') as f:
        f.write(hermes_yaml)

    with open(mounts_dir / "codex.yaml", 'w') as f:
        f.write(codex_yaml)

    # Remove agents/ directory if present
    if agents_dir.exists():
        shutil.rmtree(agents_dir)

    return {
        'path': str(skill_path),
        'format': fmt,
        'name': skill_name,
        'triggers': triggers,
        'changed': True,
    }


# ── Directory Normalization ───────────────────────────────────────────

def normalize_dogfood_yuanbao():
    """Move dogfood/SKILL.md and yuanbao/SKILL.md into subdirectories."""
    for cat in ['dogfood', 'yuanbao']:
        cat_dir = SKILLS_DIR / cat
        skill_md = cat_dir / 'SKILL.md'
        if skill_md.exists():
            target_dir = cat_dir / cat
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / 'SKILL.md'
            shutil.copy2(skill_md, target_path)
            skill_md.unlink()
            print(f"  Normalized: {skill_md} -> {target_path}")


def flatten_mlops():
    """Flatten mlops subcategories (models, inference, evaluation)."""
    subcats = ['models', 'inference', 'evaluation']
    for subcat in subcats:
        subcat_dir = SKILLS_DIR / 'mlops' / subcat
        if not subcat_dir.exists():
            continue
        for skill_dir in subcat_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / 'SKILL.md'
            if not skill_md.exists():
                continue
            with open(skill_md, 'r') as f:
                content = f.read()
            fm, _ = parse_frontmatter_full(content)
            skill_name = fm.get('name', skill_dir.name)
            # Get original tags
            tags = fm.get('_hermes_tags', fm.get('tags', []))
            if isinstance(tags, str):
                tags = parse_inline_list(tags) if tags else []
            # Prepend subcategory as tag
            subcat_tag = subcat.capitalize() if subcat != 'evaluation' else 'Evaluation'
            if subcat_tag not in tags:
                tags.insert(0, subcat_tag)
            # Write updated frontmatter
            new_fm = dict(fm)
            new_fm['_hermes_tags'] = tags
            # Move to flat location
            target_dir = SKILLS_DIR / 'mlops' / skill_name
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(skill_dir, target_dir)
            # Update SKILL.md with tags preserved
            target_md = target_dir / 'SKILL.md'
            with open(target_md, 'r') as f:
                tgt_content = f.read()
            _, tgt_body = parse_frontmatter_full(tgt_content)
            # We'll let the main migration handle the final format
            print(f"  Flattened: {skill_dir} -> {target_dir}")
        # Remove subcategory directory
        if subcat_dir.exists():
            shutil.rmtree(subcat_dir)
            print(f"  Removed subcat dir: {subcat_dir}")


# ── DESCRIPTION.md Standardization ────────────────────────────────────

def standardize_description_md(category_dir: Path):
    """Ensure DESCRIPTION.md uses standard frontmatter format."""
    desc_path = category_dir / 'DESCRIPTION.md'
    if not desc_path.exists():
        # Generate one
        cat_name = category_dir.name
        desc_content = f'---\ndescription: "Skills for {cat_name} category"\n---\n'
        desc_path.write_text(desc_content)
        return

    content = desc_path.read_text()
    if content.startswith('---'):
        return  # Already frontmatter format

    # Convert markdown list format to frontmatter
    cat_name = category_dir.name
    # Try to extract description from existing content
    first_line = content.strip().split('\n')[0].lstrip('#').strip()
    if first_line:
        desc = first_line
    else:
        desc = f"Skills for {cat_name} category"

    new_content = f'---\ndescription: "{desc}"\n---\n'
    desc_path.write_text(new_content)


# ── Main ──────────────────────────────────────────────────────────────

def discover_skills() -> list[Path]:
    """Find all SKILL.md files in skills/ directory."""
    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if '.git' in root or 'node_modules' in root:
            continue
        if 'SKILL.md' in files:
            skills.append(Path(root) / 'SKILL.md')
    return sorted(skills)


def run_migration(dry_run: bool = False):
    """Execute the full migration."""
    # Step 0: Backup
    if not dry_run:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = BACKUP_DIR / f"skills-{timestamp}"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Backing up to {backup_path}...")
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(SKILLS_DIR, backup_path)

    # Step 1: Normalize directory structure
    print("\n=== Step 1: Normalize directory structure ===")
    if not dry_run:
        normalize_dogfood_yuanbao()
        flatten_mlops()
    else:
        print("  (would normalize dogfood, yuanbao, mlops subcategories)")

    # Step 2: Discover skills
    print("\n=== Step 2: Discover skills ===")
    skills = discover_skills()
    print(f"  Found {len(skills)} SKILL.md files")

    # Step 3: Migrate each skill
    print("\n=== Step 3: Migrate skills ===")
    stats = defaultdict(int)
    reports = []

    for skill_path in skills:
        rel_path = skill_path.relative_to(SKILLS_DIR)
        category = rel_path.parts[0]
        report = migrate_skill(skill_path, category, dry_run=dry_run)
        stats[report['format']] += 1
        reports.append(report)

    # Print summary
    print(f"\n=== Summary ===")
    print(f"  Total skills: {len(reports)}")
    print(f"  By format:")
    for fmt, count in sorted(stats.items()):
        print(f"    {fmt}: {count}")

    if dry_run:
        print("\n  [DRY RUN] No files were modified.")
        # Show a few samples
        print("\n  Sample triggers (first 5):")
        for r in reports[:5]:
            print(f"    {r['name']} ({r['format']}): {r['triggers'][:5]}...")

    # Step 4: Standardize DESCRIPTION.md
    print("\n=== Step 4: Standardize DESCRIPTION.md ===")
    if not dry_run:
        for cat_dir in sorted(SKILLS_DIR.iterdir()):
            if cat_dir.is_dir():
                standardize_description_md(cat_dir)
        print(f"  Standardized {len(list(SKILLS_DIR.iterdir()))} DESCRIPTION.md files")
    else:
        print("  (would standardize DESCRIPTION.md files)")

    return reports


def verify_migration():
    """Verify all migrated skills."""
    print("\n=== Verification ===")
    errors = []

    skills = discover_skills()
    print(f"  SKILL.md count: {len(skills)} (expected 222)")

    # Check each skill
    mounts_count = {k: 0 for k in ['claude-code', 'hermes', 'codex']}
    agents_count = 0
    frontmatter_ok = 0

    for skill_path in skills:
        skill_dir = skill_path.parent
        mounts_dir = skill_dir / 'mounts'

        # Check mounts
        for k in mounts_count:
            mount_file = mounts_dir / f'{k}.yaml'
            if mount_file.exists():
                mounts_count[k] += 1
            else:
                errors.append(f"Missing mount: {mount_file}")

        # Check agents/ gone
        agents_dir = skill_dir / 'agents'
        if agents_dir.exists():
            agents_count += 1
            errors.append(f"agents/ still exists: {agents_dir}")

        # Check frontmatter
        with open(skill_path, 'r') as f:
            content = f.read()
        fm, _ = parse_frontmatter_full(content)
        required = ['name', 'description', 'triggers', 'platforms']
        for field in required:
            if field not in fm:
                errors.append(f"Missing field '{field}' in {skill_path}")
        if all(f in fm for f in required):
            frontmatter_ok += 1

    print(f"  claude-code.yaml mounts: {mounts_count['claude-code']}")
    print(f"  hermes.yaml mounts: {mounts_count['hermes']}")
    print(f"  codex.yaml mounts: {mounts_count['codex']}")
    print(f"  Frontmatter OK: {frontmatter_ok}/{len(skills)}")
    print(f"  agents/ directories remaining: {agents_count}")
    print(f"  Errors: {len(errors)}")

    if errors[:10]:
        print("\n  First 10 errors:")
        for e in errors[:10]:
            print(f"    - {e}")

    return len(errors) == 0


if __name__ == '__main__':
    if '--verify' in sys.argv:
        verify_migration()
    elif '--dry-run' in sys.argv:
        run_migration(dry_run=True)
    else:
        run_migration(dry_run=False)
        verify_migration()
