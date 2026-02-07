---
name: Lighthouse Console Error
about: Console error detected by Lighthouse audit
title: 'Console Error: [ERROR_TYPE] in [COMPONENT]'
labels: lighthouse, console-error, needs-investigation
assignees: ''
---

## Error Details

**Detected by:** Lighthouse Best Practices Audit
**Audit Date:** YYYY-MM-DD HH:MM:SS
**Environment:** [Staging/Production URL]
**Lighthouse Run ID:** run-TIMESTAMP

### Error Message

```
[Full error message]
```

### Stack Trace

```
[Stack trace if available]
```

### Location
- **File:** `[file path]`
- **Line:** [line number]
- **Column:** [column number]
- **Component/Context:** [component name or page]

### Error Classification
**Category:** [Error type - e.g., Third-party library, Network, Logic]
**Severity:** [High/Medium/Low based on frequency and impact]
**Frequency:** [How often error occurs]

### Healthcare Compliance Impact
**PHI Exposure Risk:** [High/Medium/Low/None]
**HIPAA Concern:** [Yes/No - explain if yes]
**Clinical Functionality Impact:** [Describe any impact on clinical workflows]

### Reproduction Steps
1. Navigate to [URL]
2. Open browser console
3. [Specific actions that trigger error]
4. Observe error in console

### Investigation Needed
- [ ] Identify root cause
- [ ] Determine if error affects functionality
- [ ] Check if error occurs in production
- [ ] Verify HIPAA compliance (no PHI exposure in console)
- [ ] Test potential fixes
- [ ] Verify fix doesn't break other functionality
- [ ] Ensure clinical workflows remain intact

### Lighthouse Report
**Full Report:** [Link to Lighthouse report in CI artifacts]
**Related Audits:**
- errors-in-console: [pass/fail]
- best-practices score: [XX/100]

### Additional Context
[Any other relevant information from Lighthouse or manual inspection]

---
**Security Note:** If this error exposes Protected Health Information (PHI), treat as HIGH priority and tag @security-team immediately.

<!-- lighthouse-issue-tracker: [issue-id] -->
