# Lighthouse Console Error Audit System

## Overview

Automated system for detecting, classifying, and resolving console errors in the Titan_Lite healthcare application using Lighthouse audits. This tool ensures high code quality and HIPAA compliance by preventing PHI exposure through console logs.

## Why This Matters for Healthcare

Console errors in healthcare applications can:
- **Expose Protected Health Information (PHI)** through verbose error messages
- **Impact clinical workflows** if errors cause functionality issues
- **Create security vulnerabilities** that could be exploited
- **Reduce user trust** in the clinical system
- **Violate HIPAA compliance** if patient data appears in browser logs

## Architecture

### Components

1. **Lighthouse Console Analyzer** (`scripts/lighthouse-console-analyzer.js`)
   - Main analysis engine
   - Runs Lighthouse audits
   - Classifies errors into categories
   - Applies auto-fixes or creates issues

2. **GitHub Actions Workflow** (`.github/workflows/lighthouse-console-audit.yml`)
   - Automatically runs on PRs and pushes
   - Deploys to preview environment
   - Executes analyzer
   - Commits fixes and updates PRs

3. **Configuration** (`config/lighthouse.config.json`)
   - Lighthouse audit settings
   - Auto-fix preferences
   - Issue creation rules
   - Healthcare compliance settings

## Error Categories

### Category A: Auto-Fixable Issues ✅

These errors can be automatically fixed by the system:

1. **Console.log statements**
   - Leftover debug statements
   - Development logging artifacts
   - **Fix:** Remove or wrap in environment checks

2. **Simple null/undefined checks**
   - `Cannot read property 'x' of undefined`
   - `TypeError: x is null`
   - **Fix:** Add optional chaining or null checks

3. **Missing error boundaries**
   - Unhandled promise rejections
   - React component errors
   - **Fix:** Add try-catch or error boundaries

### Category B: Investigation Required 🔍

These errors require manual review:

1. **Third-party library errors**
   - External dependency issues
   - Version conflicts
   - **Action:** Create issue with library details

2. **Network/API failures**
   - Failed fetch requests
   - CORS errors
   - Timeout issues
   - **Action:** Document and investigate backend

3. **Complex logic errors**
   - State management issues
   - Race conditions
   - **Action:** Create issue with reproduction steps

4. **PHI exposure risks** 🚨
   - Any error mentioning patient data
   - Medical record information in logs
   - **Action:** High priority issue + security review

## Usage

### Automatic Execution (Recommended)

The system runs automatically on:
- **Pull Requests** - Audits PR preview deployments
- **Main branch pushes** - Audits staging/production
- **Manual triggers** - Via GitHub Actions UI

### Manual Execution

```bash
# Install dependencies
npm install lighthouse chrome-launcher @octokit/rest

# Run analyzer
LIGHTHOUSE_URL=https://your-app.com \
GITHUB_TOKEN=your_token \
PR_NUMBER=123 \
node scripts/lighthouse-console-analyzer.js
```

### Configuration Options

Edit `config/lighthouse.config.json`:

```json
{
  "autofix": {
    "enabled": true,              // Enable auto-fixing
    "maxChangesPerRun": 10,       // Limit fixes per run
    "dryRun": false               // Preview without committing
  },
  "issueCreation": {
    "enabled": true,              // Create GitHub issues
    "labels": ["lighthouse", "console-error"],
    "autoAssign": true            // Auto-assign to PR author
  },
  "healthcareCompliance": {
    "hipaaAudit": true,           // Check for PHI exposure
    "requireSecureContext": true  // Enforce HTTPS
  }
}
```

## Workflow

```
1. PR Created
   ↓
2. Deploy to Preview Environment
   ↓
3. Run Lighthouse Audit
   ↓
4. Extract Console Errors
   ↓
5. Classify Each Error
   ↓
   ├─→ Category A (Auto-fixable)
   │   ├─ Apply fix
   │   ├─ Commit changes
   │   └─ Push to PR
   │
   └─→ Category B (Investigation)
       ├─ Create GitHub Issue
       ├─ Add detailed context
       └─ Link in PR comment
   ↓
6. Update PR Comment with Summary
   ↓
7. Upload Reports as Artifacts
```

## Output Examples

### PR Comment

