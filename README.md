# Titan_Lite
Lightweight/portable clinical note assistant

## 🔦 Code Quality & Console Error Monitoring

This repository uses automated Lighthouse audits to maintain high code quality and HIPAA compliance. Console errors are automatically detected, classified, and either fixed or reported for investigation.

### Key Features

- ✅ **Automated console error detection** via Lighthouse
- 🔧 **Auto-fix simple issues** (console.log removal, null checks, error boundaries)
- 📝 **GitHub issues created** for complex problems
- 🏥 **HIPAA compliance checks** to prevent PHI exposure in logs
- 📊 **PR-level reporting** with detailed analysis

### Documentation

- [Lighthouse Console Audit System](./docs/LIGHTHOUSE_CONSOLE_AUDIT.md) - Complete documentation
- [Issue Template](/.github/ISSUE_TEMPLATE/lighthouse-console-error.md) - For manual error reporting

### How It Works

Every PR is automatically audited for console errors:

1. **Lighthouse runs** against PR preview deployment
2. **Errors are classified**:
   - Category A: Auto-fixed and committed
   - Category B: GitHub issues created for investigation
3. **PR is updated** with comprehensive analysis
4. **HIPAA compliance verified** - no PHI exposure

See [workflow configuration](./.github/workflows/lighthouse-console-audit.yml) for details.

### For Developers

**Best Practices:**
- Remove `console.log` statements before committing
- Handle errors gracefully with try-catch blocks
- Never log Protected Health Information (PHI)
- Review Lighthouse PR comments before merging

**Running Locally:**
```bash
cd scripts
npm install
LIGHTHOUSE_URL=http://localhost:3000 \
GITHUB_TOKEN=your_token \
node lighthouse-console-analyzer.js
```

### Healthcare Compliance

This system helps maintain HIPAA compliance by:
- 🔒 Detecting PHI exposure in console logs
- 🛡️ Enforcing secure contexts (HTTPS)
- 📋 Documenting all code quality issues
- ✅ Ensuring clean browser consoles in production

---

For more information about the clinical note assistant functionality, see our [full documentation](./docs/).
