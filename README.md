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


### `chatGPT.py` — Interface & Usage  
`chatGPT.py` is a command-line interface for sending a text prompt to the OpenAI ChatGPT API using a stored conversation history and a locally saved API key. The script reads your API keys from a `config.json` file in the same directory, under the `”keys”` dictionary (with service names like `”ChatGPT”` or `”mistral”`). Conversation history is maintained in a JSON file you provide, allowing for persistent, multi-turn chats.  

**Usage:**  

```bash
python3 chatGPT.py <session_id> <payload_text> <history_file_path> <service_name>
```
Example:

```bash
python3 chatGPT.py session123 “Tell me a joke” history.json ChatGPT
```

The script appends your prompt to the conversation history, sends it to the API, prints the assistant’s reply, and saves the updated history back to the file.



## config.json Format

The config.json file must be located in the same directory as chatGPT.py and should follow this structure:

```json
{
  “keys”: {
    “ChatGPT”: [
      “sk-your-first-openai-key”,
      “sk-your-second-openai-key-if-needed”
    ],
    “mistral”: [
      “mistral-key-1”,
      “mistral-key-2”
    ]
  }
}
```

**keys** — Top-level dictionary containing services as keys.

**Service names** — e.g., “ChatGPT”, “mistral” (match exactly when calling the script).

**Array of keys** — Allows multiple API keys per service (first key is used by default).

>Security Note: Add config.json to your .gitignore file to prevent accidental commits.

