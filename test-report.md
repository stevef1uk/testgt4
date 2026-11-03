# Test Review — active phases

## Summary
The planned active-phase tests were reviewed for file existence and substantive
assertions. The Playwright tests contain real user-facing assertions. However,
phase verification is not green: the app container healthcheck invokes `curl`
while the supplied Alpine runtime image does not install `curl`, so the
Playwright service cannot proceed after the app healthcheck.

## Per-requirement results
- Active UI requirements: `finally/test/e2e.spec.ts` exists and contains real
  assertions for dashboard rendering, seeded portfolio/watchlist data,
  add/remove behavior, and portfolio-question submission.
- Phase verification: FAIL — app healthcheck cannot execute `curl` in the
  supplied runtime image.

## Overall assessment
FAIL. Reopen the implementation bead that owns `finally/Dockerfile` and/or the
compose runtime healthcheck, make the healthcheck executable in the runtime
image, and rerun the required phase verification. No source or test files were
modified by this review.
