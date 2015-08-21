import os, math, re, sys, fnmatch, string 
from ConfigParser import ConfigParser
reload(sys)

def make_lex_dict(f):
    return dict(map(lambda (w, m): (w, float(m)), [wmsr.strip().split('\t')[0:2] for wmsr in open(f) ]))

WORD_VALENCE_DICT = {}

##CONSTANTS#####

#(empirically derived mean sentiment intensity rating increase for booster words)
B_INCR = 0.293
B_DECR = -0.293

#(empirically derived mean sentiment intensity rating increase for using ALLCAPs to emphasize a word)
c_INCR = 0.733

# for removing punctuation
REGEX_REMOVE_PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))

PUNC_LIST = [".", "!", "?", ",", ";", ":", "-", "'", "\"",
                "!!", "!!!", "??", "???", "?!?", "!?!", "?!?!", "!?!?"]
NEGATE = []
# booster/dampener 'intensifiers' or 'degree adverbs' http://en.wiktionary.org/wiki/Category:English_degree_adverbs
BOOSTER_DICT = {}

# check for special case idioms using a sentiment-laden keyword known to SAGE
SPECIAL_CASE_IDIOMS = {}

def load_languages(additional_language_configs=None):
    global NEGATE

    additional_language_configs = additional_language_configs or []

    language_config_search_paths = [
        os.path.join(os.path.dirname(__file__),'vader_sentiment_languages.cfg'),
    ] + additional_language_configs

    for language_config in language_config_search_paths:
        if os.path.exists(language_config):
            cp = ConfigParser()
            cp.readfp(open(language_config))
            for lang in cp.sections():
                if cp.has_option(lang, "negate_words"):
                    NEGATE += [
                        i.strip() for i in cp.get(
                            lang, "negate_words").strip().split('\n')
                    ]


                if cp.has_option(lang, "booster_increment_words"):
                    for word in [
                        i.strip() for i in cp.get(
                            lang, "booster_increment_words").strip().split('\n')
                        ]:
                        BOOSTER_DICT[word] = B_INCR

                if cp.has_option(lang, "booster_decrement_words"):
                    for word in [
                        i.strip() for i in cp.get(
                            lang, "booster_decrement_words").strip().split('\n')
                        ]:
                        BOOSTER_DICT[word] = B_DECR
                if cp.has_option(lang, "special_case_idioms"):
                    for line in [
                        i.strip() for i in cp.get(
                            lang, "special_case_idioms").strip().split("\n")
                        ]:
                        k, v = line.split('=')
                        SPECIAL_CASE_IDIOMS[k.strip()] = float(v.strip())
                if cp.has_option(lang, "lexicon_file"):
                    lexicon_file = cp.get(lang, "lexicon_file")
                    lexicon_search_paths = [
                        lexicon_file,
                        os.path.join(os.path.dirname(language_config),lexicon_file),
                        os.path.join(os.path.dirname(__file__), lexicon_file),
                    ]
                    valence_dict = None
                    for f in lexicon_search_paths:
                        if os.path.exists(f):
                            valence_dict = make_lex_dict(f)
                            break
                
                    if valence_dict is None:
                        raise Exception("Unable to load %s" % lexicon_file)
                    
                    for k, v in valence_dict.items():
                        WORD_VALENCE_DICT[k] = v

load_languages()
