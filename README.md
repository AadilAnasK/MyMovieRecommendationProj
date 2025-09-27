# MyMovieRecommendationProj
This is a movie recommendation system. This will suggest the movies corresponding to user preferences. 


Pre-requisites:
1. Download the csv file from https://www.kaggle.com/datasets/danielgrijalvas/movies
2. Download and install MySQL Command Line Client if not installed
3. Create a database in the name Project
4. Refer the Python code and change the password in line 96 to match with your SQL password
5. Create a table in Project with columns matching the columns of the downloaded csv file
6. Load the dataset into the created table using the command:
          LOAD DATA INFILE '/path/to/data.csv'
          INTO TABLE your_table_name
          FIELDS TERMINATED BY ',' 
          ENCLOSED BY '"'
          LINES TERMINATED BY '\n'
          IGNORE 1 ROWS;
7. If error occurs, it maybe because the local_infile variable is set to False. Then run the below command, relaunch MySQL and repeat step 6:
          SET GLOBAL local_infile = 1;
8. Create another table with the name movie with columns name, genre, release_year, user_rating, movie_rating, runtime. Transfer data from the initial table to appropriate tables using the INSERT-SELECT statement
9. You may now TRUNCATE the initial table
10. Now execute the Project.py file in the command prompt and follow the instructions
