I want to turn a course PDF into an interactive 3D pop-up book using PopBook Studio (https://github.com/AlphaaCode/Popbook). Please do the whole setup and build for me, step by step, and explain anything in plain words (I'm not a developer).

1. Check that Node.js 18+ is installed (`node -v`). If not, tell me exactly how to install the LTS version for my operating system, and wait for me to confirm before continuing.
2. Clone the repo into a folder called Popbook (use git; if git is missing, download the ZIP from GitHub and extract it). If the folder already exists, run `git pull` instead.
3. In that folder, run `npm install`.
4. Read the repo's README.md, CLAUDE.md / AGENTS.md and prompts/system.md so you follow the project's own rules for generating a book.
5. Ask me for: the full path to my PDF, the page range (default 1-10), the book language (default: same as the source), and any extra instructions (level, tone).
6. Generate the book exactly as the project's `/popup-book path/to/lesson.pdf 1-10` workflow does: write books/<name>/book.json, then validate it with `npm run check`. Fix any errors yourself.
7. Start the server with `npm start` in the background, and tell me to open http://localhost:5173 and click my book under "Your books".
8. Finish with: where the book is saved (books/<name>), how to download it as a single HTML file to share, and the 3 commands I need next time (open terminal in the Popbook folder, `npm start`, open localhost:5173).

Rules: stay faithful to my PDF's content, never ask me to paste an API key into this chat, and stop and ask me if something needs my decision.