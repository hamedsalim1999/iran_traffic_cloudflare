# Iran Traffic Monitor 

Monitor Iran's internet traffic using Cloudflare Radar API and send notifications to Telegram.

## Features

- 📊 Monitors Iran's network traffic volume (NetFlows)
- 📈 Tracks HTTP request trends
- 💬 Sends Telegram notifications when traffic is detected
- 🗄️ Stores historical data in SQLite database
- 🐳 Docker support for easy deployment
- ⏰ Runs automatically every 15 minutes

## Prerequisites

1. **Cloudflare API Token** - Get your token from [Cloudflare Dashboard](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
2. **Telegram Bot** - Create a bot following [Telegram Bot Tutorial](https://core.telegram.org/bots/tutorial)
3. **Python 3.13+** (for local setup) or **Docker** (for containerized setup)

## Quick Start

### Option 1: Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd radar
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the monitor**
   ```bash
   python main.py
   ```

### Option 2: Docker Setup

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Start the container**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container**
   ```bash
   docker-compose down
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Cloudflare Radar API
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token_here
COUNTRY_CODE=IR

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=@your_channel_username

# Database (optional)
DB_PATH=iran_traffic.db
```

### Getting Cloudflare API Token

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **My Profile** → **API Tokens**
3. Click **Create Token**
4. Select **Create Custom Token**
5. Add permissions for **Radar** (Read access)
6. Click **Continue to summary** → **Create Token**
7. Copy the token and add it to your `.env` file

Full guide: https://developers.cloudflare.com/fundamentals/api/get-started/create-token/

### Creating a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to set a name and username for your bot
4. Copy the bot token provided by BotFather
5. Add your bot as an administrator to your channel
6. Use your channel username (e.g., `@blackout`) as `TELEGRAM_CHAT_ID`

Full guide: https://core.telegram.org/bots/tutorial

## Project Structure

```
radar/
├── main.py                 # Main monitoring script
├── test.py                 # Test script for API calls
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .env.example           # Environment variables template
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker compose configuration
├── .gitignore            # Git ignore rules
├── .dockerignore         # Docker ignore rules
├── data/                 # SQLite database volume (Docker)
└── README.md            # This file
```

## Testing

Run the test script to verify your API credentials:

```bash
source venv/bin/activate  # If using local setup
python test.py
```

## Database

The application stores traffic data in a SQLite database with the following schema:

```sql
CREATE TABLE traffic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    traffic_volume REAL NOT NULL,
    traffic_trend REAL NOT NULL
)
```

- **Local setup**: Database stored as `iran_traffic.db` in the project directory
- **Docker setup**: Database stored in `./data/iran_traffic.db` (persisted volume)

Old records are automatically cleaned up (keeps last 100 minutes).

## Telegram Notifications

Notifications are sent to your configured Telegram channel when:
- Traffic trend is greater than 0

Message format:
```
[2026-01-09T09:00:00Z] IR traffic | volume=0.1234 trend=0.5678
```

## Monitoring Schedule

The monitor runs every **15 minutes** and checks traffic data with a 15-minute aggregation interval (minimum supported by Cloudflare Radar API).

## Troubleshooting

### "Unable to authenticate request" error
- Verify your `CLOUDFLARE_API_TOKEN` in `.env` is correct and has Radar read permissions

### "The dateEnd must be after dateStart" error
- This is handled automatically with a 15-minute lag
- If you still see this, the API may be processing data

### Telegram messages not sending
- Ensure your bot is added as an administrator to your channel
- Verify `TELEGRAM_CHAT_ID` starts with `@` for public channels
- Check `TELEGRAM_BOT_TOKEN` is correct

### Docker container not starting
- Check logs: `docker-compose logs`
- Verify `.env` file exists and is properly formatted
- Ensure port 80/443 are not blocked if needed

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for monitoring purposes only. Use responsibly and in accordance with Cloudflare's Terms of Service and Telegram's Bot API Terms.
