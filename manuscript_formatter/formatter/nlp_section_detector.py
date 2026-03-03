import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    print("[NLP] spaCy loaded: en_core_web_sm")
except Exception as e:
    SPACY_AVAILABLE = False
    _nlp = None
    print(f"[NLP] spaCy unavailable ({e}) — using rules only")

try:
    from transformers import pipeline as hf_pipeline
    _zero_shot = hf_pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1           # CPU; set 0 for CUDA GPU
    )
    TRANSFORMERS_AVAILABLE = True
    print("[NLP] Transformers zero-shot classifier loaded")
except Exception as e:
    TRANSFORMERS_AVAILABLE = False
    _zero_shot = None
    print(f"[NLP] Transformers unavailable ({e}) — using rules only")

# ── Descriptive labels for zero-shot model ────────────────────────────────────
ZS_LABEL_MAP: Dict[str, str] = {
    "title":              "paper title or document title",
    "authors":            "list of author names or affiliations",
    "abstract_heading":   "section heading that says Abstract",
    "abstract_text":      "abstract or summary paragraph of a research paper",
    "keywords_heading":   "section heading for keywords or index terms",
    "keywords_text":      "list of keywords or index terms",
    "heading":            "main section heading like Introduction or Methodology",
    "subheading":         "sub-section heading",
    "body":               "main body paragraph of a research paper",
    "references_heading": "section heading that says References or Bibliography",
    "references_item":    "individual bibliographic reference entry",
    "figure_caption":     "caption for a figure or image",
    "table_caption":      "caption for a table",
    "acknowledgements":   "acknowledgements or funding statement",
    "appendix":           "appendix or supplementary material heading",
}
_ZS_REVERSE = {v: k for k, v in ZS_LABEL_MAP.items()}
_ZS_LABELS  = list(ZS_LABEL_MAP.values())

ZS_THRESHOLD = 0.75   # confidence below this → invoke zero-shot
ZS_WEIGHT    = 0.40   # zero-shot weight in blended score

# ── Data structures ───────────────────────────────────────────────────────────
@dataclass
class SectionLabel:
    label: str
    confidence: float
    signals: List[str] = field(default_factory=list)

@dataclass
class ParagraphContext:
    index: int
    total_paragraphs: int
    prev_label: Optional[str] = None

# ── Regex patterns ────────────────────────────────────────────────────────────
_ABSTRACT_KW    = re.compile(r"^(abstract|summary|overview)\s*[:\-\u2013\u2014]?$", re.I)
_KEYWORDS_KW    = re.compile(r"^(keywords?|index\s+terms?)\s*[:\-\u2013\u2014]?", re.I)
_REFERENCES_KW  = re.compile(r"^(references?|bibliography|works\s+cited)\s*[:\-\u2013\u2014]?$", re.I)
_ACK_KW         = re.compile(r"^(acknowledg(e)?ments?|funding|conflict\s+of\s+interest)", re.I)
_APPENDIX_KW    = re.compile(r"^(appendix|appendices)\s*[A-Z]?\s*[:\-\u2013\u2014]?$", re.I)
_FIGURE_KW      = re.compile(r"^(fig\.?|figure)\s*\d+", re.I)
_TABLE_KW       = re.compile(r"^table\s*\d+", re.I)
_NUMBERED_HDG   = re.compile(r"^(\d+(\.\d+)*|[IVXLC]+\.|[A-Z]\.)\s+", re.I)
_REFERENCE_ITEM = re.compile(r"^(\[\d+\]|\d+\.\s+[A-Z]|[A-Z][a-z]+,\s+[A-Z]\.)")
_AUTHOR_PATTERN = re.compile(r"([A-Z][a-z]+,?\s+[A-Z]\.\s*,?\s*){2,}|et\s+al\.", re.I)


# ── Layer 1: Rule-based scorer ────────────────────────────────────────────────
def _rule_scores(text: str, ctx: ParagraphContext) -> Dict[str, float]:
    s = text.strip()
    if not s:
        return {"blank": 1.0}

    scores: Dict[str, float] = {}
    word_count  = len(s.split())
    is_short    = word_count <= 12
    is_long     = word_count > 35
    is_all_caps = s.isupper() and len(s) > 3
    ends_period = s.endswith(".")
    rel_pos     = ctx.index / max(ctx.total_paragraphs - 1, 1)

    if ctx.index == 0 and is_short:
        scores["title"] = 0.90
    if ctx.index == 1 and _AUTHOR_PATTERN.search(s):
        scores["authors"] = 0.90
    if _ABSTRACT_KW.match(s):
        scores["abstract_heading"] = 0.98
    if ctx.prev_label in ("abstract_heading", "abstract_text"):
        if not _KEYWORDS_KW.match(s) and not _NUMBERED_HDG.match(s):
            scores["abstract_text"] = 0.85
    if _KEYWORDS_KW.match(s):
        scores["keywords_heading"] = 0.97
    if ctx.prev_label == "keywords_heading":
        scores["keywords_text"] = 0.90
    if _REFERENCES_KW.match(s):
        scores["references_heading"] = 0.99
    if ctx.prev_label in ("references_heading", "references_item"):
        if _REFERENCE_ITEM.match(s):
            scores["references_item"] = 0.95
        elif word_count > 10:
            scores["references_item"] = 0.70
    if _ACK_KW.match(s):
        scores["acknowledgements"] = 0.96
    if _APPENDIX_KW.match(s):
        scores["appendix"] = 0.95
    if _FIGURE_KW.match(s):
        scores["figure_caption"] = 0.96
    if _TABLE_KW.match(s):
        scores["table_caption"] = 0.96
    if _NUMBERED_HDG.match(s) and is_short:
        scores["heading"] = max(scores.get("heading", 0), 0.90)
    if is_all_caps and is_short:
        scores["heading"] = max(scores.get("heading", 0), 0.88)
    if is_short and not ends_period and rel_pos > 0.05 and not scores:
        scores["subheading"] = 0.50
    if is_long and ends_period:
        scores["body"] = max(scores.get("body", 0), 0.80)
    if not scores:
        scores["body"] = 0.55

    return scores


