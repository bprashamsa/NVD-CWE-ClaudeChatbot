Security Flaw Chatbot

A chatbot you can ask questions about software security flaws. It looks up real, up-to-date information and tells you how urgent each flaw is.

What it does
Answers questions about known security flaws
Gives each flaw a risk score from 0 to 100 and a label: Low, Medium, High, or Critical
Helps you decide what to fix first

The score combines two things: how bad the flaw could be, and how likely hackers are to actually use it. The second part counts more, because a flaw that’s being used in real attacks matters more than one that only sounds scary.

How to set it up
Make a separate workspace for the project:
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
Install what it needs:
   pip install -r requirements.txt
Add your key. Copy the file .env.example and rename the copy to .env. Paste your Anthropic API key into it (you can get one at platform.claude.com). The other key, NVD_API_KEY, is optional and just helps avoid slowdowns.
Start it:
   python main.py

Never share your API key with anyone.

Using it in your browser
Run python web_app.py
Open website.html using the VS Code Live Server extension

No API key? It still works, just with simpler answers.

Things you can ask
CVE-2021-44228
What is the risk of CVE-2021-44228?
How worried should I be about CVE-2024-3094?
What is SQL injection?
CWE-79
What year was Heartbleed discovered?
recent openssl vulnerabilities
What’s in the project
File	What it does
main.py	Starts the chatbot
tools/nvd_tool.py	Looks up flaws in the national database
tools/cwe_tool.py	Looks up types of flaws (like SQL injection)
tools/cvss_tool.py	Gets the official severity score
tools/risk_tool.py	Calculates the 0-100 risk score
tools/utils.py	Small helper functions
How the risk score works

The score is 40% how severe the flaw is, plus 60% how likely it is to be exploited. You can change these percentages in tools/risk_tool.py.

Score	Label
75 or more	Critical
50 to 74	High
25 to 49	Medium
Under 25	Low
