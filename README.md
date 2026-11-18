
# PortfolioIQ

<p align="center">
  <img src="assets/banner.png" alt="PortfolioIQ - AI Financial Data Assistant" width="100%">
</p>

**Your financial data is complex. Querying it shouldn't be.**

PortfolioIQ is an AI-powered financial data assistant that lets financial professionals ask questions about complex financial datasets in plain English instead of writing SQL.

From portfolio holdings and account details to historical positions, transactions, tax lots, and financial calculations, PortfolioIQ handles the underlying database queries and brings the results together in a clear, structured response.

It's built to do more than just convert text into SQL. It understands financial data relationships, handles multi-table queries and calculations, maintains conversation context, and uses multiple LLM prompts to break the process into manageable steps.

### How It Works

<details open>
<summary><b>01. User Authentication</b> → Identify the user and access scope</summary>

Users select their role (Advisor or Sponsor Admin) and provide their ID. The application establishes their identity and access context.
</details>

<details>
<summary><b>02. Question Understanding</b> → Decide what to do with the question</summary>

The LLM receives the question, user context, system instructions, and conversation history.

It determines whether to:
- Answer directly
- Query the financial database
- Ask for clarification
- Return a refusal or indicate that it cannot answer
</details>

<details>
<summary><b>03. SQL Query Planning</b> → Understand financial data relationships</summary>

The LLM identifies relevant tables, relationships, joins, filters, aggregations, and calculations needed to answer the question.

PortfolioIQ uses a multi-prompt approach to break down the task, generate parameterized SQL, and handle complex financial queries more reliably.
</details>

<details>
<summary><b>04. Query Execution</b> → Retrieve authorized financial data</summary>

The generated query and its parameters are validated and passed to the database layer for read-only execution, with user access scope applied.
</details>

<details>
<summary><b>05. Answer Generation</b> → Turn database results into meaningful answers</summary>

Retrieved records are passed to a second LLM call, which generates a structured response containing:
- Natural language answer
- Query results
- Supporting evidence
- Assumptions
</details>

<details>
<summary><b>06. Conversation & Usage Tracking</b> → Maintain context across questions</summary>

Conversation history is maintained for contextual follow-up questions. Older messages are periodically summarized to keep the context manageable.

Token usage, API costs, and request metrics are also tracked.
</details>

---

### Setup (Windows)

Clone the repository and install dependencies:

```powershell
git clone https://github.com/sthakur369/PortfolioIQ.git
cd PortfolioIQ

python -m venv myenv
.\myenv\scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key
OPENAI_DEFAULT_MODEL=your_model_name
```

Run the assistant:

```powershell
python main.py
```

Follow the terminal prompts to select a user and start asking questions. Use sample user IDs configured in the database for testing.

---

### Evaluation

Run the evaluation suite:

```powershell
cd eval
python run_eval.py
```

Results are saved to `eval/results.json`, including individual question status, accuracy, latency, and API cost.

**Last recorded results:**

- **Accuracy:** 18/20 (90%)
- **Average latency:** 18.87 seconds
- **Total API cost:** $0.5638
- **Average cost per question:** $0.0282

| Category | Passed |
|---|---:|
| Direct answers | 1/1 |
| Scope | 1/1 |
| Accounts | 2/2 |
| Portfolio | 2/2 |
| Trades | 2/2 |
| Prompt injection | 1/1 |
| Authorization | 1/1 |
| Sponsor admin | 3/3 |
| Households | 1/1 |
| Tax lots | 1/1 |
| Market data | 1/1 |
| Cannot answer | 1/2 |
| Clarification | 1/2 |

---

### What Makes It Different?

- **Built for Financial Data:** Designed around interconnected financial data such as households, advisors, accounts, portfolios, holdings, trades, tax lots, and market prices.
- **Complex Queries & Calculations:** Handles multi-table joins, aggregations, date-based filtering, historical comparisons, and financial calculations through database queries.
- **Multi-Prompt Architecture:** Uses separate LLM prompts for question understanding, query planning, SQL generation, and answer generation rather than trying to do everything in one prompt.
- **Security Guardrails:** Includes safeguards for prompt injection, unauthorized data access, and unsafe database operations.
- **Evidence-Backed Answers:** Responses include supporting database results, assumptions, and relevant evidence rather than relying on the LLM to make up an answer.
- **Conversation Memory:** Understands follow-up questions without requiring users to repeat the entire context.

