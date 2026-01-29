# Website Evolution Tracker

Track how any website evolved over time using Web Archive data and AI-powered analysis.

## Features

- 📊 **Quarterly Timeline**: See how websites changed quarter by quarter
- 💰 **Revenue Projections**: AI-powered revenue estimates based on business model
- 📝 **Marketing Evolution**: Track changes in messaging, positioning, and value proposition
- 💵 **Pricing Analysis**: Identify pricing strategies even when not visible on the site
- 🚀 **Distribution Channels**: Discover how companies reach their customers

## Setup

1. **Install Dependencies**
```bash
pip3 install -r requirements.txt
```

2. **Set Environment Variable**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. **Run the Application**
```bash
python3 app.py
```

4. **Open Browser**
Navigate to: http://localhost:5000

## How to Use

1. Enter a website domain (e.g., `www.myadorabook.com`)
2. Click "Analyze"
3. Wait 30-60 seconds while the app:
   - Fetches all Web Archive snapshots
   - Organizes them by quarter
   - Uses Claude AI to analyze each snapshot
   - Projects revenue based on business model

## What You'll See

### Top Bar
- **Start Date**: When the business launched
- **Distribution Channels**: How they reach customers
- **Total Quarters**: Number of quarters analyzed

### Timeline
For each quarter, you'll see:
- **Marketing Copy**: Headlines, taglines, key messages
- **Value Proposition**: What problem the company solves
- **Product Focus**: Main products/features promoted
- **Pricing Strategy**: Pricing model and tiers
- **Revenue Projection**: Estimated monthly revenue range
- **Changes**: What changed from previous quarters

## Example Sites to Try

- www.myadorabook.com (Personalized children's books)
- www.stripe.com
- www.notion.so
- www.airbnb.com

## Technical Details

- **Backend**: Python Flask
- **AI**: Claude Sonnet 4.5 (Anthropic)
- **Data Source**: Internet Archive Wayback Machine
- **Analysis**: Quarterly snapshot analysis with revenue modeling

## Notes

- Analysis depends on Web Archive availability
- Revenue projections are AI-estimated (not actual financials)
- JavaScript-heavy sites may have limited content in archives
- Analysis takes 30-60 seconds per website

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Flask Backend  │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌────────┐ ┌──────────┐
│  Web   │ │ Claude   │
│Archive │ │   AI     │
└────────┘ └──────────┘
```

1. User enters domain in browser
2. Flask backend fetches Web Archive snapshots
3. Organizes snapshots by quarter
4. For each quarter:
   - Downloads archived HTML
   - Extracts text content
   - Sends to Claude AI for analysis
5. Claude analyzes:
   - Marketing messaging
   - Product positioning
   - Pricing strategy
   - Revenue projection
6. Results displayed in timeline format

## License

MIT
