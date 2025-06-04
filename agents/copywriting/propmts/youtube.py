QUERY_KEYWORD_EXPANSION_WITH_HISTORY_PROMPT = """
Following a previous message history, a user created a follow-up question/query.
Please rephrase that question/query as a keyword query \
that would be appropriate for a SEARCH ENGINE. Only use the information provided \
from the history that is relevant to provide the relevant context for the search query, \
meaning that the rephrased search query should be a suitable stand-alone search query.

Here is the relevant previous message history:
{history}

Here is the user question:
{question}

Respond with EXACTLY and ONLY one rephrased query.

Rephrased query for search engine:
""".strip()