# [Project name]

Entry for the [STEM2Connect AI Hackathon 2026](https://stem2connect-online-hackathon.devpost.com/).
Primary track: [Education / Healthcare / Sustainability / Scientific Research / Community Impact]

> Template. Fill each section in before submitting. Devpost requires this README to say what the project does,
> how to run it, and which AI tools or services it uses. The submission deadline is Nov 21, 2026, 11:59 PM EST.

## What it does

## The problem it addresses

## How to run it

These steps use WSL (Linux inside Windows). On the owner's PC, Windows Smart App Control blocks numpy, so we run
everything in WSL. On Linux or macOS, skip step 1 and run the rest in a normal terminal.

1. Open a WSL terminal: press the Windows key, type `wsl`, press Enter.
2. Install uv (it installs Python and the libraries for you). Run this once:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
   Then close the terminal and open a new one, so the `uv` command is found.
3. Go to the project folder, for example:
   `cd /mnt/c/Users/<you>/Documents/stem2connect-2026`
4. Install Python 3.12 and every library the project needs:
   `uv sync`
   The first time takes a few minutes (on a Windows drive, about 3).
5. Run the tests:
   `uv run pytest -q`
   It worked if the last line says `passed` and nothing `failed`.
6. Optional: check the code style with `uv run ruff check .` (it should say `All checks passed!`).

## AI tools and services used
**Inside the project:**

**AI coding assistants (disclosure):** Claude Code (Anthropic). Say what it contributed, what we changed, and what we tested.

## Credits and reused work
Libraries, public datasets and third-party APIs, each with a link and license.
Anything reused from an earlier project, with the project and the date it was written.

## What we learned

## What's next

## Team
