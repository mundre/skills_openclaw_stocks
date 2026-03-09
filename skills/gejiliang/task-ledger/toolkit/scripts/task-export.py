#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / 'tasks'


def die(msg, code=1):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def load_task(task_id):
    path = TASKS_DIR / f"{task_id}.json"
    if not path.exists():
        die(f"Task not found: {task_id}", 2)
    return path, json.loads(path.read_text())


def md_list(items):
    return ', '.join(items) if items else '-'


def export_short(data):
    reporting = data.get('reporting') or {
        'mode': 'short-first',
        'preferFileBackedReports': True,
        'longReportPath': None,
    }
    return {
        'taskId': data.get('taskId', '-'),
        'title': data.get('title', '-'),
        'status': data.get('status', '-'),
        'stage': data.get('stage', '-'),
        'nextAction': data.get('nextAction', '-'),
        'workingSummary': data.get('workingSummary', ''),
        'readinessDeps': data.get('dependsOn', []),
        'reportMode': reporting.get('mode'),
        'longReportPath': reporting.get('longReportPath'),
    }


def short_text(data):
    short = export_short(data)
    deps = ', '.join(short['readinessDeps']) if short['readinessDeps'] else '-'
    return (
        f"Task `{short['taskId']}` — {short['title']}\n"
        f"status={short['status']} stage={short['stage']} mode={short['reportMode']}\n"
        f"next={short['nextAction']}\n"
        f"deps={deps}\n"
        f"summary={short['workingSummary'] or '-'}\n"
        f"report={short['longReportPath'] or '-'}\n"
    )


def export_markdown(data):
    lines = []
    lines.append(f"# {data.get('title', data.get('taskId', 'Task'))}")
    lines.append('')
    lines.append(f"- **Task ID:** `{data.get('taskId', '-')}`")
    lines.append(f"- **Status:** `{data.get('status', '-')}`")
    lines.append(f"- **Priority:** `{data.get('priority', '-')}`")
    lines.append(f"- **Current Stage:** `{data.get('stage', '-')}`")
    lines.append(f"- **Execution Mode:** `{data.get('executionMode', '-')}`")
    lines.append(f"- **Created At:** {data.get('createdAt', '-')}")
    lines.append(f"- **Started At:** {data.get('startedAt', '-')}")
    lines.append(f"- **Updated At:** {data.get('updatedAt', '-')}")
    lines.append(f"- **Completed At:** {data.get('completedAt', '-')}")
    lines.append('')
    lines.append('## Goal')
    lines.append('')
    lines.append(data.get('goal') or '-')
    lines.append('')
    lines.append('## Relations')
    lines.append('')
    lines.append(f"- **Parent:** {data.get('parentTaskId') or '-'}")
    lines.append(f"- **Children:** {md_list(data.get('childTaskIds') or [])}")
    lines.append(f"- **Depends On:** {md_list(data.get('dependsOn') or [])}")
    lines.append(f"- **Blocked By:** {md_list(data.get('blockedBy') or [])}")
    lines.append(f"- **Blocked Reason:** {data.get('blockedReason') or '-'}")
    lines.append('')
    lines.append('## Next Action')
    lines.append('')
    lines.append(data.get('nextAction') or '-')
    lines.append('')
    lines.append('## Working Summary')
    lines.append('')
    lines.append(data.get('workingSummary') or '-')
    lines.append('')
    lines.append('## Stages')
    lines.append('')
    for stage in data.get('stages', []):
        lines.append(f"- `{stage.get('id', '-')}` — **{stage.get('status', '-')}**")
    lines.append('')
    lines.append('## Execution References')
    lines.append('')
    lines.append(f"- **process.sessionId:** {(data.get('process') or {}).get('sessionId')}")
    lines.append(f"- **subtask.sessionKey:** {(data.get('subtask') or {}).get('sessionKey')}")
    lines.append(f"- **cron.jobId:** {(data.get('cron') or {}).get('jobId')}")
    lines.append('')
    lines.append('## Rollback')
    lines.append('')
    rb = data.get('rollback') or {}
    lines.append(f"- **Available:** {rb.get('available')}")
    lines.append(f"- **Strategy:** {rb.get('strategy')}")
    lines.append(f"- **Status:** {rb.get('status')}")
    lines.append('')
    lines.append('## Reporting')
    lines.append('')
    reporting = data.get('reporting') or {
        'mode': 'short-first',
        'preferFileBackedReports': True,
        'longReportPath': None,
    }
    lines.append(f"- **Mode:** {reporting.get('mode')}")
    lines.append(f"- **Prefer File-Backed Reports:** {reporting.get('preferFileBackedReports')}")
    lines.append(f"- **Long Report Path:** {reporting.get('longReportPath')}")
    lines.append('')
    lines.append('## Recent Events')
    lines.append('')
    for event in (data.get('events') or [])[-10:]:
        lines.append(f"- `{event.get('ts', '-')}` `{event.get('type', '-')}` — {event.get('message', '-')}")
    if data.get('result') is not None:
        lines.append('')
        lines.append('## Result')
        lines.append('')
        lines.append('```json')
        lines.append(json.dumps(data['result'], ensure_ascii=False, indent=2))
        lines.append('```')
    if data.get('error') is not None:
        lines.append('')
        lines.append('## Error')
        lines.append('')
        lines.append('```json')
        lines.append(json.dumps(data['error'], ensure_ascii=False, indent=2))
        lines.append('```')
    return '\n'.join(lines) + '\n'


def write_long_report(task_path, data, markdown):
    reporting = data.setdefault('reporting', {
        'mode': 'short-first',
        'preferFileBackedReports': True,
        'longReportPath': None,
    })
    if not reporting.get('preferFileBackedReports', True):
        return None
    output_dir = ((data.get('artifacts') or {}).get('outputDir'))
    if not output_dir:
        return None
    report_path = Path(output_dir) / 'report.md'
    full_path = ROOT / report_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(markdown)
    reporting['longReportPath'] = str(report_path)
    task_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return str(report_path)


if len(sys.argv) < 2:
    die(f"Usage: {Path(sys.argv[0]).name} <taskId> [--format markdown|json|short] [--write-report]")

task_id = sys.argv[1]
fmt = 'markdown'
write_report = False
args = sys.argv[2:]
i = 0
while i < len(args):
    arg = args[i]
    if arg == '--format':
        i += 1
        if i >= len(args):
            die('expected --format markdown|json|short')
        fmt = args[i]
    elif arg == '--write-report':
        write_report = True
    else:
        die(f'unknown argument: {arg}')
    i += 1

task_path, data = load_task(task_id)
markdown = export_markdown(data)
if write_report:
    write_long_report(task_path, data, markdown)
    _, data = load_task(task_id)

if fmt == 'json':
    print(json.dumps(data, ensure_ascii=False, indent=2))
elif fmt == 'markdown':
    print(markdown, end='')
elif fmt == 'short':
    print(short_text(data), end='')
else:
    die('format must be markdown, json, or short')
