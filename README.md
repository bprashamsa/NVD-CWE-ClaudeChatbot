# Security Flaw Chatbot

A chatbot you can ask questions about software security flaws. It looks up real, up-to-date information and tells you how urgent each flaw is.

## What It Does

- Answers questions about known security flaws
- Gives each flaw a risk score from 0 to 100 and a label: Low, Medium, High, or Critical
- Helps you decide what to fix first

The score combines two things: how bad the flaw could be, and how likely hackers are to actually use it. The second part counts more, because a flaw that's being used in real attacks matters more than one that only sounds scary.

## Setup

1. **Make a separate workspace for the project:**
   ```bash
   python -m venv venv
   source venv/bin/activate   #
