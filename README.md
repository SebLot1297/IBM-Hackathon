# ReviewLens

**AI-powered pull request attention triage for IBM Bob**

ReviewLens helps engineers quickly identify which code changes deserve the most review attention.

Instead of treating every pull request change equally, ReviewLens analyzes the change and produces a ranked attention queue that separates routine modifications from changes that may require deeper engineering review.

Built for the **IBM Bob Hackathon**.

---

## Overview

Modern pull requests can contain dozens or hundreds of changed lines, but not every change carries the same engineering risk.

ReviewLens was designed to answer a simple question:

> **Where should an engineer look first?**

The system analyzes code changes and prioritizes them based on signals that suggest a change may deserve additional attention.

Rather than replacing code review, ReviewLens acts as a triage layer that helps reviewers focus their limited attention on the most important parts of a pull request.

---


### Example Output 
This is Output from the neatly generated file. output is also generated in the agent chat

<img width="2832" height="1408" alt="image" src="https://github.com/user-attachments/assets/9e848c55-ce5d-444a-b88d-121491fa04e5" />
<img width="2870" height="1410" alt="image" src="https://github.com/user-attachments/assets/e3cd6823-d10f-4bbb-ba8f-d99df4a67931" />
<img width="2850" height="1404" alt="image" src="https://github.com/user-attachments/assets/f344db7f-9f88-4bcd-831f-6793f5d16e0b" />
<img width="2822" height="1400" alt="image" src="https://github.com/user-attachments/assets/049733f2-5e17-4498-bd1a-fe707629993c" />
<img width="2838" height="1446" alt="image" src="https://github.com/user-attachments/assets/0ec1d543-61d2-4778-b8cd-68ae7854c5de" />



## How It Works

```text
Pull Request / Code Changes
            │
            ▼
┌───────────────────────────┐
│         ReviewLens        │
│                           │
│  Analyze changed code     │
│  Identify review signals  │
│  Rank areas by attention  │
└─────────────┬─────────────┘
              │
              ▼
   Ranked Attention Queue
              │
              ▼
      Engineer Review
