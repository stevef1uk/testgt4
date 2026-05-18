# Task List CLI – Go Spec

## What you're building

A command-line task manager. The user can add tasks, list them, mark them done, and delete them. Tasks persist between runs in a local JSON file.

## Run it

```bash
cd tasklist
go mod tidy
go run ./cmd/tasklist add "Buy milk"
go run ./cmd/tasklist list
go run ./cmd/tasklist done 1
go run ./cmd/tasklist delete 1
```

## File layout

```
tasklist/
├── go.mod
├── cmd/
│   └── tasklist/
│       └── main.go          # CLI entry point
├── internal/
│   ├── store/
│   │   ├── store.go         # Load/save tasks to JSON
│   │   └── store_test.go
│   └── tasks/
│       ├── tasks.go         # Task logic
│       └── tasks_test.go
```

## go.mod

```
module tasklist

go 1.22
```

No external dependencies. Stdlib only.

## Data model

A task is a Go struct serialised to `tasks.json` in the current directory:

```go
type Task struct {
    ID    int64  `json:"id"`
    Title string `json:"title"`
    Done  bool   `json:"done"`
}

type Store struct {
    NextID int64  `json:"next_id"`
    Tasks  []Task `json:"tasks"`
}
```

Example file on disk:

```json
{
  "next_id": 3,
  "tasks": [
    {"id": 1, "title": "Buy milk", "done": false},
    {"id": 2, "title": "Walk dog", "done": true}
  ]
}
```

## Packages

### internal/store/store.go

Handles reading and writing `tasks.json`.

```go
func Load(path string) (*Store, error)
func Save(path string, s *Store) error
```

- If the file does not exist, `Load` returns an empty `&Store{NextID: 1}` with no error.
- `Save` writes JSON with two-space indentation.

### internal/tasks/tasks.go

Pure logic — no file I/O, no `fmt.Print`. All functions take a `*Store` and return an error where appropriate.

```go
func Add(s *Store, title string) (Task, error)
func List(s *Store) []Task
func Complete(s *Store, id int64) (Task, error)
func Delete(s *Store, id int64) (Task, error)
```

Validation rules:
- `title` must be non-empty after `strings.TrimSpace` — return `error` if blank
- `id` must match an existing task — return `error` with a clear message if not found

### cmd/tasklist/main.go

CLI entry point using `os.Args`. No external flag libraries needed; stdlib `flag` package is allowed.

Commands:

| Command | Behaviour |
|---------|-----------|
| `add <title>` | Add a task; print `Added: <title> (id=N)` |
| `list` | Print all tasks; print `No tasks.` if empty |
| `done <id>` | Mark task done; print `Done: <title>` |
| `delete <id>` | Delete task; print `Deleted: <title>` |

Output format for `list`:

```
1. [ ] Buy milk
2. [x] Walk dog
```

On error (bad id, blank title, unknown command): print a short error message to `os.Stderr` and exit with code 1 via `os.Exit(1)`.

Load the store at the start, perform the action, save the store, print the result.

## Tests

### internal/store/store_test.go

- `Load` on a missing path returns an empty store with no error
- `Save` then `Load` round-trips correctly (same tasks, same NextID)
- Use `t.TempDir()` for all file paths — never write to the real `tasks.json`

### internal/tasks/tasks_test.go

- `Add` increases the task count and assigns a unique ID
- `Add` with a blank title returns an error
- `List` returns all tasks
- `Complete` sets `Done` to `true`
- `Complete` with unknown id returns an error
- `Delete` removes the task from the slice
- `Delete` with unknown id returns an error
- Adding two tasks gives them different IDs

## Run tests

```bash
cd tasklist
go test ./...
go vet ./...
```

All tests must pass. No test may write outside `t.TempDir()`.

## Definition of done

1. `go test ./...` and `go vet ./...` pass with no errors
2. `go run ./cmd/tasklist add "Hello"` creates a task and prints confirmation
3. `go run ./cmd/tasklist list` shows it
4. `go run ./cmd/tasklist done 1` marks it complete
5. `go run ./cmd/tasklist delete 1` removes it
6. Running the program twice in a row preserves data between runs
