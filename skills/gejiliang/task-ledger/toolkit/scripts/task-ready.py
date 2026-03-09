#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / 'tasks'
SATISFIED = {'succeeded'}
UNSATISFIABLE = {'failed', 'cancelled'}
ACTIVE = {'pending', 'running', 'waiting', 'blocked', 'partial'}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def load_all():
    tasks = {}
    for path in sorted(TASKS_DIR.glob('*.json')):
        try:
            tasks[path.stem] = json.loads(path.read_text())
        except Exception:
            continue
    return tasks


def evaluate(task_id, tasks):
    if task_id not in tasks:
        die(f'Task not found: {task_id}', 2)
    data = tasks[task_id]
    deps = data.get('dependsOn') or []
    missing = []
    unsatisfied = []
    waiting = []
    for dep in deps:
        dep_task = tasks.get(dep)
        if dep_task is None:
            missing.append(dep)
            continue
        dep_status = dep_task.get('status')
        if dep_status in SATISFIED:
            continue
        if dep_status in UNSATISFIABLE:
            unsatisfied.append({'taskId': dep, 'status': dep_status})
        else:
            waiting.append({'taskId': dep, 'status': dep_status})

    if missing:
        readiness = 'missing-deps'
    elif unsatisfied:
        readiness = 'unsatisfied'
    elif waiting:
        readiness = 'waiting-deps'
    else:
        readiness = 'ready'

    return {
        'taskId': task_id,
        'status': data.get('status'),
        'currentStage': data.get('stage'),
        'dependsOn': deps,
        'readiness': readiness,
        'missing': missing,
        'unsatisfied': unsatisfied,
        'waiting': waiting,
    }


if len(sys.argv) not in {2, 3}:
    die(f"Usage: {Path(sys.argv[0]).name} <taskId> [--json]")

task_id = sys.argv[1]
as_json = len(sys.argv) == 3 and sys.argv[2] == '--json'
if len(sys.argv) == 3 and not as_json:
    die('only --json is supported as optional argument')

result = evaluate(task_id, load_all())
if as_json:
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0)

print(f"Task: {result['taskId']}")
print(f"Status: {result['status']}")
print(f"Stage: {result['currentStage']}")
print(f"Readiness: {result['readiness']}")
if result['dependsOn']:
    print('Dependencies:')
    for dep in result['dependsOn']:
        print(f"- {dep}")
if result['missing']:
    print('Missing dependencies:')
    for dep in result['missing']:
        print(f"- {dep}")
if result['unsatisfied']:
    print('Unsatisfied dependencies:')
    for dep in result['unsatisfied']:
        print(f"- {dep['taskId']} [{dep['status']}]")
if result['waiting']:
    print('Waiting on dependencies:')
    for dep in result['waiting']:
        print(f"- {dep['taskId']} [{dep['status']}]")
