# GIT_TROUBLESHOOTING.md

## Troubleshooting GitHub Rule Violations (e.g., Secret Scanning, File Restrictions)

If your push to GitHub is **rejected due to repository rule violations** (such as secret scanning or file restrictions), follow these steps to resolve the issue:

---

## 1. **Read the Error Message Carefully**

- GitHub will often specify the rule violated and the commit/file involved.
- Example error:
  ```
  Push declined due to repository rule violations
  - Push cannot contain secrets
    locations:
      - commit: 00f54f9cb874c1e4e1d29c0df8c71b3876fc5969
        path: .mcp.json:45
  ```

---

## 2. **Understand What `.gitignore` Does (and Doesn’t Do)**

- Adding a file to `.gitignore` **prevents future commits** of that file.
- **It does NOT remove files already committed or erase them from history.**

---

## 3. **Check If the Problem File Was Committed**

Run:
```sh
git log -- 
```
If you see commits listed, the file is in your history.

---

## 4. **Remove the File from Your Latest Commit (If Necessary)**

If you just committed the file and haven’t pushed:
```sh
git rm --cached 
echo  >> .gitignore
git commit -m "Remove  from repository and add to .gitignore"
```
But **this does NOT remove the file from previous commits or your repo history**.

---

## 5. **Remove the File from All Repository History (If Required)**

If the file contains secrets or is flagged by GitHub, you must remove it from all history:

### a. **Clone a Fresh Copy of Your Repository**

```sh
git clone https://github.com//.git cleaned-repo
cd cleaned-repo
```

### b. **Run `git filter-repo` to Remove the File**

```sh
git filter-repo --use-base-name --path  --invert-paths
```
- If prompted, you may need to use `--force`:
  ```sh
  git filter-repo --use-base-name --path  --invert-paths --force
  ```

### c. **Re-add Your Remote (if needed)**

```sh
git remote add origin https://github.com//.git
```

### d. **Force Push the Cleaned History**

```sh
git push origin main --force
```
- This will overwrite the remote repository with your cleaned history.

---

## 6. **Rotate Any Exposed Secrets**

If any secrets (API keys, tokens, passwords) were exposed, **revoke and regenerate them** immediately.

---

## 7. **Verify Success**

- Try pushing again.
- Check the repository on GitHub to confirm the file and secrets are gone from all history.

---

## 8. **Additional Resources**

- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [GitHub: Working with push protection](https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push)
- [git-filter-repo documentation](https://github.com/newren/git-filter-repo)

---

## Quick Reference Table

| Step                        | Command/Action                                              |
|-----------------------------|------------------------------------------------------------|
| Identify violating file      | `git log -- `                                    |
| Remove from latest commit    | `git rm --cached ` + commit                     |
| Remove from all history      | `git filter-repo --use-base-name --path  --invert-paths` |
| Re-add remote                | `git remote add origin `                        |
| Force push                   | `git push origin main --force`                            |
| Rotate secrets               | Regenerate/revoke any exposed credentials                 |

---

**Remember:**  
- Removing sensitive files from history is a destructive operation. Always work on a fresh clone and double-check your results before force-pushing.
- `.gitignore` alone is not enough for files already committed to history.


