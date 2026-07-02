# Transfer Workflow Reference

Use this reference when the short workflow in `SKILL.md` is not enough to complete an Outlook-to-Apple-Calendar transfer.

## Date Range Resolution

Always let the user choose the date range. Support explicit dates and relative wording, then resolve the request into a concrete inclusive-start/exclusive-end window before querying Outlook.

Required outputs:

- `start_inclusive`: first instant to include.
- `end_exclusive`: first instant after the requested range.
- `timezone`: the timezone used for interpretation.
- `user_visible_range`: exact dates to show back to the user.

Rules:

- Interpret a single date as that entire local day: `[date 00:00, next day 00:00)`.
- Interpret "from X to Y", "X through Y", and equivalent wording as inclusive of both calendar dates unless the user explicitly gives times.
- Convert date-only inclusive ends to the next local day at `00:00`.
- Preserve explicit times. If the user says `2026-03-02 09:00 to 2026-03-02 17:00`, use those instants directly.
- Resolve relative dates using the current date and the user's timezone, not UTC.
- For "week", use the locale or user preference when known. If unknown, ask whether the week starts Monday or Sunday when it changes the result.
- For "work week", use Monday through Friday by default and make the exclusive end Saturday `00:00`.
- For "month", use the first day of that month through the first day of the next month.
- For "quarter", use the first day of the quarter through the first day of the next quarter.
- Around daylight saving transitions, create local midnight boundaries in the target timezone rather than adding fixed 24-hour durations.
- If the year is omitted and the requested date may have already passed, confirm the year before extraction.

Examples:

```text
User request: "March 2 to March 4, 2026"
Window: 2026-03-02T00:00:00 in user timezone through 2026-03-05T00:00:00 exclusive

User request: "tomorrow"
Window: local tomorrow 00:00 through the following local day 00:00 exclusive

User request: "next work week"
Window: next Monday 00:00 through next Saturday 00:00 exclusive, unless the user defines workdays differently
```

Use `scripts/date_range_to_window.py` when the start and end dates are already known and you need a reliable exclusive end:

```bash
python3 scripts/date_range_to_window.py --start 2026-03-02 --end 2026-03-04 --timezone Europe/Moscow
```

## Normalized Event JSON

Represent extracted source events as either a JSON array or an object with an `events` array:

```json
{
  "timezone": "America/New_York",
  "events": [
    {
      "title": "Project Sync",
      "start": "2026-03-02T09:00:00-04:00",
      "end": "2026-03-02T09:30:00-04:00",
      "all_day": false,
      "location": "Conference Room",
      "notes": "Imported from Outlook.",
      "url": "https://example.com/meeting",
      "source_uid": "outlook-event-id-or-icaluid",
      "status": "confirmed"
    }
  ]
}
```

Rules:

- Use ISO 8601 timestamps with timezone offsets when the source provides them.
- For all-day events, date-only values are allowed: `"start": "2026-03-02"`, `"end": "2026-03-03"`, `"all_day": true`.
- Use an exclusive end for all-day events. A one-day all-day event has `end` equal to the next day.
- Set `status` to `cancelled` for cancelled source events so the import script can skip them.
- Keep `source_uid` when available; it improves auditability but should not be treated as public data.

## Microsoft Graph Route

Use this route when the user can authenticate and the tenant/app policy allows calendar access.

Important points:

- Prefer `calendarView` over raw event lists for date-range transfer because it returns occurrences, exceptions, and single event instances for the requested time window.
- Use the user's timezone in the request window and request header when possible.
- Follow `@odata.nextLink` until there are no more pages.
- Request the least privilege allowed by the environment, typically read-only calendar access.
- For shared or delegated calendars, confirm the user has rights to view the calendar and private items if needed.

Typical request shape:

```text
GET /me/calendar/calendarView?startDateTime={start}&endDateTime={end}
GET /me/calendars/{calendar-id}/calendarView?startDateTime={start}&endDateTime={end}
Prefer: outlook.timezone="{iana-or-windows-timezone}"
```

