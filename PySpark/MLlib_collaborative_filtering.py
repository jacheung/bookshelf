from pyspark.context import SparkContext
from pyspark.mllib.recommendation import Rating
from pyspark.mllib.recommendation import ALS

sc = SparkContext.getOrCreate()  # SparkContext setup
file_path = '/Users/jonathancheung/Documents/GitHub/still-learning/PySpark/datasets/movie_ratings.csv'

# data source : https://grouplens.org/datasets/movielens/
# load raw data. Data is in the format of user_id, movie_id, rating, time_stamp
data = sc.textFile(file_path)

# basic data clean up of CSV files and packaging into Rating tuples for collaborative filtering
ratings = data.map(lambda l: l.split(','))
ratings_final = ratings.map(lambda line: Rating(int(line[0]), int(line[1]), float(line[2])))
training_data, test_data = ratings_final.randomSplit([0.8, 0.2])
test_data_no_rating = test_data.map(lambda x: (x[0], x[1]))

# train model on ALS
model = ALS.train(training_data, rank=10, iterations=10)

# make predictions for model
predictions = model.predictAll(test_data_no_rating)

# evaluate model by converting back into an RDD, joining, and evaluating MSE
rates = ratings_final.map(lambda r: ((r[0], r[1]), r[2]))
preds = predictions.map(lambda r: ((r[0], r[1]), r[2]))
rates_and_preds = rates.join(preds)
MSE = rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
print("Mean Squared Error of the model for the test data = {:.2f}".format(MSE))