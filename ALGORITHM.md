# Recommendation Algorithm — Real Estate Assistant (Mauritania)

## TL;DR

This system uses **Content-Based Filtering** with a **Hybrid Scoring Function** that combines TF-IDF text similarity, price compatibility, popularity, and recency into a single relevance score.

---

## 1. Why Content-Based Filtering?

The dataset (voursa.com listings) contains **item metadata only** — title, price, location, views, status. There is no user interaction data. This rules out the alternatives:

| Algorithm | Requires | Available? | Verdict |
|---|---|---|---|
| **Collaborative Filtering (User-User)** | User similarity via shared ratings/purchases | ❌ No user accounts | Not applicable |
| **Collaborative Filtering (Item-Item)** | Co-purchase / co-view patterns | ❌ No interaction log | Not applicable |
| **Matrix Factorization (SVD, ALS)** | User × Item interaction matrix | ❌ No interaction data | Not applicable |
| **Neural CF / BERT4Rec** | Large labeled interaction dataset | ❌ Not available | Overkill |
| **Content-Based Filtering** ✅ | Item feature vectors | ✅ Title, price, location, views | **Used here** |
| **Knowledge Graph** | Ontology of property attributes | ⚠️ Partial | Future work |

**Content-Based Filtering** is the only viable option: we describe what the user wants (via conversation) and find the most similar listings using engineered features.

---

## 2. Feature Engineering

Raw columns → engineered feature matrix:

### 2a. Text Features (TF-IDF)

```
text_input = Title + " " + Location + " " + Main_Location + " " + price_bucket_label
```

- **Vectorizer**: `TfidfVectorizer` with **character n-grams (2–4)**
- Character n-grams work well for **Arabic and French** (no tokenization needed)
- `sublinear_tf=True` reduces the weight of very frequent terms
- 8,000 features to capture vocabulary richness without overfitting

Why character n-grams instead of word n-grams?  
→ Arabic morphology is complex (root-based); character-level captures partial matches  
→ French words in Arabic text don't need a French tokenizer  
→ Handles spelling variants naturally

### 2b. Price Features

| Feature | Formula | Purpose |
|---|---|---|
| `price_bucket` | `pd.qcut(Price_MRU, q=5)` → budget / affordable / mid / premium / luxury | Semantic label appended to text |
| `price_normalized` | Min-max within real_estate category | Numerical similarity |
| `price_compatibility` | `1 − clip((price − budget_max) / budget_max, 0, 1)` | Penalise over-budget listings |

### 2c. Popularity Feature

```
popularity_score = normalize(log1p(Views))
```

- `log1p` compresses the extreme range (2 views → 50,000 views)
- Normalized to [0, 1] so it's comparable with other scores
- Acts as a **proxy collaborative signal**: listings viewed by many people tend to be more desirable

### 2d. Recency Feature

```
recency_score = exp(−days_ago / 30)
```

- Exponential decay: a listing posted today scores 1.0, one month ago scores ~0.37, three months ago scores ~0.05
- Prevents stale listings from dominating results

---

## 3. Hybrid Scoring Formula

For a user query **q** and candidate listing **d**:

```
final_score(q, d) = 0.65 × cosine_sim(tfidf(q), tfidf(d))
                  + 0.15 × price_compatibility(q.budget, d.price)
                  + 0.12 × popularity_score(d.views)
                  + 0.08 × recency_score(d.days_ago)
```

### Weight Rationale

| Component | Weight | Reason |
|---|---|---|
| **Text similarity** | 65% | The query (type + location keywords) is the strongest signal |
| **Price compatibility** | 15% | Budget is a hard constraint in real estate |
| **Popularity** | 12% | High-view listings are likely higher quality or better priced |
| **Recency** | 8% | Fresh listings are more likely still available |

---

## 4. Data Cleaning Steps

1. **Price parsing**: strip `MRU`, commas → numeric. Drop rows where price ≤ 1 (placeholder entries).
2. **Outlier removal**: per-category 1st–99th percentile clip (removes data-entry errors like 1,000,000,000 MRU).
3. **Views normalization**: `pd.to_numeric(..., errors='coerce').fillna(0)`.
4. **Location extraction**: regex match against known Mauritanian neighborhoods (Tevragh Zeina, Ksar, Arafat, etc.); fallback to first token.
5. **Deduplication**: drop rows with identical (Title, Price, Main_Location).
6. **Feature engineering**: add `price_bucket`, `popularity_score`, `recency_score`.

---

## 5. Conversational Layer (Mistral Large)

The chatbot adds a **natural language interface** on top of the recommender:

```
User speech / text
      ↓
Mistral Large (multi-turn dialogue)
  – asks: type, budget, location, requirements
  – emits structured <SEARCH>{...}</SEARCH> signal when ready
      ↓
Recommender.recommend(keywords, price_min, price_max, location)
      ↓
Mistral Large (result formatting)
  – generates professional summary of top listings
      ↓
gTTS → voice response
```

Mistral is NOT doing the retrieval — it only:
1. Extracts structured search parameters from conversation
2. Formats the retrieved results into professional prose

---

## 6. Evaluation

**Precision@K proxy**: fraction of top-K results with `cosine_similarity > 0` across a test query set.

| Test Query | Score |
|---|---|
| "villa Tevragh Zeina" | High |
| "cheap apartment Arafat" | High |
| "commercial space downtown" | Medium |
| "land for construction" | Medium |

More rigorous evaluation (NDCG, MAP) would require click-through or purchase labels — not available in this dataset.

---

## 7. Future Improvements

| Improvement | Impact |
|---|---|
| Multilingual sentence-transformers (e.g., `paraphrase-multilingual-MiniLM-L12-v2`) | Better Arabic semantic matching |
| User session logging → implicit CF | Unlock collaborative signals |
| Price-per-m² feature (if area data added) | Fairer comparison across sizes |
| Re-ranking with LLM based on full conversation context | Higher precision for edge cases |
| Map visualization (folium / pydeck) | Better location UX |
