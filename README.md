# InvestSmartly

InvestSmartly is a beginner-friendly stock analysis app built with Streamlit, focusing on simplicity, reliable investing strategies, and profile-based recommendations inspired by well-known investors.

## Features

- User authentication and personalized recommendations
- Stock analysis with real-time data
- Economic trends overview
- Investor profiles and their investment strategies
- Educational resources for investing terms and concepts
- Advanced filtering options for stock selection
- Notification system for significant market events and stock changes
- Dark mode and advanced mode options

## Technologies Used

- Python
- Streamlit
- yfinance
- Plotly
- pandas
- NumPy
- ta (Technical Analysis Library)

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/InvestSmartly.git
   cd InvestSmartly
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following variables:
   ```
   NOTIFICATION_EMAIL=your_email@example.com
   NOTIFICATION_EMAIL_PASSWORD=your_email_password
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   ```

4. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

## Usage

1. Register for an account or log in if you already have one.
2. Customize your user preferences and notification settings.
3. Explore the different tabs:
   - Stock Analysis: Analyze individual stocks and view personalized recommendations.
   - Economic Trends: Get an overview of current economic trends.
   - Investor Profiles: Learn about different investor strategies and their recommended stocks.
   - Educational Resources: Access a glossary of investing terms and take quizzes to test your knowledge.
4. Use the advanced filtering options to find stocks that match your criteria.
5. Keep an eye on the notification sidebar for important updates on your watchlist and market events.

## Project Structure

- `main.py`: The main Streamlit application file
- `stock_analysis.py`: Functions for stock data retrieval and analysis
- `economic_trends.py`: Economic trends data and analysis
- `investor_profiles.py`: Investor profile information and recommendations
- `user_accounts.py`: User authentication and preference management
- `educational_resources.py`: Investing terms, concepts, and quizzes
- `notifications.py`: Notification system implementation
- `utils.py`: Utility functions
- `style.css`: Custom CSS styles for the Streamlit app

## Contributing

Contributions to InvestSmartly are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Create a pull request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
