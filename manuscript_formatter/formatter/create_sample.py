"""
create_sample.py
Run: python create_sample.py
Generates a plain unformatted sample_raw_manuscript.docx to test the formatter.
"""

from docx import Document
from docx.shared import Pt

doc = Document()

paragraphs = [
    "Deep Learning Approaches for Natural Language Processing in Academic Manuscripts",

    "Sarah J. Mitchell, Ph.D., James R. Thompson, M.Sc., Priya K. Sharma, Ph.D.",
    "Department of Computer Science, University of Technology, City, Country",

    "Abstract",

    "This paper presents a comprehensive study of deep learning techniques applied to "
    "natural language processing tasks in academic manuscripts. We explore transformer-based "
    "architectures, convolutional neural networks, and recurrent models to address challenges "
    "in text classification, named entity recognition, and document summarization. Our "
    "experiments on three benchmark datasets demonstrate that the proposed hybrid model "
    "achieves state-of-the-art performance with an average F1-score of 92.4%, outperforming "
    "baseline models by a significant margin.",

    "Keywords: deep learning, natural language processing, transformers, text classification, "
    "named entity recognition",

    "I. Introduction",

    "Natural language processing (NLP) has witnessed remarkable advancements in recent years, "
    "driven largely by the development of deep learning architectures. The ability to "
    "automatically understand, process, and generate human language has opened new frontiers "
    "in applications ranging from machine translation to sentiment analysis. Academic "
    "manuscripts, in particular, present unique challenges for automated processing due to "
    "their domain-specific vocabulary, structured formatting, and complex argumentation patterns.",

    "The proliferation of scientific literature has made it increasingly difficult for "
    "researchers to keep pace with developments in their field. Automated tools for manuscript "
    "analysis, summarization, and classification have therefore become essential. However, "
    "existing approaches often struggle with domain adaptation and specialized terminology.",

    "II. Related Work",

    "Early approaches to document classification relied primarily on bag-of-words models and "
    "term frequency-inverse document frequency (TF-IDF) representations. These methods, while "
    "computationally efficient, failed to capture long-range dependencies and contextual "
    "meaning within text. Support vector machines trained on such representations achieved "
    "reasonable performance on standard benchmarks but showed limited generalization.",

    "A. Transformer-Based Models",

    "The introduction of the Transformer architecture by Vaswani et al. (2017) marked a "
    "paradigm shift in natural language processing. The self-attention mechanism enables the "
    "model to capture dependencies between arbitrary positions in the input sequence. BERT "
    "further advanced the field by introducing bidirectional pre-training on large text corpora.",

    "B. Domain-Specific Adaptations",

    "Several studies have explored domain-specific adaptations of pre-trained language models. "
    "SciBERT, trained on scientific text from Semantic Scholar, demonstrated improved "
    "performance on biomedical and computer science tasks compared to general-domain BERT. "
    "BioBERT achieved superior results on named entity recognition tasks in the clinical domain.",

    "III. Methodology",

    "Our proposed framework consists of three main components: a document preprocessing "
    "pipeline, a hierarchical feature extraction module, and a multi-task classification head. "
    "The preprocessing pipeline handles tokenization, sentence segmentation, and special "
    "character normalization. We employ a sliding window approach for long documents.",

    "The hierarchical feature extraction module operates at two levels: sentence-level "
    "encoding using a pre-trained transformer backbone, and document-level aggregation using "
    "a bidirectional LSTM with attention. This design allows the model to capture both local "
    "semantic information and global document structure simultaneously.",

    "IV. Experiments and Results",

    "We evaluate our model on three publicly available datasets: the ACL Anthology corpus "
    "containing 50,000 computer science papers, the PubMed abstracts dataset comprising "
    "200,000 biomedical documents, and the arXiv preprint collection with 100,000 papers. "
    "Results show our hybrid model achieves an average F1-score of 92.4% across all datasets.",

    "Table 1: Comparison of model performance across benchmark datasets (F1-score %)",

    "Figure 1: Training loss and validation accuracy curves over 10 epochs on ACL Anthology",

    "Error analysis reveals that most misclassifications occur at section boundaries, where "
    "contextual cues from adjacent paragraphs are required for accurate classification. "
    "This observation motivates future work on incorporating document-level context more "
    "explicitly into the classification process.",

    "V. Conclusion",

    "This paper presented a hierarchical deep learning framework for automated section "
    "detection and classification in academic manuscripts. By combining transformer-based "
    "sentence encoding with document-level LSTM aggregation, our model achieves "
    "state-of-the-art performance on multiple benchmark datasets.",

    "Future work will explore multilingual manuscripts, incorporation of PDF layout "
    "information, and development of an end-to-end formatting system. We plan to release "
    "pre-trained models and annotated datasets to facilitate reproducibility.",

    "Acknowledgements",

    "The authors thank the anonymous reviewers for their constructive feedback. This research "
    "was supported by the National Science Foundation under Grant No. NSF-2024-AI-7823. "
    "Computing resources were provided by the High-Performance Computing Center.",

    "References",

    "[1] Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention is all you need. "
    "Advances in Neural Information Processing Systems, 30, 5998-6008.",

    "[2] Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of "
    "deep bidirectional transformers for language understanding. NAACL-HLT 2019, 4171-4186.",

    "[3] Beltagy, I., Lo, K., & Cohan, A. (2019). SciBERT: A pretrained language model for "
    "scientific text. EMNLP-IJCNLP 2019, 3615-3620.",

    "[4] Lee, J., Yoon, W., Kim, S., et al. (2020). BioBERT: A pre-trained biomedical "
    "language representation model. Bioinformatics, 36(4), 1234-1240.",

    "[5] Brown, T., Mann, B., Ryder, N., et al. (2020). Language models are few-shot "
    "learners. Advances in Neural Information Processing Systems, 33, 1877-1901.",
]

for text in paragraphs:
    p = doc.add_paragraph(text)
    # Everything plain — 12pt Calibri, no bold/italic/caps
    for run in p.runs:
        run.font.size     = Pt(12)
        run.font.bold     = False
        run.font.italic   = False
        run.font.all_caps = False
        run.font.name     = "Calibri"

doc.save("sample_raw_manuscript.docx")
print("Created: sample_raw_manuscript.docx")