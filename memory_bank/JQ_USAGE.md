Great! Your JSON file is a **top-level array** of objects, each with a `tags` array. This means you should use `.[]` (not `.lessons[]`) in your jq queries.

## Example jq Queries

### 1. **Find All Lessons with Specific Tags (case-insensitive)**

To find all lessons where `tags` include `"cli"`, `"typer"`, `"prompt"`, or `"option"` (case-insensitive):

```sh
jq '.[] | select(.tags[] | ascii_downcase | (contains("cli") or contains("typer") or contains("prompt") or contains("option")))' docs/memory_bank/lessons_learned.json
```

#### Explanation:
- `.[]` - iterate over each object in the top-level array.
- `select(.tags[] | ascii_downcase | (contains("cli") or ...))` - select objects where any tag matches (case-insensitive).

---

### 2. **Show Only Title, Problem, and Solution for Matching Lessons**

If you want to show only specific fields:

```sh
jq '.[] | select(.tags[] | ascii_downcase | (contains("cli") or contains("typer") or contains("prompt") or contains("option"))) | {title: ._key, problem, solution, tags}' docs/memory_bank/lessons_learned.json
```

---

### 3. **List All Unique Tags**

To see all unique tags used in your lessons:

```sh
jq '[.[] | .tags[] | ascii_downcase] | unique' docs/memory_bank/lessons_learned.json
```

---

## Common jq Pitfalls (and How to Avoid Them)

- **If your JSON root is an array:** Use `.[]`
- **If your JSON root is an object with a key:** Use `.key[]`
- **For case-insensitive tag matching:** Use `ascii_downcase` before `contains`
- **To avoid errors:** Always check your JSON structure with `jq . file.json` before writing complex queries

---

## Summary Table

| What you want to do                        | jq command                                                                                                    |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Find lessons with "cli", "typer", etc tags | `.[] | select(.tags[] | ascii_downcase | (contains("cli") or contains("typer") ...))`                          |
| Show specific fields                       | `.[] | select(...) | {title: ._key, problem, solution, tags}`                                                 |
| List all unique tags                       | `[.[] | .tags[] | ascii_downcase] | unique`                                                                 |

