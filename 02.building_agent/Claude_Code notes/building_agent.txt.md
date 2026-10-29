
## .md create with Gemini prompt:

    If I send you a bunch of text, can you convert it into a really nice .md code?

---

# Claude Code Setup Guide for Windows

To get **Claude Code** running on your Windows machine, you do not need to download a heavy application from a website. Instead, you install it straight through a terminal command.

Regarding **Administrator privileges**, you do not strictly need to be an Admin to perform a native user installation. However, having Admin rights can be helpful because if Claude Code needs to install automated system dependencies (like Git) later in the process, a non-admin terminal might block it. Running your terminal as an Administrator prevents these permission errors.

---

## ⚙️ The Three Setup Phases

### Phase 1: Install Git for Windows (Crucial Prerequisite)
Claude Code relies heavily on a terminal language called **Bash** (which Mac and Linux use by default). Windows uses PowerShell. To bridge this gap, you need Git Bash installed on your computer.

1. Go to the [Official Git Download Page](https://git-scm.com).
2. Download the **64-bit Git for Windows Setup**.
3. Run the installer. You can safely click **"Next"** through all the default options without changing anything.

### Phase 2: Install Claude Code
1. Click your Windows **Start menu**, type `PowerShell`, right-click it, and select **"Run as administrator"**.
2. To download and install Claude Code natively, copy, paste, and hit **Enter** on the following official command from Anthropic's Quickstart Docs:
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
3. Let the script run. The terminal window may look like it is freezing or showing no progress for a minute while it downloads—this is **completely normal**. Once it finishes, close that PowerShell window.

### Phase 3: Connect Your Folder & Wake Up the Agent
1. Open a **fresh** PowerShell window.
2. Navigate to the empty project folder you made for your assignment:
   ```powershell
   cd C:\Path\To\Your\HI634_Assignment_Folder
   ```
3. Type the magic command to wake up the agent:
   ```powershell
   claude
   ```
4. On your **very first run**, the terminal will print a login link. Copy that link, paste it into your web browser, log into your paid **Claude Pro/Console account**, and click authorize.

Once authorized, your terminal prompt will change, indicating that **Claude Code is officially awake**, sitting inside your folder, and waiting for your project prompts!

---

## 📊 Setup Roadmap Summary

| Component | Target Location / Action | Requirement Note |
| :--- | :--- | :--- |
| **1. Shell Baseline** | Git for Windows | Must be installed first to give the agent Bash tool access. |
| **2. Installation** | `irm https://claude.ai/install.ps1 \| iex` | Run inside an elevated Administrator PowerShell prompt. |
| **3. Access Tier** | Paid Plan (Pro, Max, or Console API) | The standard free tier of Claude does not support the terminal agent. |
| **4. Initialization** | Run `claude` inside your project folder | The agent is now localized and won't touch files outside this folder. |

---

### Next Steps & Feedback
Let me know once you've tried these steps or if you run into any hiccups!
* Did the PowerShell install script finish successfully?
* Are you logged in and seeing the active Claude terminal prompt?

*Once your agent is up, we can move directly to passing it the instructions for the virtual environment and `requirements.txt` file!*


<br>

---

<br>

# Issues when setting up Claude:

1.	Do I need to add the path for Anthropic's install to the PATH?


    Yes, you absolutely must add that exact folder path to your User PATH environment variable.

        powershell

        [Environment]::SetEnvironmentVariable("PATH", [Environment]::GetEnvironmen

  <br> 

      _I set up the Path manually through the Environment PATH settings._


2.  Navigate to path for Project:

        T:\

        cd\
        cd HI_634\Project_Assignments\Project_01\HI-634-Assignment_1-Health-Data-Science-Project\project


3.  The Agent didn't wake up.  A paid subscription may be required.

      > claude

      PS T:\HI_634\Project_Assignments\Project_01\HI-634-Assignment_1-Health-Data-Science-Project\project> claude


          Welcome to Claude Code v2.1.312
          ..........................................................

              *                                       █████▓▓░
                                          *         ███▓░     ░░
                      ░░░░░░                        ███▓░
              ░░░   ░░░░░░░░░░                      ███▓░
            ░░░░░░░░░░░░░░░░░░░    *                ██▓░░      ▓
                                                      ░▓▓███▓▓░
          *                                 ░░░░
                                          ░░░░░░░░
                                        ░░░░░░░░░░░░░░░░
                █████████                                        *
                ██▄█████▄██                        *
                █████████      *
          .......█ █   █ █..........................................

          Unable to connect to Anthropic services

          Failed to connect to api.anthropic.com: Status 403

          Please check your internet connection and network settings.

          Note: Claude Code might not be available in your country. Check supported countries at
          https://anthropic.com/supported-countries


    PS T:\HI_634\Project_Assignments\Project_01\HI-634-Assignment_1-Health-Data-Science-Project\project>


    I asked Gemini:

    My agent did not wake up. Do I need to create an account first? "Unable to connect to Anthropic services Failed to connect to api.anthropic.com: Status 403"


    Yes, you must create and fund an Anthropic API Console account to use Claude Code.

    The standard consumer "Claude Pro" web subscription ($20/month) does not cover Claude Code. Because the agent runs directly on your computer's terminal and makes rapid background calls to process files, Anthropic bills it as a developer tool using a pay-as-you-go API keys account.

    The Status 403 error you are seeing means Anthropic's servers are explicitly blocking your terminal because it doesn't detect a funded developer account linked to it.

    Here is exactly how to fix this and get your agent to wake up:

    * Step 1: Create an Anthropic Console Account

      1. Go to the Anthropic Developer Console.
      2. Sign up using your email (you can use the same email as your regular Claude account, but the developer backend is separate).

    * Step 2: Add Initial Funds (Credits)

        1. Once logged into the Console, look at the top menu and click on the Billing tab.
        2. Click Claim Free Credits if a pop-up appears (Anthropic often gives $5 inside new developer accounts, which is more than enough to complete this entire assignment).
        3. If no free credits are available, click Add Funds. You only need to load a tiny amount—$5.00 or $10.00 is plenty.

    * Step 3: Authenticate in Your Windows Terminal

      Once your console account has a cash balance, go back to your Windows PowerShell window inside your project folder and run this specific login command:
      powershell
      claude login
      Use code with caution.
      This will open your web browser, look for your active developer console session, and link your terminal.
      Once that link completes, type claude again, and the agent will wake up without the 403 error!


