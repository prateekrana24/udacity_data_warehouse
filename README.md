# FINAL PROJECT - Data Warehouse

### Steps To Running The Code
1) Create a IAM User on AWS Redshift

2) Create a dwh.cfg file that contains all information needed for your S3, AWS Cluster, IAM_Role, and Secret Keys

3) Run each code segment in the datawarehouse_aws_redshift_setup.ipynb file until you get to the section where you need to run your example queries

4) If the first 3 steps have worked without issues, now you can run the create_tables.py file in the terminal within Jupyter Notebook

5) If step 4 worked fine for dropping and creating the tables, now you can run the etl.py file and this load the data from S3 into the staging tables and insert the final data into the tables on AWS Redshift

NOTE: Make sure you have all of the files: create_tables.py, etl.py, and especially sql_queries.py working before you create an AWS services like Redshift because you will start getting charged.
NOTE: Both the create_tables.py and etl.py files use the queries that you create in the sql_queries.py, so the most important file is the sql_queries.py as this is where all of the logic is held for your data.

6) Now, return to the datawarehouse_aws_redshift_setup.ipynb file and create and run your example queries and see if it's all working. If not, revisit the previous steps and see what went wrong or if your data didn't properly get uploaded into the staging/final tables on AWS Redshift. 


### Overview
- In this final project for the data warehouse, the idea is to create an ETL pipeline for the music streaming startup, Sparkify. The main purpose is to extract user data from S3, stage them in AWS Redshift, and then transform the data into a set of dimensional tables for their analytics team for goal of finding insights into what songs their users are listening to.

We are working with two datasets stored in S3: 
Song data: s3://udacity-dend/song_data
Log data: s3://udacity-dend/log_data

In order to read the log data, we need the following metadata file:
Log metadata: s3://udacity-dend/log_json_path.json


SONG DATASET:
Format of the Song Dataset file structure:
song_data/A/B/C/TRABCEI128F424C983.json

Format for what a single song file, TRAABJL12903CDCF1A.json, looks like inside:
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}


LOG DATASET:
Format for the Log Dataset file structure:
log_data/2018/11/2018-11-12-events.json

Format for what data looks like in an example log file, 2018-11-12-events.json:
![Picture of An Example Log File](https://video.udacity-data.com/topher/2019/February/5c6c3ce5_log-data/log-data.png)


LOG JSON METADATA:
Format for the Log JSON Metadata is seen in log_json_path.json:
![Picture of An Example Log JSON Metadata](https://video.udacity-data.com/topher/2022/May/6276f08b_log-json-path/log-json-path.png)


### Justification For Database Schema Design and ETL Pipeline

#### 1. Database Schema Design
- So, the schema for this project was designed with the goal of efficiently analyzing song data after getting insights into user behaviors, song popularity, and trends. The star schema was chosen because of its ability to simplify complex queries while optimizing performance.

FACT TABLE:
The songplays table serves as the fact table in this schema. It records individual song play events that are activated by users interacting with the system. The key columns used are start_time, user_id, song_id, artist_id, and session_id and they allow for tracking user interactions, identifying trends, and analyzing the relationship between users, songs, and sessions.

Justification: Songplays table has the most granular level of data which is good for analytical querying. The columns used allow for performance-based analysis such as identifying the most played songs or users who interact with the app the most. 

DIMENSION TABLES:
users - this table holds information about the users like user_id, first_name, last_name, gender, and level. 
Justification - user behavior is an important aspect of analyzing song plays as it's crucial to have user details in a separate dimension table to enable filtering and grouping by user characteristics.

songs - this table holds information about songs such as song_id, title, artist_id, year, and duration.
Justification - storing song details in a separate table allows for more dynamic querying like figuring trends in song popularity using year. We don't need to repeat song information in the songplays table as well and this is good for efficiency. 

artists - this table includes artist_id, name, location, latitude, and longitude.
Justification - artist information is used in song-related analyses so storing this data in a dimension table ensures that artist data is centralized and can be easily joined with other tables when needed

time - this table includes date and time breakdowns for songplay events like start_time, hour, day, week, month, year, and weekday.
Justification - time based analysis is essential for understanding patterns in song plays and by breaking down the timestamp into multiple components, we can properly aggregate song plays over different time periods. 

#### 2. ETL Pipeline
- The ETL pipeline was made to handle the extraction, transformation, and loading of data from S3 to Redshift. This means that the staging and final tables were populated correctly and efficiently. 

STAGING TABLES:
- Both staging_events and staging_songs tables temporarily store raw event and song data from S3. These staging tables are created/used to make sure that data is loaded correctly before it is processed into the final schema.
Justification - bby loading raw data into staging tables first, we can clean and transform the data without altering the core schema and this allows for easier troubleshooting of data quality issues before inserting into the final tables.

TRANSFORMATIONS:
- In this ETL pipeline, the data was transformed through SQL queries seen in the sql_queries.py file. There were different types of transformations such as timestamp conversions seen in the UNIX timestamps into readable data-time formats. Another transformation used was extracting date parts from the whole timestamp using EXTRACT function. Another transformation was using the JOINS (left specifically) between staging_events and staging_songs in order to connect song play events to song details, so that there is proper mapping to existing songs and artists
Justification - these transformations ensure that data is cleaned and formatted so that we may have more efficient querying and analysis.

DATA LOADING:
- These are the final tables where the data is loaded into for analysis: songplays, users, songs, artists, and time
Justification - Once the data is clean and transformed, it's put into the final tables where it's then ready for analytical querying. Each table is optimized with keys (DISTKEY and SORTKEY) for efficient lookups, ensuring that large datasets can be processed and queried without any performance bottlenecks.


#### 3. Example Queries
![AWS Redshift Example Query 1](/images/Udacity - Final Project Data Warehouse Example Queries 1.PNG)
![AWS Redshift Example Query 2](/images/Udacity - Final Project Data Warehouse Example Queries 2.PNG)
![AWS Redshift Example Query 3](/images/Udacity - Final Project Data Warehouse Example Queries 3.PNG)

NOTE: If you can't view these pictures, please refer to datawarehouse_aws_redshift_setup.ipynb file at the bottom of that file and all of the example queries will be there.
