<h1 align="center">Outlook to Apple Calendar Skill</h1>

<p align="center">
  A universal AI-agent skill for moving Outlook, Exchange, Microsoft 365, and Outlook.com calendar events into Apple Calendar on macOS.
</p>

<p align="center">
  Custom date ranges · Dry-run first · Duplicate protection · Graph, ICS, Outlook for Mac, and UI fallback workflows
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#русский">Русский</a> · <a href="#github-repository-metadata">GitHub Metadata</a>
</p>

---

## GitHub Repository Metadata

**Recommended repository name**

```text
outlook-to-apple-calendar-skill
```

**Short GitHub description**

```text
Universal AI-agent skill for transferring Outlook, Exchange, and Microsoft 365 calendar events to Apple Calendar on macOS with custom date ranges, dry-run import, duplicate protection, and Graph, ICS, Outlook for Mac, and UI fallback workflows.
```

**Suggested GitHub topics**

```text
outlook-calendar
apple-calendar
microsoft-365
exchange-calendar
calendar-migration
calendar-import
macos
applescript
microsoft-graph
ics
ai-agent
codex-skill
```

---

## English

### What Is This?

**Outlook to Apple Calendar Skill** is a reusable skill for AI agents that need to transfer calendar events from Microsoft Outlook into Apple Calendar on macOS.

It is designed for the messy real world: Outlook.com, Microsoft 365, Exchange, work accounts, school accounts, shared calendars, delegated calendars, blocked Graph access, incomplete local Outlook scripting, recurring meetings, cancellations, and custom date ranges.

The skill does not promise a fragile one-click sync. Instead, it gives an AI agent a safe workflow:

1. Resolve the user's requested date range.
2. Extract Outlook events using the best available route.
3. Normalize the events into a consistent JSON shape.
4. Generate a dry-run Apple Calendar import plan.
5. Avoid duplicates.
6. Import only after review.
7. Verify the final Apple Calendar result.

### Who Is It For?

Use this repository if you searched for:

- how to move Outlook calendar to Apple Calendar,
- import Outlook Calendar to Apple Calendar on Mac,
- transfer Microsoft 365 calendar to Apple Calendar,
- copy Exchange calendar events to Apple Calendar,
- Outlook to iCal migration,
- Outlook calendar AppleScript import,
- Microsoft Graph calendarView export,
- ICS to Apple Calendar import,
- AI agent calendar migration workflow.

### Why This Skill Exists

Calendar migration sounds simple until it is not.

Common problems:

- Microsoft Graph authentication may be disabled by an organization.
- Outlook exports may include recurring masters instead of expanded instances.
- Outlook for Mac scripting may miss synced or recurring events.
- Calendar UI views may show more events than APIs expose locally.
- Apple Calendar imports can easily create duplicates.
- Date ranges are easy to get wrong, especially when the user says "next week", "work week", or "from Monday to Friday".

This skill helps an agent choose the safest available method and verify the result instead of guessing.

### Key Features

- **Any date range**: one day, multiple days, work week, full week, month, quarter, or exact start/end times.
- **Relative date support**: prompts the agent to resolve phrases like "tomorrow" or "next week" against the user's current date and timezone.
- **Inclusive-to-exclusive window handling**: converts user wording like "March 2 through March 4" into the correct query window.
- **Dry-run by default**: generates an AppleScript import plan before writing anything.
- **Duplicate protection**: checks title, start time, and end time before creating Apple Calendar events.
- **Cancelled event handling**: skips cancelled events by default unless the user asks to include them.
- **Multiple Outlook routes**: Microsoft Graph, ICS export, Outlook for Mac scripting, macOS Accessibility UI extraction, and manual fallback.
- **Privacy-first process**: no tokens, emails, event dumps, meeting bodies, or attendee lists are committed by default.

### How It Works

The skill guides an agent through this fallback ladder:

```text
Microsoft Graph calendarView
        ↓
Outlook / Exchange ICS export
        ↓
Outlook for Mac scripting
        ↓
macOS Accessibility extraction from the Outlook UI
        ↓
Manual export and verified Apple Calendar import
```

The goal is not to bypass Microsoft, Exchange, school, or company security policies. The goal is to use a user-approved route that works in the current environment.

### Repository Structure

```text
outlook-to-apple-calendar/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── transfer-workflow.md
└── scripts/
    ├── date_range_to_window.py
    └── events_json_to_apple_import.py
```

### Install for Codex