# ── Layer 2: spaCy feature booster ───────────────────────────────────────────
def _spacy_boost(text: str, ctx: ParagraphContext, scores: Dict[str, float]) -> Dict[str, float]:
    doc     = _nlp(text)
    tokens  = [t for t in doc if not t.is_space]
    n       = len(tokens)
    if n == 0:
        return scores

    ent_labels = {ent.label_ for ent in doc.ents}
    has_verb   = any(t.pos_ == "VERB" for t in tokens)
    noun_ratio = sum(1 for t in tokens if t.pos_ in ("PROPN", "NOUN")) / n
    sent_count = sum(1 for _ in doc.sents)

    # Title: mostly nouns/proper nouns, no verb, first paragraph
    if ctx.index == 0 and noun_ratio > 0.4 and not has_verb:
        scores["title"] = max(scores.get("title", 0), 0.93)

    # Author line: PERSON entities near the top
    if "PERSON" in ent_labels and ctx.index <= 3:
        scores["authors"] = max(scores.get("authors", 0), 0.88)

    # Affiliations: ORG entities near the top
    if "ORG" in ent_labels and ctx.index <= 5:
        scores["authors"] = max(scores.get("authors", 0), 0.70)

    # Body: verbs + multiple sentences
    if has_verb and sent_count >= 2:
        scores["body"] = max(scores.get("body", 0), 0.75)

    # Reference items: DATE/ORDINAL inside reference context
    if ("DATE" in ent_labels or "ORDINAL" in ent_labels) and n < 60:
        if ctx.prev_label in ("references_heading", "references_item"):
            scores["references_item"] = max(scores.get("references_item", 0), 0.80)

    return scores


# ── Layer 3: Transformers zero-shot ──────────────────────────────────────────
def _zeroshot_classify(text: str) -> Dict[str, float]:
    result = _zero_shot(text[:512], candidate_labels=_ZS_LABELS, multi_label=False)
    out: Dict[str, float] = {}
    for label, score in zip(result["labels"], result["scores"]):
        internal = _ZS_REVERSE.get(label)
        if internal:
            out[internal] = round(float(score), 4)
    return out


# ── Combined classifier ───────────────────────────────────────────────────────
class NLPSectionDetector:
    def classify(self, text: str, ctx: ParagraphContext) -> SectionLabel:
        stripped = text.strip()
        if not stripped:
            return SectionLabel("blank", 1.0, ["empty paragraph"])

        signals: List[str] = []

        # Layer 1
        scores = _rule_scores(stripped, ctx)
        signals.append("layer1:rules")

        # Layer 2
        if SPACY_AVAILABLE:
            scores = _spacy_boost(stripped, ctx, scores)
            signals.append("layer2:spacy")

        best_label = max(scores, key=scores.__getitem__)
        best_conf  = scores[best_label]

        # Layer 3 — only when confidence is low
        if (TRANSFORMERS_AVAILABLE
                and best_conf < ZS_THRESHOLD
                and len(stripped.split()) > 4):
            try:
                zs = _zeroshot_classify(stripped)
                zs_top = max(zs, key=zs.get)
                signals.append(f"layer3:zero-shot={zs_top}({zs[zs_top]:.2f})")
                # Blend scores: 60% rule/spaCy + 40% zero-shot
                for lbl, zs_score in zs.items():
                    scores[lbl] = round(
                        scores.get(lbl, 0.0) * (1 - ZS_WEIGHT) + zs_score * ZS_WEIGHT, 4
                    )
                best_label = max(scores, key=scores.__getitem__)
                best_conf  = scores[best_label]
            except Exception as e:
                signals.append(f"layer3:failed({e})")

        return SectionLabel(best_label, round(min(best_conf, 1.0), 3), signals)


# ── Document-level entry point ────────────────────────────────────────────────
def classify_document(paragraphs: List[str]) -> List[SectionLabel]:
    detector = NLPSectionDetector()
    labels: List[SectionLabel] = []
    total = len(paragraphs)

    for i, text in enumerate(paragraphs):
        prev_label = labels[i - 1].label if i > 0 else None
        ctx = ParagraphContext(index=i, total_paragraphs=total, prev_label=prev_label)
        labels.append(detector.classify(text, ctx))

    return labels