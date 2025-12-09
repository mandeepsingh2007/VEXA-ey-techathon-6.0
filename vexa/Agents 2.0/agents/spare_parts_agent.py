# agents/spare_parts_agent.py

from __future__ import annotations

import os
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv

from vehicle_master import get_vehicle_meta

load_dotenv()

# RapidAPI (TecDoc Catalog)
TECDOC_BASE_URL = os.getenv("TECDOC_BASE_URL", "https://tecdoc-catalog.p.rapidapi.com")
TECDOC_RAPIDAPI_KEY = os.getenv("TECDOC_RAPIDAPI_KEY")
TECDOC_RAPIDAPI_HOST = os.getenv("TECDOC_RAPIDAPI_HOST", "tecdoc-catalog.p.rapidapi.com")

if not TECDOC_RAPIDAPI_KEY:
    raise RuntimeError(
        "Missing TECDOC_RAPIDAPI_KEY in .env. "
        "Get it from RapidAPI → TecDoc Catalog → X-RapidAPI-Key."
    )

# Map our component types → example TecDoc article numbers
# (These numbers can be replaced with other valid ones from the API docs)
COMPONENT_ARTICLE_MAP: Dict[str, str] = {
    "brake_pad": "0242236561",   # example from your cURL snippet
    "brake": "0242236561",
    "battery": "560410054",      # placeholder example
    "tire": "0358010043",        # placeholder example
    "tyre": "0358010043",
    "engine": "0451103082",      # e.g. an oil filter article
}


class SparePartsAgent:
    """
    Spare Parts Agent backed by TecDoc Catalog (RapidAPI).

    For the prototype we use the 'search-articles-by-article-no' endpoint:

      /artlookup/search-articles-by-article-no/lang-id/4/article-type/ArticleNumber/article-no/{article_no}

    Logic:
    - Map failing component type (brake_pad, battery, etc.) to a sample article number.
    - Call TecDoc to see if this article exists.
    - If API returns data, treat the part as "available".
    - Vehicle metadata is included in the response for context (A + D story),
      even though the HTTP query is based on article number.
    """

    def __init__(self) -> None:
        self.base_url = TECDOC_BASE_URL.rstrip("/")

    # ------------- HTTP helper -------------

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "X-RapidAPI-Key": TECDOC_RAPIDAPI_KEY,
            "X-RapidAPI-Host": TECDOC_RAPIDAPI_HOST,
            "Accept": "application/json",
        }

    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self._headers, params=params or {}, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # ------------- TecDoc call -------------

    def _lookup_article_by_number(self, article_no: str) -> Dict[str, Any]:
        """
        Call TecDoc 'search-articles-by-article-no' endpoint with a given article number.
        """
        path = f"/artlookup/search-articles-by-article-no/lang-id/4/article-type/ArticleNumber/article-no/{article_no}"
        return self._get(path)

    # ------------- Public API used by MasterAgent -------------

    def is_available_for_vehicle(self, vehicle_id: str, component_type: str, qty: int = 1) -> bool:
        """
        Prototype availability check:

        - Lookup article number for the component_type.
        - Call TecDoc.
        - If the call succeeds and returns data, treat as available.
        """
        article_no = COMPONENT_ARTICLE_MAP.get(component_type)
        if not article_no:
            return False

        try:
            data = self._lookup_article_by_number(article_no)
        except Exception:
            return False

        articles = data.get("data") or data.get("articles") or data
        if isinstance(articles, list):
            return len(articles) >= qty
        return bool(articles)

    def reserve_for_vehicle(self, vehicle_id: str, component_type: str, qty: int = 1) -> Dict[str, Any]:
        """
        Prototype 'reservation':
        - Check availability via TecDoc.
        - Return a payload describing what part we recommend.
        """
        article_no = COMPONENT_ARTICLE_MAP.get(component_type)
        vehicle_meta = get_vehicle_meta(vehicle_id)

        available = self.is_available_for_vehicle(vehicle_id, component_type, qty=qty)

        recommendation: Dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "vehicle_meta": vehicle_meta.__dict__ if vehicle_meta else None,
            "component_type": component_type,
            "requested_qty": qty,
            "article_no": article_no,
            "available": available,
        }

        if not article_no:
            recommendation["reason"] = "No article mapping configured for this component_type."

        return recommendation
