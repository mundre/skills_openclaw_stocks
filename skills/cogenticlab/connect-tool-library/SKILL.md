---
name: connect-tool-library
description: Interact with remote tool libraries via cogenticlink CLI. Use this skill when you need to manage Tool libraries (tokens), browse available tools, and execute tool calls.
metadata:
  openclaw:
    homepage: https://www.npmjs.com/package/cogenticlink
    emoji: 📋
    requires:
      bins:
        - node
        - npx
      config:
        - ~/.cogenticlab/link/config.json
    install:
      - kind: node
        package: "cogenticlink"
        bins:
          - cogenticlink
---

# Connect Tool Library Skill (via cogenticlink CLI)

## Managing Tool Libraries (Tokens)

Before using any tool, you must add a library (API token) using the cogenticlink CLI:

1. Set a library (name, token, optional description): `cogenticlink libraries set <name> <token> [description]`

2. List all libraries (markdown output): `cogenticlink libraries`

3. Remove a library: `cogenticlink libraries remove <name>`

## Executing Tool Calls

All tool commands require the library name as a positional argument.

1. Fetch Tool Categories (markdown output): `cogenticlink categories <library>`. Returns a list of categories.

2. Fetch Tool List of Category (markdown output): `cogenticlink list <library>`. If category is omitted, defaults to All Tools.

3. Obtain Tool Description & Input Schema: `cogenticlink describe <library> <tool>`. Returns Markdown containing the tool's description and JSON schema for parameters.

4. Call a Tool: `cogenticlink call <library> <tool> [parameters]`. parameters is an optional JSON object (default {}). Successful responses return JSON with a content array. Errors return isError: true with details in content.

## Workflow

1. **Check/Create Library** – If no library exists, instruct the user to set one: `cogenticlink libraries set <name> <token> [description]`. If the token is unknown, ask the user to create a tool library in Cogentic Hub.
2. **Fetch Tool Categories** – Run `cogenticlink categories <library>` to see available categories. 
3. **Select a category**, If none selected, use `All Tools` category.
4. **Fetch Tool List from Selected Category** – Run `cogenticlink list <library> <category>` to see tools and their tags.
5. Obtain Tool Description (optional) – Run `cogenticlink describe <library> <tool>` to understand required parameters.
6. **Call Tool** – Run `cogenticlink call <library> <tool> '<json-params>'` to execute.


## Troubleshooting with the CLI
1. Library not found – Run `cogenticlink libraries` to list existing libraries.
2. Invalid token – Re‑set the library with the correct token.
3. Tool not found – Verify the tool name using `cogenticlink list <library>`.
4. Invalid parameters – Check the tool's input schema with `cogenticlink describe <library> <tool>`.
