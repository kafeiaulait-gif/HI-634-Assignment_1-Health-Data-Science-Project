

### It is completely normal to feel like you are missing something here. The assignment assumes you have already been introduced to a specific tool called an AI Coding Agent.

<br>

* An AI coding agent is different from regular ChatGPT or standard Claude. While regular ChatGPT can only write code text for you to copy and paste, a coding agent is a specialized AI program running inside your computer's terminal or code editor that can actually create files, type commands, and run Python programs on its own.

<br>

---

Here is exactly what your professor is talking about and how you actually get started:

* What "Agent" is he talking about?

	In your first snippet, the assignment explicitly listed the tools you are allowed to use: Codex, Claude Code, Antigravity, or OpenCode.
	Most students in university data science courses right now use Claude Code (a command-line tool made by Anthropic) or tools integrated into VS Code (like GitHub Copilot Workspace or OpenCode variants). These tools connect an AI model directly to a folder on your computer.


---

#### I'm doing a simple project for school. Are any of these AI agents free? Which would would be best to use? I'm going to download a patient set and do some analysis with it, using prompts: Codex, Claude Code, Antigravity, or OpenCode.


	For your school project, Google Antigravity and OpenCode are the best free options because they offer robust public previews or open-source local configurations at zero cost. In contrast, Codex and Claude Code require active paid subscriptions to their respective ecosystems (ChatGPT Plus/Pro/Team or Claude Pro) to use their native terminal agents out of the box.
	For a school data analysis project involving prompting and python datasets, Google Antigravity is your best choice. It provides a managed Linux sandbox environment right out of the box that natively executes Python code.

---

### Deep Dive into Your Options


1. Google Antigravity (Top Recommendation)

	* Cost: Free. Google offers Antigravity at no cost for individuals during its public preview, giving you generous, free rate limits on Gemini 3 Pro.
	* How it fits your project: It is excellent for data analysis. A single agent call sets up an environment that reasons, manages your dataset files, and autonomously writes and executes Python data analysis scripts inside a secure, Google-hosted Linux sandbox.
	* Platform options: You can download the standalone Antigravity App desktop client (macOS, Windows, Linux), use the VS Code-based Antigravity IDE, or code it directly in Python using the Gemini API in Google AI Studio.

2. OpenCode

	* Cost: Free / Model-Dependent. The agent harness itself is entirely open-source. You can download it via the terminal and use it for free by connecting it to a free API key (like Google AI Studio's Gemini tier) or running completely free local models via Ollama.
	* How it fits your project: If you enjoy tinkering with terminal interfaces (TUIs), OpenCode is highly flexible. However, setting up the API keys or local model bridges requires an intermediate level of technical setup, which might add unnecessary friction to a simple school project.

3. OpenAI Codex

	* Cost: Paid. While it is a powerhouse for repository management and running multi-agent workflows in parallel cloud sandboxes, it is only available to paying users. It requires an active ChatGPT Plus, Pro, Edu, or Enterprise plan and lives inside the ChatGPT desktop app.

4. Claude Code (Anthropic)

	* Cost: Paid. Anthropic's official terminal agent requires a paid Claude Pro ($20/month) or Team subscription tier to be authorized. While developers have created independent, open-source proxy workarounds to redirect the CLI to free models, the native out-of-the-box experience is locked behind a paywall.

---


### Step-by-Step Approach for Your Project

Since you are analyzing a patient dataset using prompts, follow this path using Google Antigravity:

1. Go to the Google Antigravity Portal and download the desktop client for your operating system.
2. Open the app and sign in with your regular Google account.
3. Create a new "Project" folder and drop your patient dataset (e.g., a .csv or .xlsx file) directly into it.
4. Prompt the agent in plain English: "Look at this patient dataset. Write a Python script to check for missing values, calculate the averages for each demographic, and plot a distribution of the patient outcomes. Run the script and show me the results."
5. The agent will spin up the secure sandbox, write the code, execute it, handle any debugging automatically, and present you with the completed analysis.

<br>


	Google Antigravity is a standalone desktop application rather than a command-line terminal agent like Claude Code. While Claude Code installs directly into your local terminal via npm and executes commands line-by-line, Google Antigravity functions as a complete "Agent Platform" or specialized IDE.
	
	You download it as a traditional application (packaged as a .dmg for Mac, .exe for Windows, or .deb/.rpm for Linux). Once installed, it provides a full graphical user interface where you can chat with agents, drop files into custom workspaces, and visually watch the agent execute code, run terminal tasks, and handle data analysis within a sandboxed environment.


<br>
<br>



