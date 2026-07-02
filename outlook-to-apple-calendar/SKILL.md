---
name: outlook-to-apple-calendar
description: Universal workflow for copying, migrating, importing, or syncing Outlook, Exchange, Microsoft 365, or Outlook.com calendar events into Apple Calendar on macOS for any user-specified date range. Use when a user asks to transfer meetings or events from Outlook to Apple Calendar for explicit dates, relative dates, a single day, multiple weeks, a month, or any custom range, including personal, work, school, shared, delegated, or corporate calendars where Microsoft Graph, ICS export, local Outlook scripting, or macOS Accessibility/UI extraction may be needed.
---

# Outlook to Apple Calendar

## Goal

Move Outlook calendar events into Apple Calendar with a verified source count, a dry-run import plan, duplicate protection, and a final Apple Calendar verification pass.

## Non-Negotiables

- Treat calendar data as private. Do not commit tokens, screenshots, event dumps, email addresses, meeting bodies, attendee lists, or generated import files unless the user explicitly asks and the content has been reviewed/redacted.
- Ask only for the missing choices that change the outcome: source account/calendar, date range, target Apple Calendar, whether to include cancelled/private events, and whether existing Apple events may be updated.
- Accept any user-specified date range: single day, explicit start/end dates, week, work week, month, quarter, or relative wording such as "next week" or "tomorrow". Resolve relative wording against the current date and the user's timezone.
- If a date range is ambiguous, confirm it before extraction. Always restate the resolved concrete window with exact dates.
- Convert inclusive user ranges to an exclusive end boundary. Example: "March 2 through March 4, 2026" means `[2026-03-02 00:00, 2026-03-05 00:00)` in the user's chosen timezone.
- Prefer expanded event instances over recurring masters. Verify recurring meetings, exceptions, and cancellations before import.
- Skip cancelled events by default. Include them only if the user explicitly requests it.
- Never write to Apple Calendar until the extracted event list and dry-run plan have been checked for obvious omissions and duplicates.

## Route Selection

Use the first route that works for the user's account and environment:

1. **Microsoft Graph calendarView**: best when authentication is allowed. It returns occurrences, exceptions, and single instances for a time range.
2. **Outlook/Exchange ICS export or published ICS**: good when a range export is available. Validate recurrence expansion carefully.
3. **Local Outlook for Mac scripting**: good when Outlook exposes the account's synced calendars through AppleScript/JXA.
4. **Outlook UI Accessibility fallback**: use when APIs or scripted object models are blocked but the user can view the calendar in the Outlook app. Switch Outlook to list/work-week view for the date range and extract rows from the macOS accessibility tree.
5. **Manual export/import fallback**: use only when automation is blocked. Still normalize, dedupe, and verify after import.

For detailed commands, extraction checks, and fallback notes, read `references/transfer-workflow.md`.

## Standard Workflow

1. **Prepare**
   - Confirm source Outlook calendar(s), target Apple Calendar, date range, timezone, and inclusion policy for cancelled/private items.
   - Resolve the user's date request into concrete `start_inclusive` and `end_exclusive` boundaries before touching Outlook.
   - Create a temporary work directory outside any repo when possible.
   - Check Apple Calendar permissions before the final write.

2. **Extract**
   - Use the selected route to collect every event instance in the exclusive date window.
   - Record a source-side count grouped by date.
   - If the source view has a visible count, compare it with the extracted count.

3. **Normalize**
   - Convert the source data into JSON with fields accepted by `scripts/events_json_to_apple_import.py`.
   - Preserve at least `title`, `start`, `end`, `all_day`, `location`, `notes`, `url`, `source_uid`, and `status` when available.
   - Keep timezone offsets in `start` and `end` values whenever possible.

4. **Plan**
   - Run `scripts/events_json_to_apple_import.py` without `--write` to generate a dry-run AppleScript.
   - Inspect the dry-run output for event count, date grouping, duplicate decisions, and skipped cancelled items.

5. **Import**
   - Regenerate the AppleScript with `--write` only after the plan looks correct.
   - Run it with `osascript`.
   - Do not use destructive cleanup unless the user explicitly approves it.

6. **Verify**
   - Query Apple Calendar for the same exclusive date window.
   - Compare imported count, titles, start/end times, all-day flags, and target calendar.
   - Report skipped events and any conflicts that required manual handling.

## Bundled Scripts

- `scripts/date_range_to_window.py`: converts explicit start/end dates into a timezone-aware inclusive-start/exclusive-end query window.
- `scripts/events_json_to_apple_import.py`: converts normalized event JSON into an idempotent AppleScript importer. It defaults to dry-run mode and skips cancelled events unless requested.

## Output Standard

When finished, summarize:

- source route used,
- source event count and imported count,
- target Apple Calendar name,
- date range and timezone,
- skipped cancelled/private/conflicting items,
- verification result.
