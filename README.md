# 📰 AI News Aggregator Bot

An automated, cloud-hosted ETL pipeline that fetches the latest global news, generates intelligent summaries using Google's Gemini AI, and delivers categorized briefings directly to specific Topics in a Telegram Supergroup. 

Designed to run 24/7 on a serverless architecture using Docker, FastAPI, Render, and GitHub Actions.

## 🚀 Features

* **Global Data Extraction:** Scrapes massive, live RSS aggregators from Google News to capture the most critical daily stories.
* **The "Big 4" AI Categorization:** Utilizes the Google Gemini API to intelligently read and sort every article into four master categories: *Markets & Economy*, *Tech & Innovation*, *Corporate Moves*, and *Business Trends*.
* **Telegram Topic Routing:** Automatically routes the formatted markdown digests into their specific, dedicated sub-folders (Topics) within a Telegram group for a premium reading experience.
* **Smart Memory Bank:** Implements a rolling `.json` database to track previously sent articles and ensure zero duplicate messages across runs.
* **Bulletproof Quota Management:** Features a custom 3-strike retry loop, strategic sleep timers, and console tracking to safely maximize the Google Gemini Free Tier without ever crashing from "429 Rate Limit" errors.
* **Automated Scheduling:** Utilizes GitHub Actions to ping the server on a precise, automated schedule (e.g., 8:00 AM and 7:00 PM) while bypassing cloud paywall sleep-states.

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **Web Framework:** FastAPI, Uvicorn
* **AI Engine:** Google Gemini 2.5 Flash (`google-generativeai`)
* **Data Processing:** Pandas, Feedparser
* **Deployment & Containerization:** Docker, Render.com
* **Automation:** GitHub Actions

## 📂 Project Architecture (ETL Pipeline)

The project is structured around the Extract, Transform, Load (ETL) methodology:

```text
├── .github/workflows/
│   └── trigger.yml    # GitHub Actions configuration for scheduled automation
├── app/
│   ├── extract/       # Fetches raw XML/RSS data from Google News
│   ├── transform/     # Cleans data, checks memory, and prompts Gemini for categorizations
│   └── load/          # Routes the final markdown to exact Telegram Topic IDs
├── run_bot.py         # The FastAPI server, scheduling, and retry logic
├── Dockerfile         # Container instructions for cloud deployment
└── requirements.txt   # Python dependencies
```

## ⚙️ Environment Variables
To run this project, you must configure the following environment variables in a `.env` file (local) or your cloud provider's dashboard (production):

`GEMINI_API_KEY` - Your Google Gemini API Key.

`TELEGRAM_BOT_TOKEN` - The token provided by Telegram's BotFather.

`TELEGRAM_CHAT_ID` - The destination Supergroup ID (include the `-100` prefix).

`PYTHONUNBUFFERED=1` - Required for Docker/Render to output live console logs.

*(Note: Telegram Topic IDs are hardcoded in the `TOPIC_MAP` inside `app/load/telegram_bot.py`)*

## 💻 Local Setup
Clone the repository:

```bash
git clone [https://github.com/gittam06/news_aggregator_bot.git](https://github.com/gittam06/news_aggregator_bot.git)
cd news_aggregator_bot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up your environment variables in a `.env` file.

Run the server:

```bash
python run_bot.py
```
The bot will start a local web server. Visit `http://localhost:10000/trigger-news` in your browser to test the pipeline.

## ☁️ Cloud Deployment (Render + GitHub Actions)
This bot is designed to be deployed as a Dockerized Web Service on Render.com, triggered by GitHub Actions.

1. Connect this repository to Render and deploy as a Docker Web Service.
2. Add your Environment Variables in the Render dashboard.
3. Configure your `.github/workflows/trigger.yml` file to hit your Render URL (`https://your-app-name.onrender.com/trigger-news`) at your desired times using CRON syntax.
4. Push to GitHub. The Actions tab will now automatically execute the pipeline on schedule or via the manual "Run workflow" button.

---
*Developed by Gittam Pal*
