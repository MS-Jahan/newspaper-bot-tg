# Newspaper Bot TG

A Telegram bot that aggregates news and notices from multiple Bangladeshi sources and delivers them to configured Telegram channels.

## Features

### News Sources
- National University Bangladesh (nu.ac.bd) notices
- Prothom Alo (prothomalo.com)
  - General news
  - Science & Technology news
- BBC Bangla (bbc.com/bengali)
- Kaler Kantho (kalerkantho.com) Science & Technology news
- Ridmik News technology section

### Core Features
- Multi-source proxy support for accessing blocked sites
  - HTTP, SOCKS4, and SOCKS5 proxies
  - Integration with proxybd and proxyscrape.com
- Telegraph integration for better reading experience
- Automatic post categorization and tagging
- Health check monitoring integration
- Configurable posting delays and rate limiting
- Error reporting via dedicated Telegram channel

## Setup

1. Clone the repository:
```bash
git clone https://gitlab.com/MS-Jahan/newspaper-bot-sjs.git
cd newspaper-bot-sjs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=main_channel_id
SCIENCE_CHAT_ID=science_channel_id
NATIONAL_UNIVERSITY_CHAT_ID=nu_channel_id
ERROR_MESSAGE_CHAT_ID=error_channel_id
HC_PING_ID=healthcheck_ping_id
```

## Project Structure
- `nunotice.py` - National University notice monitor
- `grab_news.py` - Prothom Alo news aggregator
- `grab_science_news.py` - Prothom Alo science news
- `grab_bbc_news.py` - BBC Bangla news aggregator
- `grab_kalerkontho_science_news.py` - Kaler Kantho science news
- `grab_ridmik_science_news.py` - Ridmik science news
- `helpers.py` - Proxy handling and utility functions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Project Status

Active development - Features and improvements are being added occasionally.
