import streamlit as st

investing_terms = {
    "Stock": "A share of ownership in a company.",
    "Bond": "A debt security that represents a loan made by an investor to a borrower.",
    "Dividend": "A distribution of a portion of a company's earnings to shareholders.",
    "P/E Ratio": "Price-to-Earnings Ratio, a metric used to value a company's stock.",
    "Market Cap": "The total value of a company's outstanding shares.",
    "Bull Market": "A market condition in which stock prices are rising or expected to rise.",
    "Bear Market": "A market condition in which stock prices are falling or expected to fall.",
    "ETF": "Exchange-Traded Fund, a type of investment fund traded on stock exchanges.",
    "Diversification": "The practice of spreading investments across various financial instruments to reduce risk.",
    "Volatility": "A statistical measure of the dispersion of returns for a given security or market index."
}

investing_concepts = {
    "Value Investing": "An investment strategy that involves picking stocks that appear to be trading for less than their intrinsic or book value.",
    "Growth Investing": "An investment strategy focused on capital appreciation by investing in companies expected to grow at an above-average rate compared to their industry or the overall market.",
    "Dollar-Cost Averaging": "The practice of investing a fixed dollar amount on a regular basis, regardless of the share price.",
    "Asset Allocation": "The implementation of an investment strategy that attempts to balance risk versus reward by adjusting the percentage of each asset in an investment portfolio.",
    "Compound Interest": "The addition of interest to the principal sum of a loan or deposit, or in other words, interest on interest.",
    "Risk Management": "The process of identification, analysis, and acceptance or mitigation of uncertainty in investment decisions.",
    "Market Timing": "The act of attempting to predict future market price movements to buy or sell securities.",
    "Fundamental Analysis": "A method of evaluating securities by attempting to measure the intrinsic value of a stock.",
    "Technical Analysis": "A trading discipline employed to evaluate investments and identify trading opportunities by analyzing statistical trends gathered from trading activity.",
    "Portfolio Rebalancing": "The process of realigning the weightings of a portfolio of assets to maintain a desired level of asset allocation."
}

def display_educational_resources():
    st.markdown('<div class="futuristic-header">Educational Resources</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.subheader("Investing Terms")
    for term, definition in investing_terms.items():
        with st.expander(term):
            st.write(definition)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.subheader("Investing Concepts")
    for concept, explanation in investing_concepts.items():
        with st.expander(concept):
            st.write(explanation)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.subheader("Interactive Quiz")
    if st.button("Take a Quiz"):
        quiz()
    st.markdown('</div>', unsafe_allow_html=True)

def quiz():
    questions = [
        {
            "question": "What is a stock?",
            "options": [
                "A type of bond",
                "A share of ownership in a company",
                "A government-issued currency",
                "A type of mutual fund"
            ],
            "correct_answer": 1
        },
        {
            "question": "What does P/E ratio stand for?",
            "options": [
                "Profit/Earnings Ratio",
                "Price/Equity Ratio",
                "Price-to-Earnings Ratio",
                "Percentage/Evaluation Ratio"
            ],
            "correct_answer": 2
        },
        {
            "question": "What is diversification in investing?",
            "options": [
                "Investing all your money in one stock",
                "Spreading investments across various financial instruments to reduce risk",
                "Investing only in government bonds",
                "Frequently buying and selling stocks"
            ],
            "correct_answer": 1
        }
    ]
    
    score = 0
    for i, q in enumerate(questions):
        st.write(f"Question {i+1}: {q['question']}")
        user_answer = st.radio(f"Select your answer for question {i+1}:", q['options'], key=f"q{i}")
        if user_answer == q['options'][q['correct_answer']]:
            score += 1
    
    st.write(f"Your score: {score}/{len(questions)}")
    if score == len(questions):
        st.success("Congratulations! You got all questions correct!")
    elif score >= len(questions) / 2:
        st.info("Good job! You're on the right track. Keep learning!")
    else:
        st.warning("You might want to review the terms and concepts again. Don't give up!")
