import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


# ── Feature engineering ───────────────────────────────────────────────────────

def _price_bucket(series: pd.Series) -> pd.Series:
    labels = ["budget", "affordable", "mid-range", "premium", "luxury"]
    try:
        return pd.qcut(series, q=5, labels=labels, duplicates="drop")
    except ValueError:
        return pd.cut(series, bins=5, labels=labels[:5], duplicates="drop")


def _popularity_score(views: pd.Series) -> pd.Series:
    log_v = np.log1p(views.astype(float))
    rng = log_v.max() - log_v.min()
    return (log_v - log_v.min()) / rng if rng > 0 else log_v * 0


def _recency_score(days_ago: pd.Series) -> pd.Series:
    filled = days_ago.fillna(30).astype(float)
    return np.exp(-filled / 30)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns used by the recommender."""
    df = df.copy()
    df["price_bucket"] = _price_bucket(df["Price_MRU"]).astype(str)
    df["popularity_score"] = _popularity_score(df["Views"])
    df["recency_score"] = _recency_score(df.get("Days_Ago", pd.Series(30, index=df.index)))
    df["_text"] = (
        df["Title"].fillna("") + " "
        + df["Location"].fillna("") + " "
        + df["Main_Location"].fillna("") + " "
        + df["price_bucket"]
    )
    return df


# ── Recommender ───────────────────────────────────────────────────────────────

class Recommender:
    """
    Content-Based Filtering with Hybrid Scoring.

    Score = 0.65 * text_similarity
           + 0.15 * price_compatibility
           + 0.12 * popularity_score
           + 0.08 * recency_score
    """

    WEIGHTS = dict(text=0.65, price=0.15, popularity=0.12, recency=0.08)

    def __init__(self, category: str = "real_estate"):
        self.category = category
        self._df: pd.DataFrame | None = None
        self._tfidf = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=8_000,
            sublinear_tf=True,
        )
        self._tfidf_matrix = None

    # ── fit ──────────────────────────────────────────────────────────────────

    def fit(self, df: pd.DataFrame) -> None:
        sub = df[df["Category"] == self.category].copy().reset_index(drop=True)
        sub = engineer_features(sub)
        self._df = sub
        self._tfidf_matrix = self._tfidf.fit_transform(sub["_text"])

    # ── recommend ─────────────────────────────────────────────────────────────

    def recommend(
        self,
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        location: str | None = None,
        top_n: int = 5,
        available_only: bool = True,
    ) -> pd.DataFrame:
        assert self._df is not None, "Call fit() first."
        df = self._df

        # ── hard filters ──
        mask = pd.Series(True, index=df.index)
        if available_only:
            mask &= df["Is_Available"]
        if min_price is not None:
            mask &= df["Price_MRU"] >= min_price
        if max_price is not None:
            mask &= df["Price_MRU"] <= max_price
        if location:
            loc_mask = df["Location"].str.lower().str.contains(location.lower(), na=False)
            if loc_mask.any():
                mask &= loc_mask

        sub_idx = mask[mask].index.tolist()
        if not sub_idx:
            sub_idx = list(range(len(df)))  # fallback: no filter

        # ── text similarity ──
        q_vec = self._tfidf.transform([query])
        text_sims = cosine_similarity(q_vec, self._tfidf_matrix[sub_idx]).flatten()

        # ── price compatibility ──
        prices = df["Price_MRU"].iloc[sub_idx].values
        if max_price and max_price > 0:
            over = np.clip((prices - max_price) / max_price, 0, 1)
            price_compat = 1 - over
        else:
            scaler = MinMaxScaler()
            price_compat = 1 - scaler.fit_transform(prices.reshape(-1, 1)).flatten()

        # ── popularity + recency ──
        popularity = df["popularity_score"].iloc[sub_idx].values
        recency = df["recency_score"].iloc[sub_idx].values

        # ── hybrid score ──
        w = self.WEIGHTS
        score = (
            w["text"] * text_sims
            + w["price"] * price_compat
            + w["popularity"] * popularity
            + w["recency"] * recency
        )

        top_local = min(top_n, len(sub_idx))
        best = np.argsort(score)[-top_local:][::-1]

        result = df.iloc[[sub_idx[i] for i in best]].copy()
        result["hybrid_score"] = score[best]
        result["text_similarity"] = text_sims[best]
        result["score_pct"] = (result["hybrid_score"] * 100).round(1)

        return result[
            [
                "Title", "Price_MRU", "Location", "Main_Location", "Views",
                "Status", "Link", "Image", "Days_Ago",
                "popularity_score", "recency_score", "price_bucket",
                "hybrid_score", "text_similarity", "score_pct",
            ]
        ].reset_index(drop=True)

    # ── evaluation ────────────────────────────────────────────────────────────

    def evaluate(self, test_queries: list[str], k: int = 5) -> dict:
        hits, total = 0, 0
        scores = []
        for q in test_queries:
            res = self.recommend(q, top_n=k)
            if not res.empty:
                hits += (res["hybrid_score"] > 0.1).sum()
                total += len(res)
                scores.append(res["hybrid_score"].mean())
        return {
            "queries_tested": len(test_queries),
            "precision_at_k": round(hits / total, 3) if total else 0,
            "avg_hybrid_score": round(float(np.mean(scores)), 3) if scores else 0,
        }
