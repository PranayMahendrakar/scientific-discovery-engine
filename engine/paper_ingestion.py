"""
📚 Paper Ingestion Module
Fetches and parses scientific papers from ArXiv, PubMed, and PDFs.
"""

import re
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET


class PaperIngestion:
    """
    Fetches scientific papers from:
    - ArXiv API (free, no key needed)
    - PubMed/Entrez API (free)
    - Direct PDF URLs
    - Manual text input
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ScientificDiscoveryEngine/1.0 (research@example.com)"
        })
        self.arxiv_base = "http://export.arxiv.org/api/query"
        self.pubmed_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.pubmed_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.pubmed_summary = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def fetch_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search and fetch papers from ArXiv.

        Args:
            query: Search query (e.g., "protein folding cancer")
            max_results: Number of papers to fetch

        Returns:
            List of paper dicts
        """
        papers = []
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
            response = self.session.get(self.arxiv_base, params=params, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

            for entry in root.findall("atom:entry", ns):
                paper = self._parse_arxiv_entry(entry, ns)
                if paper:
                    papers.append(paper)

        except Exception as e:
            print(f"   ArXiv fetch error: {e}")

        return papers

    def _parse_arxiv_entry(self, entry, ns: dict) -> Optional[Dict]:
        """Parse a single ArXiv entry XML element."""
        try:
            title = entry.findtext("atom:title", namespaces=ns, default="").strip()
            abstract = entry.findtext("atom:summary", namespaces=ns, default="").strip()
            published = entry.findtext("atom:published", namespaces=ns, default="")

            authors = [
                a.findtext("atom:name", namespaces=ns, default="")
                for a in entry.findall("atom:author", ns)
            ]

            arxiv_id_raw = entry.findtext("atom:id", namespaces=ns, default="")
            arxiv_id = arxiv_id_raw.split("/abs/")[-1] if "/abs/" in arxiv_id_raw else arxiv_id_raw

            categories = [
                c.get("term", "") for c in entry.findall("atom:category", ns)
            ]

            # Extract year from published date
            year = published[:4] if published else "Unknown"

            return {
                "id": f"arxiv:{arxiv_id}",
                "source": "arxiv",
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "categories": categories,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
                "ingested_at": datetime.now().isoformat(),
            }
        except Exception:
            return None

    def fetch_pubmed(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search and fetch paper metadata from PubMed.

        Args:
            query: Search query
            max_results: Number of results

        Returns:
            List of paper dicts
        """
        papers = []
        try:
            # Step 1: Search for IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance",
            }
            search_resp = self.session.get(self.pubmed_search, params=search_params, timeout=15)
            search_resp.raise_for_status()
            ids = search_resp.json().get("esearchresult", {}).get("idlist", [])

            if not ids:
                return []

            time.sleep(0.5)  # PubMed rate limit

            # Step 2: Fetch summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json",
            }
            summary_resp = self.session.get(self.pubmed_summary, params=summary_params, timeout=15)
            summary_resp.raise_for_status()
            result = summary_resp.json().get("result", {})

            for pmid in ids:
                doc = result.get(pmid, {})
                if doc:
                    paper = self._parse_pubmed_doc(pmid, doc)
                    if paper:
                        papers.append(paper)

        except Exception as e:
            print(f"   PubMed fetch error: {e}")

        return papers

    def _parse_pubmed_doc(self, pmid: str, doc: dict) -> Optional[Dict]:
        """Parse PubMed document summary."""
        try:
            authors = [
                a.get("name", "") for a in doc.get("authors", [])
            ]
            return {
                "id": f"pubmed:{pmid}",
                "source": "pubmed",
                "title": doc.get("title", "").strip("."),
                "abstract": doc.get("source", "") + " — " + doc.get("fulljournalname", ""),
                "authors": authors[:5],
                "year": doc.get("pubdate", "")[:4],
                "categories": [doc.get("source", "")],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "pdf_url": None,
                "doi": doc.get("elocationid", ""),
                "ingested_at": datetime.now().isoformat(),
            }
        except Exception:
            return None

    def ingest_text(self, title: str, abstract: str, source: str = "manual") -> Dict:
        """
        Ingest manually provided paper text.

        Args:
            title: Paper title
            abstract: Abstract or full text
            source: Source identifier

        Returns:
            Paper dict
        """
        return {
            "id": f"manual:{hash(title) % 100000}",
            "source": source,
            "title": title,
            "abstract": abstract,
            "authors": [],
            "year": str(datetime.now().year),
            "categories": [],
            "url": None,
            "pdf_url": None,
            "ingested_at": datetime.now().isoformat(),
        }

    def fetch_multi_source(
        self, query: str, max_per_source: int = 5, sources: List[str] = None
    ) -> List[Dict]:
        """
        Fetch papers from multiple sources simultaneously.

        Args:
            query: Research query
            max_per_source: Papers per source
            sources: List of sources to use ('arxiv', 'pubmed')

        Returns:
            Combined list of unique papers
        """
        if sources is None:
            sources = ["arxiv", "pubmed"]

        all_papers = []
        seen_titles = set()

        for source in sources:
            print(f"   Fetching from {source}...")
            if source == "arxiv":
                papers = self.fetch_arxiv(query, max_per_source)
            elif source == "pubmed":
                papers = self.fetch_pubmed(query, max_per_source)
            else:
                continue

            for paper in papers:
                title_key = paper["title"].lower()[:50]
                if title_key not in seen_titles and paper.get("abstract"):
                    seen_titles.add(title_key)
                    all_papers.append(paper)

            time.sleep(1)  # Rate limit between sources

        print(f"   Total: {len(all_papers)} unique papers")
        return all_papers