Copy the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R outlook-to-apple-calendar ~/.codex/skills/outlook-to-apple-calendar
```

Then ask Codex:

```text
Use $outlook-to-apple-calendar to transfer my Outlook calendar events to Apple Calendar from March 2 to March 4.
```

### Use With Any AI Agent

This is a file-based skill. Agents should:

1. Read `SKILL.md`.
2. Load `references/transfer-workflow.md` when detailed transfer guidance is needed.
3. Use the scripts only as helpers, not as a substitute for verifying the calendar data.

### Date Range Helper

Convert explicit dates into an inclusive-start / exclusive-end query window:

```bash
python3 scripts/date_range_to_window.py \
  --start 2026-03-02 \
  --end 2026-03-04 \
  --timezone Europe/Moscow
```

Example output:

```json
{
  "start_inclusive": "2026-03-02T00:00:00+03:00",
  "end_exclusive": "2026-03-05T00:00:00+03:00",
  "timezone": "Europe/Moscow",
  "start_was_date_only": true,
  "end_mode": "inclusive_date_end"
}
```

### Apple Calendar Import Helper

Generate a dry-run AppleScript importer from normalized event JSON:

```bash
python3 scripts/events_json_to_apple_import.py events.json \
  --calendar "Work" \
  --output import.applescript

osascript import.applescript
```

Generate a real importer after reviewing the dry run:

```bash
python3 scripts/events_json_to_apple_import.py events.json \
  --calendar "Work" \
  --output import.applescript \
  --write

