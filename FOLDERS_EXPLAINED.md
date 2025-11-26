# Project Folders Explained

## Core Project Folders (Keep These)

### `/ingestion/`
**Purpose:** Data ingestion from RAWG API to MinIO
- Fetches game data from RAWG API
- Tracks processed games with CDC (Change Data Capture)
- Saves as parquet files and uploads to MinIO

### `/storage/`
**Purpose:** MinIO storage operations
- S3-compatible client wrapper
- Upload/download parquet files
- List and read data from MinIO

### `/etl/`
**Purpose:** ETL transformations (MinIO → Iceberg)
- Build dimension tables
- Build bridge tables (many-to-many relationships)
- Build fact table
- Write to Iceberg warehouse

### `/utils/`
**Purpose:** Shared utilities and configuration
- Configuration management
- Service health checks
- Common helper functions

### `/tests/`
**Purpose:** Test suite
- Unit tests for ETL components
- Integration tests (future)
- Test fixtures and utilities

---

## Data Folders (Gitignored)

### `/data/`
**Purpose:** Local data storage
**Contains:**
- `rawg_games/` - Downloaded parquet files
- `cdc_state.json` - CDC tracking state
**Should be in git?** NO - data files are large and change frequently

---

## Cache/Config Folders (Gitignored)

### `.vscode/`
**Purpose:** VS Code editor configuration
**Created by:** Visual Studio Code IDE
**Contains:** 
- `settings.json` - Editor preferences
- `launch.json` - Debug configurations (if any)
- `extensions.json` - Recommended extensions (if any)

**Should be in git?** 
- ❌ **NO** for personal settings (theme, font size, etc.)
- ✅ **YES** for project-specific settings (Python path, linting rules)
- **Current status:** Contains only Kiro-specific config, safe to ignore

### `.pytest_cache/`
**Purpose:** pytest test runner cache
**Created by:** pytest when running tests
**Contains:**
- Test results cache
- Node IDs for test collection
- Plugin data

**Should be in git?** ❌ **NO** - temporary cache, regenerated on each test run

### `.kiro/`
**Purpose:** Kiro IDE configuration
**Created by:** Kiro IDE
**Contains:** IDE-specific settings and specs
**Should be in git?** Depends on team preference

### `__pycache__/`
**Purpose:** Python bytecode cache
**Created by:** Python interpreter
**Contains:** Compiled `.pyc` files
**Should be in git?** ❌ **NO** - automatically regenerated

---

## Recommendation

### Keep in Git ✅
```
/ingestion/
/storage/
/etl/
/utils/
/tests/
README.md
requirements.txt
.env.example
.gitignore
```

### Ignore in Git ❌
```
.vscode/          # Editor config
.pytest_cache/    # Test cache
__pycache__/      # Python cache
data/             # Data files
.env              # Secrets
*.pyc             # Compiled Python
```

### Optional (Team Decision)
```
.kiro/            # Kiro IDE config
```

---

## Clean Up Commands

If you want to remove cache folders:

```bash
# Remove pytest cache
rm -rf .pytest_cache

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove VS Code settings (if not needed)
rm -rf .vscode
```

Or on Windows:
```powershell
# Remove pytest cache
Remove-Item -Recurse -Force .pytest_cache

# Remove Python cache
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force

# Remove VS Code settings (if not needed)
Remove-Item -Recurse -Force .vscode
```

---

## Current Status

Your `.gitignore` already excludes these folders, so they won't be committed to git. They're safe to keep locally (they'll be regenerated as needed) or delete (they'll be recreated when you use the tools).

**Bottom line:** These are just cache/config folders created by your tools. They're already gitignored and won't clutter your repository. You can safely delete them anytime - they'll regenerate when needed.
