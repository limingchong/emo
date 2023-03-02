from rake_nltk import Rake
import nltk

#nltk.download('stopwords')
#nltk.download('punkt')
text = """spaCy is an open-source software library for advanced natural language processing,
written in the programming languages Python and Cython. The library is published under the MIT license
and its main developers are Matthew Honnibal and Ines Montani, the founders of the software company Explosion."""


def get_key_word(text):
    rake_nltk_var = Rake()
    rake_nltk_var.extract_keywords_from_text(text)
    return rake_nltk_var.get_ranked_phrases()[:1]