r"""
Distance Metrics
================

Introduces the concept of distance between document representations, and demonstrates its calculation using Gensim.

"""

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

###############################################################################
# If you simply want to calculate the similarity between documents, then you
# may want to check out the `Similarity Queries Tutorial
# <https://radimrehurek.com/gensim/tut3.html>`_ and the `API reference for similarities
# <https://radimrehurek.com/gensim/similarities/docsim.html>`_. The current
# tutorial shows the building block of these larger methods, which are a small
# suite of distance metrics.
#
# Here's a brief summary of this tutorial:
#
# 1. Set up a small corpus consisting of documents belonging to one of two topics
# 2. Train an LDA model to distinguish between the two topics
# 3. Use the model to obtain distributions for some sample words
# 4. Compare the distributions to each other using a variety of distance metrics:
#
#   * Hellinger distance
#   * Jaccard coefficient
#
# 5. Discuss the concept of distance metrics in slightly more detail
#
from gensim.corpora import Dictionary

# you can use any corpus, this is just illustratory
texts = [
    ['bank', 'river', 'shore', 'water'],
    ['river', 'water', 'flow', 'fast', 'tree'],
    ['bank', 'water', 'fall', 'flow'],
    ['bank', 'bank', 'water', 'rain', 'river'],
    ['river', 'water', 'mud', 'tree'],
    ['money', 'transaction', 'bank', 'finance'],
    ['bank', 'borrow', 'money'],
    ['bank', 'finance'],
    ['finance', 'money', 'sell', 'bank'],
    ['borrow', 'sell'],
    ['bank', 'loan', 'sell'],
]

dictionary = Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

import numpy
numpy.random.seed(1) # setting random seed to get the same results each time.

from gensim.models import ldamodel
model = ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=2, minimum_probability=1e-8)
model.show_topics()

###############################################################################
# Let's call the 1st topic the **water** topic and the second topic the **finance** topic.
#
# Let's take a few sample documents and get them ready to test our distance functions.
#
doc_water = ['river', 'water', 'shore']
doc_finance = ['finance', 'money', 'sell']
doc_bank = ['finance', 'bank', 'tree', 'water']

# Now let's transform these into a bag of words format.
bow_water = model.id2word.doc2bow(doc_water)
bow_finance = model.id2word.doc2bow(doc_finance)
bow_bank = model.id2word.doc2bow(doc_bank)

# We can now get the LDA topic distributions for these.
lda_bow_water = model[bow_water]
lda_bow_finance = model[bow_finance]
lda_bow_bank = model[bow_bank]

###############################################################################
# Hellinger
# ---------
#
# We're now ready to apply our distance metrics.
# These metrics return a value between 0 and 1, where values closer to 0 indicate a
# smaller distance and therefore a larger similarity.
#
# Let's start with the popular Hellinger distance.
#
# The Hellinger distance metric is symmetric and gives an output in the range [0,1]
# for two probability distributions. Values closer to 0 mean "more similar".
#
from gensim.matutils import hellinger
print(hellinger(lda_bow_water, lda_bow_finance))
print(hellinger(lda_bow_finance, lda_bow_bank))

###############################################################################
# Makes sense, right? In the first example, Document 1 and Document 2 are hardly similar, so we get a value of roughly 0.5.
#
# In the second case, the documents are a lot more semantically similar, so their distance is lower.
#

###############################################################################
#
# In our previous examples we saw that there were lower distance values between
# ``bank`` and ``finance`` than for ``bank`` and ``water``, even if it wasn't by a huge margin.
# What does this mean?
#
# The ``bank`` document is a combination of both water and finance related
# terms - but as bank in this context is likely to belong to the finance topic,
# the distance values are less between the finance and bank bows.
#

# just to confirm our suspicion that the bank bow is more to do with finance:
model.get_document_topics(bow_bank)

###############################################################################
#
# It's evident that while it isn't too skewed, it it more towards the finance topic.
#

###############################################################################
# Jaccard coefficient
# -------------------
#
# Let's now look at the `Jaccard Distance
# <https://en.wikipedia.org/wiki/Jaccard_index>`_ (also Jaccard index, Jaccard coefficient)
# for calculating the similarity between two documents represented as two bags-of-words vectors.
#
from gensim.matutils import jaccard

print(jaccard(bow_water, bow_bank))
print(jaccard(doc_water, doc_bank))
print(jaccard(['word'], ['word']))

###############################################################################
# The three examples above feature 2 different input methods.
#
# In the first case, we present document vectors already in bag of
# words format. The distance can be defined as 1 minus the size of the
# intersection upon the size of the union of the vectors.
#
# We can see (on manual inspection as well), that the distance is likely to be
# high - and it is.
#
# The last two examples illustrate the ability for Jaccard distance to accept even lists
# of words (i.e, documents) as inputs.
#
# In the last case, because they are the same vectors, so the value returned is 0
# - this means the distance is 0 and the two documents are identical.
#

###############################################################################
#
# Distance Metrics for Topic Distributions
# ----------------------------------------
#
# While there are already standard methods to identify similarity of documents,
# our distance metrics has one more interesting use-case: topic distributions.
#
# Let's say we want to find out how similar our two topics are, ``water`` and ``finance``.
#
topic_water, topic_finance = model.show_topics()

# Preprocess to get the topics in a format accepted by our distance metric functions.

def parse_topic_string(topic):
    """Split a string returned by model.show_topics() into topics and their probabilities."""
    topic = topic.split('+')
    topic_bow = []
    for word in topic:
        # split the probability from word
        prob, word = word.split('*')
        # get rid of spaces and quote marks
        word = word.replace(" ", "").replace('"', '')
        # convert the word (string) to its dictionary index (int)
        word = model.id2word.token2id[word]
        topic_bow.append((word, float(prob)))
    return topic_bow