Map Graph events to normalized JSON:

- `subject` -> `title`
- `start.dateTime` + `start.timeZone` -> `start`
- `end.dateTime` + `end.timeZone` -> `end`
- `isAllDay` -> `all_day`
- `location.displayName` -> `location`
- `bodyPreview` or sanitized `body.content` -> `notes`
- `webLink` or online meeting join URL -> `url`
- `iCalUId` or `id` -> `source_uid`
- `isCancelled` -> `status: "cancelled"`

## ICS Route

Use this route when Outlook, Outlook Web, Exchange, or a subscribed calendar can export or publish `.ics`.

Checks:

- Confirm whether the export is a single calendar, all calendars, or a subscribed view.
- Confirm whether the export contains expanded instances or recurring masters.
- If recurring masters are present, expand recurrence with a reliable ICS library when available. Do not hand-roll complex recurrence rules unless the date window is tiny and every instance can be verified against the Outlook UI.
- Respect `STATUS:CANCELLED`, `RECURRENCE-ID`, `EXDATE`, `RDATE`, timezone definitions, and all-day `VALUE=DATE` fields.

If recurrence expansion is uncertain, compare the resulting list against Outlook's visible list view for the target date range before importing.

## Outlook for Mac Scripting Route

Use this route when Outlook is installed and synced locally.

Checks:

- Inspect Outlook's scripting dictionary if needed; Outlook versions differ.
- Enumerate calendars/folders first instead of assuming the default calendar.
- Query events by a broad window, then filter by exclusive date boundaries in the script.
- Validate whether recurring events are exposed as individual occurrences or only as masters. If only masters are exposed, switch to Graph, ICS with expansion, or UI fallback.
- Compare the scripted count with Outlook's list view for the same range.

Avoid relying on cached local data until it has been compared with what the user sees in Outlook.

## Outlook UI Accessibility Fallback

Use this route when corporate policy blocks Graph/device auth and the local Outlook object model is incomplete, but the user can open Outlook on macOS.

Workflow:

1. Ask the user to open Outlook and make sure the correct account/calendar is visible.
2. Use Outlook controls or AppleScript UI scripting to navigate to the resolved target date range.
3. Switch to the densest list-style calendar view that matches the requested range. Use day, work-week, week, or month views as appropriate, then prefer list rows for extraction.
4. Dump the macOS accessibility tree for the Outlook window or read visible static text rows.
5. Parse rows into dates, titles, start times, and durations.
6. Scroll through the whole list if the range does not fit on screen.
7. Compare parsed rows with the visible Outlook list before generating import JSON.

Extraction tips:

- Treat row grouping headers as dates.
- Parse localized time and duration labels carefully.
- Mark rows whose title begins with a localized cancellation prefix as `status: "cancelled"`.
- Preserve unknown fields in notes only if the user is comfortable importing them.
- UI text can be truncated; verify suspiciously short titles manually.

## Apple Calendar Import

Use `scripts/events_json_to_apple_import.py` to generate AppleScript from normalized JSON.

Dry run:

```bash
python3 scripts/events_json_to_apple_import.py events.json --calendar "Work" --output import.applescript
osascript import.applescript
```

Actual write:

```bash
python3 scripts/events_json_to_apple_import.py events.json --calendar "Work" --output import.applescript --write
osascript import.applescript
```

The generated AppleScript:

- finds the target Apple Calendar by name,
- skips cancelled events by default,
- checks for existing events with the same title, start, and end,
- creates missing events,
- optionally updates matching existing events when generated with `--update-existing`,
- logs created, skipped, and updated counts.

## Verification Checklist

Before final response:

- Source event count equals imported plus intentionally skipped events.
- Apple Calendar has the expected events in the exact target calendar.
- Times are correct in the user's timezone.
- All-day events span the expected days.
- Recurring meetings, moved occurrences, exceptions, and cancellations are accounted for.
- Existing Apple Calendar events were not duplicated.
- Any private details in temporary artifacts are removed, ignored, or explicitly kept only with user approval.
