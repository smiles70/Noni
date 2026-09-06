---
name: work-item-assignment
description: Assign a GitHub work item (issue + optional project board card) directly from this chat
---

# Work Item Assignment from Chat

## Purpose
Let the user turn a chat message into a GitHub issue and assign it to a person who has access to the `smiles70/Noni` repository.

## Chat surface

When the user says any of the following, this skill activates:

- `assign <task> to @<github-username>`
- `create a work item: <task> and assign to @<github-username>`
- `open issue "<title>" for @<github-username>`
- `give <task> to @<github-username>`

## Prerequisites (the skill checks these on every run)

1. `gh auth status` must show a logged-in account.
2. `smiles70/Noni` must have Issues enabled (verified via `gh repo view`).
3. `.ai/config/work-item-config.yaml` must exist and be readable.
4. `.ai/people.yaml` must exist.
5. The assignee must have repository access (verified via `gh api repos/smiles70/Noni/collaborators/{handle}`).
6. A GitHub Project v2 board number must be known if the user wants the issue added to a board.

## What to do

1. **Check `gh` auth.**
   ```bash
   gh auth status
   ```
   If this fails, stop and tell the user to run `gh auth login`.

2. **Load config files.**
   - `.ai/config/work-item-config.yaml`
   - `.ai/people.yaml`

3. **Confirm the repository has Issues enabled.**
   ```bash
   gh repo view smiles70/Noni --json hasIssuesEnabled
   ```

4. **Resolve the assignee.**
   - If the user wrote `@username`, use it directly.
   - If the user wrote a real name or alias, look it up in `.ai/people.yaml` under the `aliases` list.
   - If not found, ask: *"Who should I assign this to? Give me their GitHub username."*

5. **Verify the assignee has repo access.**
   ```bash
   gh api "repos/smiles70/Noni/collaborators/{github-username}" --silent
   ```
   - Exit code `0` → the user can be assigned.
   - Exit code `404` or `403` → tell the user: *"{username} is not a collaborator on smiles70/Noni. Add them first, or choose someone else."*

6. **Confirm or infer the title.**
   Keep it short and action-oriented.

7. **Find the context.**
   - Look at the current open files and recent conversation.
   - Search `.ai/nelson/requirements-knowledge-graph.json` for the closest `Requirement`, `Gap`, `Decision`, or `Capability` node.
   - Look at the most recent `.ai/intake/*.md` file if the task came from an intake.

8. **Handle attachments.**
   - If the user provides a file path or screenshot, check whether it exists and is safe to attach.
   - For images: embed in the issue body using `![alt text](file path)` if the file is in the repo, or copy it to the issue using `gh issue create --body-file` with a markdown image link.
   - For other files: link to the file path or include a short excerpt in the issue body. Do not attach binary or secret files.
   - Supported in this version: image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`) and text files under 1 MB.
   - Never upload files that contain secrets, credentials, or private customer data.

9. **Build the issue body.**

   Template:

   ```markdown
   ---
   **Created from chat:** <today's date>
   **Knowledge-graph node:** <node-id or "none">
   **Related intake:** <path or "none">
   **Related files:** <list>
   **Attachments:** <list or "none">
   ---

   ## Task
   <title>

   ## Context
   <one or two sentences from the chat>

   ## Acceptance criteria
   - [ ] <criterion 1>
   - [ ] <criterion 2>
   ```

10. **Check the budget.**
    Read `.ai/budgets/knowledge-graph-rebuild-001.yaml`. If `consumed_usd >= max_usd`, stop and ask the user for a budget increase.

11. **Create the issue.**
    If `gh` is authenticated and the user confirms, run:
    ```bash
    gh issue create \
      --repo smiles70/Noni \
      --title "<title>" \
      --body-file /tmp/issue-body.md \
      --assignee <github-username> \
      --label "chat-assigned"
    ```
    If `gh` is not available or the user has not confirmed, print the exact `gh` command and ask them to paste it.

12. **Add to the project board (optional).**
    If a project number is known in `.ai/config/work-item-config.yaml`, run:
    ```bash
    gh project item-add <project-number> \
      --owner smiles70 \
      --url https://github.com/smiles70/Noni/issues/<NNN>
    ```
    If the project number is `null`, skip this step and tell the user: *"Project board not configured; issue created but not added to a board."*

13. **Report back.**
    Return the issue number and URL. If the issue could not be created, say why and give the user the command to run manually.

14. **Log the cost.**
    Append a `CostEvent` to `.ai/budgets/knowledge-graph-rebuild-001.yaml`.

## Identity mapping

Use `.ai/people.yaml` to map real names and aliases to GitHub handles. Example:

```yaml
hazbyn:
  github: smiles70
  role: product/owner
  aliases:
    - "haz"
    - "hazby"

kimemiles:
  github: kimemiles
  role: engineering
  aliases:
    - "kimi"
```

If the user says `assign to haz` and `haz` is an alias for `hazbyn`, create the issue with `--assignee smiles70`.

## Safety rules

- Never create an issue without a confirmed title and assignee.
- Never guess a GitHub handle. Ask if it is not in `.ai/people.yaml` and not provided as `@username`.
- Do not assign to a user who does not have repo access.
- Do not use this for infrastructure changes, secret rotation, or irreversible operations — escalate to the user.
- Do not assign work to the assistant itself unless the user explicitly says so.
- Do not run `gh` commands if `gh auth status` fails.
- Do not attach secret, credential, or private customer files.
