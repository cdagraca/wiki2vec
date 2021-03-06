import datetime
import logging
from gensim import utils
import string

logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)-18s: %(message)s")

ln = logging.getLogger()

fileHandler = logging.FileHandler("wiki2feck_log%s.txt" % datetime.datetime.now().isoformat())

fileHandler.setFormatter(logFormatter)
ln.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
ln.addHandler(consoleHandler)

ln.setLevel(logging.DEBUG)

import multiprocessing
import os
from optparse import OptionParser

import gensim
import re


os.system("taskset -p 0xff %d" % os.getpid())

entity_min_count = 5
def rule(word, count, min_count):
    if word.startswith("DBPEDIA_ID/") and count >= entity_min_count:
        return gensim.utils.RULE_KEEP
    else:
        return gensim.utils.RULE_DEFAULT


def read_corpus(path_to_corpus, output_path, min_count=10, size=500, window=10, _entity_min_count=5):
    global entity_min_count
    workers = multiprocessing.cpu_count()
    entity_min_count = _entity_min_count
    sentences = gensim.models.word2vec.LineSentence(path_to_corpus)
    model = gensim.models.Word2Vec(sentences, min_count=min_count, size=size, window=window, sg=1, workers=workers, trim_rule=rule)
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)
    model.save(output_path)


def main():
    parser = OptionParser(usage="usage: %prog [options] corpus outputModel",
                          version="%prog 1.0")

    parser.add_option("-m", "--min_count",
                      action="store",
                      dest="min_count",
                      default=10,
                      type="int",
                      help="min number of apperances",)

    parser.add_option("-e", "--entity_min_count",
                      action="store",
                      dest="_entity_min_count",
                      default=5,
                      type="int",
                      help="min number of apperances for DBpedia entities",)

    parser.add_option("-s", "--size",
                      action="store",
                      dest="size",
                      default=500,
                      type="int",
                      help="vectors size",)

    parser.add_option("-w", "--windows",
                      action="store",
                      dest="window",
                      default=10,
                      type="int",
                      help="window size",)

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("wrong number of arguments")

    option_dict = vars(options)
    option_dict["path_to_corpus"] = args[0]
    option_dict["output_path"] = args[1]
    ln.info("Options are: %s" % option_dict)

    read_corpus(**option_dict)


if __name__ == "__main__":
    main()
