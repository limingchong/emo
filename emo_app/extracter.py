from rake_nltk import Rake
import nltk

#nltk.download('stopwords')
#nltk.download('punkt')


def get_key_word(text):
    rake_nltk_var = Rake()
    rake_nltk_var.extract_keywords_from_text(text)
    return rake_nltk_var.get_ranked_phrases()[:1]