```markdown
## 🔦 Lighthouse Console Error Analysis

**Audit Run:** 2026-02-07T10:30:00Z
**Environment Tested:** https://pr-123.preview.titan-lite.com

### ✅ Auto-Fixed Issues (Category A)

| File | Issue | Fix Applied |
|------|-------|-------------|
| `components/PatientDashboard.tsx` | Line 45 | Removed console.log statement |
| `utils/api.ts` | Line 112 | Added null check for response.data |

**Total Fixes:** 2 issues resolved automatically

### 📋 Issues Created for Investigation (Category B)

| Issue | Type | Severity | Link |
|-------|------|----------|------|
| #456 | Third-party | Medium | [View Issue](#) |
| #457 | Network | High | [View Issue](#) |

**Total Issues:** 2 issues require manual investigation

### 🏥 Healthcare Compliance Notes

- ✅ All console errors reviewed for PHI exposure
- ✅ No sensitive patient data in browser console
- ✅ HIPAA compliance maintained
```

### GitHub Issue

```markdown
## Error Details

**Detected by:** Lighthouse Best Practices Audit
**Audit Date:** 2026-02-07T10:30:00Z
**Environment:** https://pr-123.preview.titan-lite.com

### Error Message

`Failed to load resource: net::ERR_FAILED`

### Location
- **File:** `services/analytics.js`
- **Line:** 23
- **Component:** Analytics Integration

### Error Classification
**Category:** Third-party library
**Severity:** Medium
**Healthcare Impact:** 🟢 LOW - No PHI exposure detected

### Investigation Needed
- [ ] Check analytics service status
- [ ] Verify API key configuration
- [ ] Test in production environment
- [ ] Consider fallback mechanism
```

## Healthcare Compliance Features

### PHI Detection

The analyzer scans for keywords that might indicate PHI exposure:
- patient, medical, diagnosis, prescription
- SSN, DOB, medical record number
- Health conditions, medications

If detected: **🔴 HIGH PRIORITY** issue created immediately

### Secure Context Enforcement

- Ensures all audited URLs use HTTPS
- Checks for mixed content warnings
- Validates CSP headers

### Error Message Sanitization

Auto-fixes remove or sanitize error messages that might contain:
- User identifiable information
- Stack traces with sensitive data
- Verbose debugging information

## Best Practices

### For Developers

1. **Remove console.log before committing**
   - Use proper logging libraries
   - Environment-specific logging

2. **Handle errors gracefully**
   - Add try-catch blocks
   - Implement error boundaries
   - Provide user-friendly messages

3. **Never log PHI**
   - No patient names, IDs, or medical data
   - Sanitize error messages
   - Use error tracking services securely

### For Code Reviewers

1. **Check Lighthouse PR comments**
   - Review auto-fixes for correctness
   - Verify no functionality broken
   - Ensure PHI compliance

2. **Address investigation issues**
   - Prioritize PHI-related errors
   - Review third-party integrations
   - Test error scenarios

## Troubleshooting

### Lighthouse Audit Fails

**Problem:** Audit cannot reach URL
**Solution:** 
- Check deployment status
- Verify preview URL is correct
- Increase wait timeout in workflow

### Auto-fixes Break Functionality

**Problem:** Automated changes cause issues
**Solution:**
- Set `"dryRun": true` in config
- Review proposed fixes before applying
- Adjust `maxChangesPerRun` to smaller number

### Too Many False Positives

**Problem:** Non-issues flagged as errors
**Solution:**
- Adjust classification patterns in analyzer
- Add exclusion rules for known safe patterns
- Update error detection thresholds

## Metrics & Reporting

The system tracks:
- **Console errors per PR**
- **Auto-fix success rate**
- **Time to resolution for issues**
- **HIPAA compliance score**
- **Lighthouse best practices score**

View reports in:
- GitHub Actions artifacts
- PR comments
- `reports/` directory (if running locally)

## Security Considerations

1. **GitHub Token Permissions**
   - Needs: `contents:write`, `issues:write`, `pull-requests:write`
   - Store as repository secret

2. **PHI Exposure Prevention**
   - All errors logged locally, never to external services
   - Reports sanitized before upload
   - Audit logs reviewed for compliance

3. **Code Injection Prevention**
   - Auto-fixes use safe AST transformations
   - No dynamic code execution
   - All changes reviewed in PR diff

## Future Enhancements

- [ ] Machine learning classification for better error categorization
- [ ] Integration with error tracking services (Sentry, Rollbar)
- [ ] Performance impact analysis of fixes
- [ ] Automated regression testing after fixes
- [ ] Custom rules engine for organization-specific patterns
- [ ] Dashboard for tracking error trends over time

## Support

For questions or issues with the Lighthouse Console Audit system:

1. Check this documentation
2. Review existing GitHub issues
3. Contact the development team
4. Create a new issue with `lighthouse` label

---

**Remember:** In healthcare applications, console errors aren't just code quality issues—they're potential compliance violations. This system helps us maintain the highest standards for patient safety and data security.
