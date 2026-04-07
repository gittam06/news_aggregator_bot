# 📰 AI News Aggregator Bot

An automated, cloud-hosted ETL pipeline that fetches the latest news, generates intelligent summaries using Google's Gemini AI, and delivers categorized briefings directly to Telegram. 

Designed to run 24/7 on a serverless architecture using Docker, FastAPI, and Render.

## 🚀 Features

* **Automated Data Extraction:** Scrapes live RSS feeds from major sources (e.g., Yahoo Finance, TechCrunch).
* **AI-Powered Summarization:** Utilizes the `google-genai` library to convert long articles into concise, bulleted digests.
* **Smart Memory Bank:** Implements a rolling `.json` database to track previously sent articles and ensure zero duplicate messages.
* **Automated Delivery:** Sends beautifully formatted markdown messages to a designated Telegram group/channel.
* **Bypass Cloud Paywalls:** Wrapped in a FastAPI web server and triggered by external cron jobs to maintain 100% uptime on free cloud tiers without sleeping.
* **Quota Management:** Built-in batch limiting to safely operate within the Google Gemini API daily limits.

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **Web Framework:** FastAPI, Uvicorn
* **AI Engine:** Google Gemini (Generative AI)
* **Data Processing:** Pandas, Feedparser
* **Deployment & Containerization:** Docker, Render.com
* **Automation:** cron-job.org

## 📂 Project Architecture (ETL Pipeline)

The project is structured around the Extract, Transform, Load (ETL) methodology:

```text
├── app/
│   ├── extract/       # Fetches raw XML/RSS data from news sources
│   ├── transform/     # Cleans data, checks memory bank, and prompts the AI agent
│   └── load/          # Formats the final markdown and triggers the Telegram API
├── run_bot.py         # The FastAPI server and main execution logic
├── Dockerfile         # Container instructions for cloud deployment
└── requirements.txt   # Python dependencies
```

## ⚙️ Environment Variables
To run this project, you must configure the following environment variables in a `.env` file (local) or your cloud provider's dashboard (production):

`LLM_API_KEY` - Your Google Gemini API Key.

`TELEGRAM_BOT_TOKEN` - The token provided by Telegram's BotFather.

`TELEGRAM_CHAT_ID` - The destination Group/Channel ID (include the `-` for supergroups).

`PYTHONUNBUFFERED=1` - Required for Docker/Render to output live console logs.

## 💻 Local Setup
Clone the repository:

```bash
git clone https://github.com/gittam06/news_aggregator_bot.git
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

## ☁️ Cloud Deployment (Render + Cron)
This bot is designed to be deployed as a Dockerized Web Service on Render.com.

1. Connect this repository to Render and deploy as a Docker Web Service.
2. Add your Environment Variables in the Render dashboard.
3. Use a free external trigger service like cron-job.org to ping the `...onrender.com/trigger-news` endpoint on your desired schedule (eg., 9:00 AM and 9:00 PM).

---
*Developed by Gittam Pal*
