import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

# Download once (safe even on Railway)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")

def generate_summary(text, max_sentences=5):
    """
    Extractive summarization (NO AI, NO API)
    """
    if not text or len(text.split()) < 50:
        return "Text is too short to summarize."

    text = re.sub(r"\s+", " ", text)

    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    stop_words = set(stopwords.words("english"))

    # Word frequency
    freq = {}
    for word in words:
        if word.isalpha() and word not in stop_words:
            freq[word] = freq.get(word, 0) + 1

    if not freq:
        return "Unable to summarize text."

    max_freq = max(freq.values())
    for word in freq:
        freq[word] /= max_freq

    # Sentence scoring
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in freq:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + freq[word]

    # Select top sentences
    top_sentences = sorted(
        sentence_scores,
        key=sentence_scores.get,
        reverse=True
    )[:max_sentences]

    return " ".join(top_sentences)
