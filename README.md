# AI-powered Manuscript Formatter

An intelligent Django web application that uses **NLP and AI** to automatically detect sections in academic manuscripts and reformat them to publication-ready standards (IEEE, APA, MLA, or your own custom style).

---

## What It Does

Upload any raw `.docx` manuscript and the system will:

1. **Read** every paragraph in the document
2. **Detect** which section it belongs to — title, abstract, headings, body, references, etc. — using a three-layer AI pipeline
3. **Apply** the typography rules of your chosen format standard
4. **Return** a fully formatted `.docx` file ready for submission

---

## Features

- **AI-Powered Section Detection** — three-layer NLP pipeline (rules → spaCy → Transformers)
- **3 Built-in Format Templates** — IEEE, APA 7th Edition, MLA 9th Edition
- **Custom Format Builder** — define font, size, alignment, bold/italic/caps per section via a visual UI
- **Section Preview** — AJAX-powered view showing detected labels and confidence scores before downloading
- **15 Section Types Detected** — title, authors, abstract, keywords, headings, subheadings, body, references, figure/table captions, acknowledgements, appendix

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Django 6.x |
| Document Processing | python-docx |
| NLP Layer 1 | Rule-based regex + positional signals |
| NLP Layer 2 | spaCy `en_core_web_sm` (POS tags, NER) |
| NLP Layer 3 | Hugging Face Transformers — `facebook/bart-large-mnli` (zero-shot classification) |
| Frontend | HTML, CSS, Vanilla JavaScript |

---


## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/manuscript-formatter.git
cd manuscript-formatter
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django python-docx spacy torch transformers
python -m spacy download en_core_web_sm
```

### 4. Apply migrations and run

```bash
cd manuscript_formatter
python manage.py migrate
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000**

---

## Usage

### Format with a standard template

1. Go to `http://127.0.0.1:8000`
2. Upload your `.docx` manuscript
3. Select **IEEE**, **APA**, or **MLA** from the dropdown
4. Click **Format and Download** — the formatted file downloads automatically

### Use a custom format

1. Click **Custom Format** link on the main page
2. Expand any section card (Title, Abstract, Heading, Body, etc.)
3. Set font size, alignment, font family, bold/italic/caps for each section
4. Upload your file and click **Format and Download**

### Preview section detection

Before downloading, you can see exactly what the AI detected:

- Send a POST request to `/preview/` with your `.docx` file
- Returns a JSON report with the detected section label and confidence score for every paragraph

---

## NLP Pipeline — How Section Detection Works

The classifier runs three layers in sequence:

```
Paragraph text
      │
      ▼
┌─────────────────────────────────┐
│  Layer 1 — Rule-Based           │  Always runs. Regex patterns +
│  (regex + positional signals)   │  position in document → fast scores
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Layer 2 — spaCy                │  POS tag ratios, named entity types
│  (en_core_web_sm)               │  (PERSON, ORG, DATE) boost scores
└─────────────────┬───────────────┘
                  │
          confidence < 0.75?
                  │ Yes
                  ▼
┌─────────────────────────────────┐
│  Layer 3 — Transformers         │  Zero-shot BART classification.
│  (facebook/bart-large-mnli)     │  Blended 60% rules + 40% model.
└─────────────────┬───────────────┘
                  │
                  ▼
          Final SectionLabel
        (label + confidence score)
```

Layer 3 only runs when the first two layers are uncertain (confidence below 0.75), keeping inference fast for clear-cut sections.

---

## Detected Section Types

| Label | What It Identifies |
|---|---|
| `title` | Paper or document title (first paragraph) |
| `authors` | Author names and affiliations |
| `abstract_heading` | The word "Abstract" as a heading |
| `abstract_text` | Abstract body content |
| `keywords_heading` | The word "Keywords" |
| `keywords_text` | Keyword list content |
| `heading` | Numbered or ALL CAPS section headings |
| `subheading` | Sub-section headings (A., 1.1, etc.) |
| `body` | Main paragraph text |
| `references_heading` | The word "References" or "Bibliography" |
| `references_item` | Individual citation entries |
| `figure_caption` | Fig. 1, Figure 2 captions |
| `table_caption` | Table 1, Table 2 captions |
| `acknowledgements` | Acknowledgements / funding section |
| `appendix` | Appendix or supplementary material |

---

## Format Templates

### IEEE
- Times New Roman throughout
- 10pt body, justified alignment
- 24pt bold centered title
- Headings in ALL CAPS bold

### APA (7th Edition)
- Times New Roman throughout
- 12pt body, left alignment
- 14pt bold centered title
- Centered bold headings for major sections

### MLA (9th Edition)
- Times New Roman throughout
- 12pt body, left alignment
- 12pt plain centered title
- Bold left-aligned headings

### Custom
- Full control over all 15 section types
- Set font family, size, alignment, bold, italic, ALL CAPS independently per section

---

## Generating a Test Document

A sample script is included to generate a realistic raw manuscript for testing:

```bash
python create_sample.py
```

This creates `sample_raw_manuscript.docx` — a plain unformatted document containing all 15 detectable section types (title, authors, abstract, keywords, headings, body, figures, tables, references, acknowledgements).

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/` | Main upload page |
| `POST` | `/format/` | Upload + template name → download formatted `.docx` |
| `POST` | `/format/custom/` | Upload + custom JSON template → download formatted `.docx` |
| `POST` | `/preview/` | Upload → JSON section detection report (no download) |

### Preview endpoint response format

```json
{
  "template": "ieee",
  "paragraphs": [
    {
      "text_preview": "Deep Learning Approaches for Natural Language...",
      "detected_section": "title",
      "confidence": 0.93,
      "signals": ["layer1:rules", "layer2:spacy"]
    }
  ]
}
```

---

## Requirements

```
django>=6.0
python-docx
spacy
torch
transformers
```

---

## Known Limitations

- Input is currently limited to `.docx` files (not PDF or plain text)
- The zero-shot transformer model (`bart-large-mnli`) requires ~1.6 GB of disk space and takes a few seconds to load on first use
- Very unconventional document structures may reduce detection accuracy


## Author
- Pooja Sri G 
- Poorani R 
- Sivani M
- Vasanth R S
- Mukhil Kumar R
