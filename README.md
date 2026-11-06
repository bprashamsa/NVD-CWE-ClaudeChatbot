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
