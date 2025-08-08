This is a sandbox for getting improved and customized LLM functionality on my iPhone 13.

UI: `Shortcuts for iOS`
Logic: Python / BASH executed via `a-shell`
Sync: For files we'll just use `iCloud` for scripts we'll sync this repo with `Working Copy`

## System  

| TOOL         | ROLE                                                               |
|--------------|--------------------------------------------------------------------|
| Working Copy | Git repository manager on device                                   |
| A-Shell      | Shell interpreter that can run python and shell scripts            |
| iCloud Drive | Bridge between Working Copy and A-Shell (via file provider access) |

### iCloud File directories  

```bash
cd ~/Library/Mobile Documents/com~apple~CloudDocs/
```

### Access Working Copy files from a-Shell

> We can...
> - Manually copy repo files to a location that accessible by `a-shell` and `shortcuts`
> - Use `Working Copy`'s app file provider
> - Use Symlinks or Shell Wrappers
 
1. in `Working Copy` tap on script -> share -> "Export to Files"
2. Choose: `iCloud Drive > a-Shell` folder

then in a-shell:
```bash
cd <wherever this stuff is saved>
python3 <target script>
```
