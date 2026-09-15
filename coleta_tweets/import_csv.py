import mysql.connector as mysql
from mysql.connector import Error
import pandas as pd


empdata = pd.read_csv('tweets.csv', index_col=False, delimiter = ',')
empdata.head()


try:
    conn = mysql.connect(host='sql10.freesqldatabase.com', database='sql10496257', user='sql10496257', password='mrv4jBw2zs')
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        cursor.execute('DROP TABLE IF EXISTS tweets;')
        print('Creating table....')
# in the below line please pass the create table statement which you want #to create
        cursor.execute("CREATE TABLE tweets (tweet_id varchar(255),tweet varchar(255),link varchar(255),created_at_tweet varchar(255),in_reply_to_status_id varchar(255),in_reply_to_user_id varchar(255),retweet_count varchar(255),favorite_count varchar(255),user_id varchar(255),name varchar(255),screen_name varchar(255),location varchar(255) ,followers_count varchar(255),created_at varchar(255),verified varchar(255),dt_coleta varchar(255))")
        print("Table is created....")
        #loop through the data frame
        for i,row in empdata.iterrows():
            #here %S means string values 
            sql = "INSERT INTO tweets VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, tuple(row.fillna(0)))
            print("Record inserted")
            # the connection is not auto committed by default, so we must commit to save our changes
            conn.commit()
except Error as e:
            print("Error while connecting to MySQL", e)