osascript import.applescript
```

### Normalized Event JSON

```json
{
  "timezone": "America/New_York",
  "events": [
    {
      "title": "Project Sync",
      "start": "2026-03-02T09:00:00-05:00",
      "end": "2026-03-02T09:30:00-05:00",
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

### Privacy and Safety

This repository intentionally contains no company-specific settings, tenant names, user emails, private calendar events, access tokens, meeting titles, screenshots, or organization-specific instructions.

The skill tells agents not to commit generated calendar exports, event dumps, credentials, meeting bodies, attendee lists, screenshots, or imported calendar data unless the user explicitly reviews and approves that content.

### What This Is Not

This is not a background sync daemon.

This is not a credential store.

This is not a way to bypass Microsoft, Exchange, school, or company security policies.

This is a careful AI-agent workflow for transferring Outlook events into Apple Calendar with review and verification.

---

## Русский

### Что Это?

**Outlook to Apple Calendar Skill** — это переиспользуемый skill для AI-агентов, которым нужно перенести события из Microsoft Outlook в Apple Calendar на macOS.

Он рассчитан на реальные сценарии: Outlook.com, Microsoft 365, Exchange, рабочие аккаунты, учебные аккаунты, общие календари, делегированные календари, заблокированный Microsoft Graph, неполные данные из локального Outlook, повторяющиеся встречи, отменённые события и любые пользовательские диапазоны дат.

Skill не обещает хрупкую магию в один клик. Вместо этого он даёт агенту безопасный процесс:

1. Разобрать диапазон дат, который указал пользователь.
2. Получить события Outlook лучшим доступным способом.
3. Привести события к единому JSON-формату.
4. Создать dry-run план импорта в Apple Calendar.
5. Проверить дубли.
6. Импортировать только после проверки.
7. Сверить итоговый результат в Apple Calendar.

### Для Кого Это?

Этот репозиторий будет полезен, если человек ищет:

- как перенести календарь Outlook в Apple Calendar,
- импорт Outlook Calendar в Apple Calendar на Mac,
- перенос календаря Microsoft 365 в Apple Calendar,
- копирование событий Exchange в Apple Calendar,
- миграция Outlook в iCal,
- импорт Outlook Calendar через AppleScript,
- экспорт через Microsoft Graph calendarView,
- импорт ICS в Apple Calendar,
- AI-агент для переноса календаря.

### Зачем Нужен Этот Skill

Перенос календаря звучит просто, пока не начинаются детали.

Типичные проблемы:

- Microsoft Graph может быть запрещён организацией.
- ICS-экспорт может содержать не отдельные встречи, а правила повторения.
- Outlook for Mac scripting может не увидеть все синхронизированные события.
- Интерфейс Outlook иногда показывает больше событий, чем локальный API.
- Apple Calendar легко засорить дублями.
- Диапазоны дат легко перепутать, особенно когда пользователь пишет "на следующей неделе", "рабочая неделя" или "с понедельника по пятницу".

Этот skill помогает агенту выбрать самый надёжный доступный путь и проверить результат, а не действовать наугад.

### Основные Возможности

- **Любой диапазон дат**: один день, несколько дней, рабочая неделя, полная неделя, месяц, квартал или точное время начала и конца.
- **Относительные даты**: агент должен вычислять фразы вроде "завтра" или "следующая неделя" от текущей даты и timezone пользователя.
- **Правильные границы дат**: включительные формулировки вроде "со 2 по 4 марта" превращаются в корректное окно запроса с exclusive end.
- **Dry-run по умолчанию**: сначала создаётся план импорта, и только потом можно писать в Apple Calendar.
- **Защита от дублей**: проверка по названию, времени начала и времени окончания.
- **Отменённые события**: по умолчанию пропускаются, если пользователь не попросил импортировать их явно.
- **Несколько путей получения Outlook-событий**: Microsoft Graph, ICS export, Outlook for Mac scripting, извлечение через macOS Accessibility и ручной fallback.
- **Privacy-first подход**: токены, email-адреса, дампы событий, тела встреч и списки участников не попадают в репозиторий.

### Как Это Работает

Skill ведёт агента по цепочке fallback-методов:

```text
Microsoft Graph calendarView
        ↓
Outlook / Exchange ICS export
        ↓
Outlook for Mac scripting
        ↓
Извлечение из интерфейса Outlook через macOS Accessibility
        ↓
Ручной экспорт и проверенный импорт в Apple Calendar
```

Цель не в обходе политик Microsoft, Exchange, учебного заведения или компании. Цель в том, чтобы использовать доступный и одобренный пользователем способ.

### Структура Репозитория

```text
outlook-to-apple-calendar/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── transfer-workflow.md
└── scripts/
    ├── date_range_to_window.py
    └── events_json_to_apple_import.py
```

### Установка Для Codex

Скопируйте папку skill в директорию Codex skills:

```bash
mkdir -p ~/.codex/skills
cp -R outlook-to-apple-calendar ~/.codex/skills/outlook-to-apple-calendar
```

После этого можно попросить Codex:

```text
Use $outlook-to-apple-calendar to transfer my Outlook calendar events to Apple Calendar from March 2 to March 4.
```

### Использование С Любым AI-Агентом

Это file-based skill. Агент должен:

1. Прочитать `SKILL.md`.
2. Открыть `references/transfer-workflow.md`, если нужны подробные инструкции по переносу.
3. Использовать скрипты как вспомогательные инструменты, но не заменять ими проверку календарных данных.

### Helper Для Диапазона Дат

Преобразовать явные даты в окно `start_inclusive` / `end_exclusive`:

```bash
python3 scripts/date_range_to_window.py \
  --start 2026-03-02 \
  --end 2026-03-04 \
  --timezone Europe/Moscow
```

Пример результата:

```json
{
  "start_inclusive": "2026-03-02T00:00:00+03:00",
  "end_exclusive": "2026-03-05T00:00:00+03:00",
  "timezone": "Europe/Moscow",
  "start_was_date_only": true,
  "end_mode": "inclusive_date_end"
}
```

### Helper Для Импорта В Apple Calendar

Создать dry-run AppleScript из нормализованного JSON:

```bash
python3 scripts/events_json_to_apple_import.py events.json \
  --calendar "Work" \
  --output import.applescript

osascript import.applescript
```

Создать реальный импорт после проверки dry-run:

```bash
python3 scripts/events_json_to_apple_import.py events.json \
  --calendar "Work" \
  --output import.applescript \
  --write

osascript import.applescript
```

### Формат Событий

```json
{
  "timezone": "America/New_York",
  "events": [
    {
      "title": "Project Sync",
      "start": "2026-03-02T09:00:00-05:00",
      "end": "2026-03-02T09:30:00-05:00",
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

### Приватность И Безопасность

В репозитории нет company-specific настроек, tenant names, email-адресов, приватных событий, access tokens, названий реальных встреч, screenshots или инструкций, привязанных к конкретной организации.

Skill отдельно говорит агенту не коммитить generated calendar exports, event dumps, credentials, тексты встреч, списки участников, screenshots или импортированные календарные данные, если пользователь явно не проверил и не разрешил сохранить эти материалы.

### Чем Этот Skill Не Является

Это не background sync daemon.

Это не хранилище credentials.

Это не способ обхода политик Microsoft, Exchange, учебного заведения или компании.

Это аккуратный workflow для AI-агента, который переносит Outlook-события в Apple Calendar с проверкой и контролем результата.

---

## Search Keywords

Outlook to Apple Calendar, Outlook Calendar to Apple Calendar, import Outlook Calendar to Apple Calendar, Microsoft 365 calendar to Apple Calendar, Exchange calendar to Apple Calendar, Outlook to iCal, Apple Calendar import, Outlook Calendar migration, Microsoft Graph calendarView, ICS to Apple Calendar, AppleScript Calendar import, AI agent calendar migration.

Outlook в Apple Calendar, перенос календаря Outlook в Apple Calendar, импорт Outlook Calendar в Apple Calendar, Microsoft 365 календарь в Apple Calendar, Exchange календарь в Apple Calendar, Outlook в iCal, импорт ICS в Apple Calendar, миграция календаря Outlook, AppleScript импорт календаря, AI-агент для переноса календаря.
