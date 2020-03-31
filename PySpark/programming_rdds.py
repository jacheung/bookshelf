from pyspark import SparkContext as sc

# data source http://www.gutenberg.org/ebooks/100
baseRDD = sc.textfile(file_path)