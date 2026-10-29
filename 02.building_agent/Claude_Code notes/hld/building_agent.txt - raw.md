To get Claude Code running on your Windows machine, you do not need to download a heavy application from a website. Instead, you install it straight through a terminal command.
Regarding Administrator privileges, you do not strictly need to be an Admin to perform a native user installation. However, having Admin rights can be helpful because if Claude Code needs to install automated system dependencies (like Git) later in the process, a non-admin terminal might block it. Running your terminal as an Administrator prevents these permission errors.
Setting up the agent involves three distinct phases:

Phase 1: Install Git for Windows (Crucial Prerequisite)

Claude Code relies heavily on a terminal language called Bash (which Mac and Linux use by default). Windows uses PowerShell. To bridge this gap, you need Git Bash installed on your computer.
1. Go to the Official Git Download Page.
2. Download the 64-bit Git for Windows Setup.
3. Run the installer. You can safely click "Next" through all the default options without changing anything.

Phase 2: Install Claude Code

1. Click your Windows Start menu, type PowerShell, right-click it, and select "Run as administrator".
2. To download and install Claude Code natively, copy and paste the following official command from Anthropic's Quickstart Docs and hit Enter:powershell
irm https://claude.ai/install.ps1 | iex
Use code with caution.
3. Let the script run. The terminal window may look like it is freezing or showing no progress for a minute while it downloads—this is completely normal. Once it finishes, close that PowerShell window.

Phase 3: Connect Your Folder and Wake Up the Agent

1. Open a fresh PowerShell window.
2. Navigate to the empty project folder you made for your assignment:powershell
cd C:\Path\To\Your\HI634_Assignment_Folder
Use code with caution.
3. Type the magic command to wake up the agent:powershell
claude
Use code with caution.
4. On your very first run, the terminal will print a login link. Copy that link, paste it into your web browser, log into your paid Claude Pro/Console account, and click authorize.
Once authorized, your terminal prompt will change, indicating that Claude Code is officially awake, sitting inside your folder, and waiting for your project prompts!

📊 Setup Roadmap Summary


Component	Target Location / Action	Requirement Note
1. Shell Baseline	Git for Windows	Must be installed first to give the agent Bash tool access.
2. Installation	irm https://claude.ai/install.ps1 | iex	Run inside an elevated Administrator PowerShell prompt.
3. Access Tier	Paid Plan (Pro, Max, or Console API)	The standard free tier of Claude does not support the terminal agent.
4. Initialization	Run claude inside your project folder	The agent is now localized and won't touch files outside this folder.

Let me know once you've tried these steps or if you run into any hiccups!
• Did the PowerShell install script finish successfully?
• Are you logged in and seeing the active Claude terminal prompt?
Once your agent is up, we can move directly to passing it the instructions for the virtual environment and requirements.txt file!
