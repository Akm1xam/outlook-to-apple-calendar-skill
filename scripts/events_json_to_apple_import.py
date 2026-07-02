#!/usr/bin/env python3
"""Generate an AppleScript importer from normalized calendar event JSON."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class Event:
    title: str
    start: datetime
    end: datetime
    all_day: bool
    location: str
    notes: str
    url: str
    source_uid: str
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an idempotent AppleScript importer for Apple Calendar."
    )
    parser.add_argument("input", type=Path, help="JSON array or object with an events array")
    parser.add_argument("--calendar", required=True, help="Target Apple Calendar name")
    parser.add_argument("--output", type=Path, required=True, help="AppleScript output path")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Generate a script that writes to Calendar. Without this, the script is dry-run only.",
    )
    parser.add_argument(
        "--include-cancelled",
        action="store_true",
        help="Include events whose status/title indicates cancellation.",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update location/notes/url on matching Apple Calendar events.",
    )
    parser.add_argument(
        "--source-tag",
        default="Imported from Outlook",
        help="Marker appended to imported event notes.",
    )
    return parser.parse_args()


def parse_datetime(value: str, all_day: bool) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("datetime value must be a non-empty string")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if all_day and len(text) == 10:
        return datetime.fromisoformat(text + "T00:00:00")
    return datetime.fromisoformat(text)


def load_events(path: Path, include_cancelled: bool) -> list[Event]:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_events = data.get("events", data) if isinstance(data, dict) else data
    if not isinstance(raw_events, list):
        raise ValueError("input must be a JSON array or an object with an events array")

    events: list[Event] = []
    for index, raw in enumerate(raw_events, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"event #{index} must be an object")

        title = str(raw.get("title") or raw.get("summary") or "").strip()
        if not title:
            raise ValueError(f"event #{index} is missing title")

        status = str(raw.get("status") or "").strip().lower()
        cancellation_prefixes = ("cancelled:", "canceled:", "cancelled ", "canceled ")
        looks_cancelled = status in {"cancelled", "canceled"} or title.lower().startswith(
            cancellation_prefixes
        )
        if looks_cancelled and not include_cancelled:
            continue

        all_day = bool(raw.get("all_day") or raw.get("is_all_day") or raw.get("isAllDay"))
        if "start" not in raw:
            raise ValueError(f"event #{index} is missing start")
        start = parse_datetime(str(raw["start"]), all_day)

        if "end" in raw and raw["end"]:
            end = parse_datetime(str(raw["end"]), all_day)
        elif raw.get("duration_minutes") is not None:
            end = start + timedelta(minutes=int(raw["duration_minutes"]))
        elif all_day:
            end = start + timedelta(days=1)
        else:
            raise ValueError(f"event #{index} is missing end or duration_minutes")

        if end <= start:
            raise ValueError(f"event #{index} ends before or at its start")

        events.append(
            Event(
                title=title,
                start=start,
                end=end,
                all_day=all_day,
                location=str(raw.get("location") or "").strip(),
                notes=str(raw.get("notes") or raw.get("description") or "").strip(),
                url=str(raw.get("url") or "").strip(),
                source_uid=str(raw.get("source_uid") or raw.get("uid") or "").strip(),
                status=status or ("cancelled" if looks_cancelled else "confirmed"),
            )
        )

    return sorted(events, key=lambda event: (event.start, event.end, event.title.lower()))


def applescript_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def datetime_parts(value: datetime) -> tuple[int, int, int, int, int, int]:
    return (value.year, value.month, value.day, value.hour, value.minute, value.second)


def render_event_call(event: Event) -> str:
    sy, sm, sd, sh, smin, ss = datetime_parts(event.start)
    ey, em, ed, eh, emin, es = datetime_parts(event.end)
    arguments = [
        applescript_string(event.title),
        str(sy),
        str(sm),
        str(sd),
        str(sh),
        str(smin),
        str(ss),
        str(ey),
        str(em),
        str(ed),
        str(eh),
        str(emin),
        str(es),
        str(event.all_day).lower(),
        applescript_string(event.location),
        applescript_string(event.notes),
        applescript_string(event.url),
        applescript_string(event.source_uid),
    ]
    return f"my importEvent({', '.join(arguments)})"


def render_script(
    events: list[Event],
    calendar_name: str,
    dry_run: bool,
    update_existing: bool,
    source_tag: str,
) -> str:
    event_calls = "\n\n".join(render_event_call(event) for event in events)
    if not event_calls:
        event_calls = 'log "No events to import."'

    return f'''property targetCalendarName : {applescript_string(calendar_name)}
property dryRun : {str(dry_run).lower()}
property updateExistingEvents : {str(update_existing).lower()}
property sourceTag : {applescript_string(source_tag)}

set createdCount to 0
set skippedCount to 0
set updatedCount to 0

{event_calls}

log "Created: " & createdCount & ", updated: " & updatedCount & ", skipped existing: " & skippedCount

on importEvent(eventTitle, sy, sm, sd, sh, smin, ss, ey, em, ed, eh, emin, es, allDayFlag, locationText, notesText, urlText, sourceUid)
  set startDate to my makeDate(sy, sm, sd, sh, smin, ss)
  set endDate to my makeDate(ey, em, ed, eh, emin, es)
  set bodyText to my buildNotes(notesText, sourceUid)

  tell application "Calendar"
    set targetCalendar to missing value
    repeat with candidateCalendar in calendars
      if name of candidateCalendar is targetCalendarName then
        set targetCalendar to candidateCalendar
        exit repeat
      end if
    end repeat
    if targetCalendar is missing value then error "Apple Calendar not found: " & targetCalendarName

    set matchingEvents to {{}}
    repeat with candidateEvent in events of targetCalendar
      set candidateTitle to summary of candidateEvent
      set candidateStart to start date of candidateEvent
      set candidateEnd to end date of candidateEvent
      if candidateTitle is eventTitle and candidateStart is startDate and candidateEnd is endDate then
        set end of matchingEvents to candidateEvent
      end if
    end repeat
    if (count of matchingEvents) is 0 then
      if dryRun then
        log "[DRY RUN] create " & eventTitle & " at " & (startDate as text)
      else
        set newEvent to make new event at end of events of targetCalendar with properties {{summary:eventTitle, start date:startDate, end date:endDate, allday event:allDayFlag}}
        set location of newEvent to locationText
        set description of newEvent to bodyText
        if urlText is not "" then set url of newEvent to urlText
      end if
      set createdCount to createdCount + 1
    else
      if updateExistingEvents then
        if dryRun then
          log "[DRY RUN] update existing " & eventTitle & " at " & (startDate as text)
        else
          set existingEvent to item 1 of matchingEvents
          set location of existingEvent to locationText
          set description of existingEvent to bodyText
          if urlText is not "" then set url of existingEvent to urlText
        end if
        set updatedCount to updatedCount + 1
      else
        log "skip existing " & eventTitle & " at " & (startDate as text)
        set skippedCount to skippedCount + 1
      end if
    end if
  end tell
end importEvent

on buildNotes(notesText, sourceUid)
  set bodyText to notesText
  if bodyText is not "" then set bodyText to bodyText & return & return
  set bodyText to bodyText & sourceTag
  if sourceUid is not "" then set bodyText to bodyText & return & "Source UID: " & sourceUid
  return bodyText
end buildNotes

on makeDate(y, m, d, h, minValue, s)
  set resultDate to current date
  set year of resultDate to y
  set month of resultDate to m
  set day of resultDate to d
  set time of resultDate to (h * hours + minValue * minutes + s)
  return resultDate
end makeDate
'''


def main() -> None:
    args = parse_args()
    events = load_events(args.input, args.include_cancelled)
    script = render_script(
        events=events,
        calendar_name=args.calendar,
        dry_run=not args.write,
        update_existing=args.update_existing,
        source_tag=args.source_tag,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(script, encoding="utf-8")
    mode = "write" if args.write else "dry-run"
    print(f"Generated {mode} AppleScript for {len(events)} event(s): {args.output}")


if __name__ == "__main__":
    main()
