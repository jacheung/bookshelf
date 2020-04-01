from pyspark.sql import SparkSession
import matplotlib.pyplot as plt

# Setting up a SparkSession
# requirements : JDK 8, if have newer version, remove JDK and JRE by following oracle CLI docs
spark = SparkSession.builder.getOrCreate()

# Link and load csv dataframe using PySpark
file_path = '/Users/jonathancheung/Documents/GitHub/still-learning/PySpark/datasets/fifa_2018.csv'
fifa_df = spark.read.csv(file_path, header=True, inferSchema=True)

# Perform some basic EDA
fifa_df.printSchema()
fifa_df.show(10)
print("There are {} rows in the fifa_df DataFrame".format(fifa_df.count()))

# Run an SQL query
fifa_df.createOrReplaceTempView('fifa_df_table')  # Create a temporary view of fifa_df
query = '''SELECT Age FROM fifa_df_table WHERE Nationality == "Germany"'''
fifa_df_germany_age = spark.sql(query)
fifa_df_germany_age.describe().show()

# Plotting example
fifa_df_germany_age_pandas = fifa_df_germany_age.toPandas()  # Convert fifa_df to fifa_df_germany_age_pandas DataFrame
fifa_df_germany_age_pandas.plot(kind='density')
plt.show()