finance_distribution = parse_topic_string(topic_finance[1])
water_distribution = parse_topic_string(topic_water[1])

# the finance topic in the bag-of-words format looks like this:
print(finance_distribution)

###############################################################################
# Now that we've got our topics in a format acceptable by our functions,
# let's use a Distance metric to see how similar the word distributions in the
# topics are.
#
print(hellinger(water_distribution, finance_distribution))

###############################################################################
# Our value of roughly 0.36 means that the topics are not TOO distant with
# respect to their word distributions.
#
# This makes sense again, because of overlapping words like ``bank`` and a
# small size dictionary.
#


###############################################################################
# What are Distance Metrics?
# --------------------------
#
# Having seen the practical usages of these measures (i.e, to find similarity),
# let's learn a little about what exactly Distance Measures and Metrics are.
#
# There
# are 4 conditons for for a distance measure to be a metric:
#
# 1. d(x,y) >= 0
# 2. d(x,y) = 0 <=> x = y
# 3. d(x,y) = d(y,x)
# 4. d(x,z) <= d(x,y) + d(y,z)
#
# That is: it must be non-negative; if x and y are the same, distance must be
# zero; it must be symmetric; and it must obey the triangle inequality law.
#
# Simple enough, right?
#
# Let's test these out for our measures.
#

# ormal Hellinger distance.
a = hellinger(water_distribution, finance_distribution)
b = hellinger(finance_distribution, water_distribution)
print(a)
print(b)
print(a == b)

# If we pass the same values, it is zero.
print(hellinger(water_distribution, water_distribution))

# For triangle inequality let's use LDA document distributions.
print(hellinger(lda_bow_finance, lda_bow_bank))

# Triangle inequality works too!
print(hellinger(lda_bow_finance, lda_bow_water) + hellinger(lda_bow_water, lda_bow_bank))


# For a nice review of the mathematical differences between the Hellinger distance and
# Kullback-Leibler divergence, see for example `here
# <http://stats.stackexchange.com/questions/130432/differences-between-bhattacharyya-distance-and-kl-divergence>`__.
#


###############################################################################
# Visualizing Distance Metrics
# ----------------------------
#
# Let's plot a graph of our toy dataset using the popular `networkx
# <https://networkx.github.io/documentation/stable/>`_ library.
#
# Each node will be a document, where the color of the node will be its topic
# according to the LDA model. Edges will connect documents to each other, where
# the *weight* of the edge will be inversely proportional to the Jaccard
# similarity between two documents. We will also annotate the edges to further
# aid visualization: **strong** edges will connect similar documents, and
# **weak (dashed)** edges will connect dissimilar documents.
#
# In summary, similar documents will be closer together, different documents
# will be further apart.
#
import itertools
import networkx as nx

def get_most_likely_topic(doc):
    bow = model.id2word.doc2bow(doc)
    topics, probabilities = zip(*model.get_document_topics(bow))
    max_p = max(probabilities)
    topic = topics[probabilities.index(max_p)]
    return topic

def get_node_color(i):
    return 'skyblue' if get_most_likely_topic(texts[i]) == 0 else 'pink'

G = nx.Graph()
for i, _ in enumerate(texts):
    G.add_node(i)

for (i1, i2) in itertools.combinations(range(len(texts)), 2):
    bow1, bow2 = texts[i1], texts[i2]
    distance = jaccard(bow1, bow2)
    G.add_edge(i1, i2, weight=1/distance)

#
# https://networkx.github.io/documentation/networkx-1.9/examples/drawing/weighted_graph.html
#
pos = nx.spring_layout(G)

threshold = 1.25
elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > threshold]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= threshold]

node_colors = [get_node_color(i) for (i, _) in enumerate(texts)]
nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors)
nx.draw_networkx_edges(G, pos, edgelist=elarge, width=2)
nx.draw_networkx_edges(G, pos, edgelist=esmall, width=2, alpha=0.2, edge_color='b', style='dashed')
nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

###############################################################################
# We can make several observations from this graph.
#
# First, the graph consists of two connected components (if you ignore the weak edges).
# Nodes 0, 1, 2, 3, 4 (which all belong to the water topic) form the first connected component.
# The other nodes, which all belong to the finance topic, form the second connected component.
#
# Second, the LDA model didn't do a very good job of classifying our documents into topics.
# There were many misclassifications, as you can confirm in the summary below:
#
print('id\ttopic\tdoc')
for i, t in enumerate(texts):
    print(f'{i}\t{get_most_likely_topic(t)}\t{" ".join(t)}')

###############################################################################
# This is mostly because the corpus used to train the LDA model is so small.
# Using a larger corpus should hopefully give better results, but that is beyond
# the scope of this tutorial.
#
# Conclusion
# ----------
#
# That brings us to the end of this small tutorial.
# To recap, here's what we covered:
#
# 1. Set up a small corpus consisting of documents belonging to one of two topics
# 2. Train an LDA model to distinguish between the two topics
# 3. Use the model to obtain distributions for some sample words
# 4. Compare the distributions to each other using the distance metrics of Hellinger distance and Jaccard index
# 5. Discuss the concept of distance metrics in slightly more detail
#
# The scope for adding new similarity metrics is large, as there exist an even
# larger suite of metrics and methods to add to the matutils.py file.
# For more details, see `Similarity Measures for Text Document Clustering
# <http://www.academia.edu/download/32952068/pg049_Similarity_Measures_for_Text_Document_Clustering.pdf>`_
# by A. Huang.

