import datetime

from app.core.deps import get_openai_provider, get_specter2_query_embedder
from app.schemas.search_dto import Paper, SearchResponse


class SearchService:
    """
    Service for managing search requests
    """

    @staticmethod
    def search_papers(query: str) -> SearchResponse:
        """
        Returns a list of matching papers based on the query
        """
        openai_provider = get_openai_provider()
        keywords = openai_provider.extract_keywords(query)

        embedder = get_specter2_query_embedder()
        embeddings = embedder.embed_batch(keywords)

        # Additionally embedd the original query -> could also be used for searching
        embeddings.append(embedder.embed_one(query))

        # Call search module to find matching papers in vector db
        # Needs to be implemented in the future

        # Mock paper as we cannot implement search as of now
        example_paper = Paper(
            paper_id=1,
            doi="some doi",
            source="arXiv",
            paper_type="conference paper",
            title="Deep Reinforcement Learning for Multi-Agent Voting with Approval Preferences",
            authors={"main": "Usain Bolt"},
            abstract="Very good paper about DRL and social choice.",
            published_at=datetime.date.today(),
            pdf_url="some url",
            url="some url",
            fetched_at=datetime.datetime.now(),
        )

        return SearchResponse(papers=[example_paper])
