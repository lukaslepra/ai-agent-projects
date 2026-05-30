# CLI Task Manager

A lightweight command-line task management tool with JSON persistence.

## Features

- Add tasks with priority levels (`high` / `normal` / `low`)
- List tasks by status (all / pending / done)
- Mark tasks as complete
- Delete tasks
- View statistics
- Data persisted to local JSON file

## Usage

```bash
# Add a task
python todo.py add "Design agent architecture" --priority high

# List pending tasks
python todo.py list

# List all tasks
python todo.py list --all

# Mark complete
python todo.py done 1

# Delete a task
python todo.py delete 2

# View stats
python todo.py stats
```

## Example Output

```
$ python todo.py list --all
All tasks:
  [✓] #1 Design agent architecture (high)
  [ ] #2 Write unit tests (normal)

$ python todo.py stats
📊 Stats: 2 total, 1 done, 1 pending
```

## Tech Stack

- Python 3.8+
- Standard library only (`json`, `os`, `sys`, `datetime`)
- No external dependencies

## Design Notes

- Safe JSON loading with graceful fallback on file corruption
- Auto-incrementing IDs based on current max (no gaps on delete)
- UTF-8 encoding enforced for cross-platform compatibility
- Retry-safe: all writes are atomic per operation