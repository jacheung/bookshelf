from pyspark import SparkConf
from pyspark.context import SparkContext
from nltk.corpus import stopwords

sc = SparkContext.getOrCreate(SparkConf().setMaster("local[*]"))  # SparkContext setup

# data source http://www.gutenberg.org/ebooks/100
# count number of words in Shakespeare using transformations and actions on Spark PairRDDs
baseRDD = sc.textFile('/Users/jonathancheung/Documents/GitHub/still-learning/PySpark/datasets/gutenberg_shakespeare.txt')

splitRDD = baseRDD.flatMap(lambda x: x.split())  # using flatmap to change sentences into words RDD
print("Total number of words in splitRDD:", splitRDD.count()) # Count the total number of words
splitRDD_no_stop = splitRDD.filter(lambda x: x.lower() not in stopwords)  # lower case and remove stop
splitRDD_no_stop_words = splitRDD_no_stop.map(lambda w: (w, 1))  # Create a tuple of the word and 1
resultRDD = splitRDD_no_stop_words.reduceByKey(lambda x, y: x + y) # Count occurences of each word

resultRDD_sort = resultRDD.sortByKey(ascending=False)  #sort keys in descending order
for word in resultRDD_sort.take(10):  # Show the top 10 most frequent words and their frequencies
    print("{} has {} counts". format(word[0], word[1]))