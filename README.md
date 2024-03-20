# YouTube Data Harvesting and Warehousing using SQL & Streamlit

Workflow Overview:
YouTube API Data Retrieval:

Utilizes the YouTube Data API to fetch video metadata, comments, likes, etc.
Requires a valid API key from the Google Developer Console.
Storing Data in MongoDB:

Interacts with MongoDB using pymongo library.
Establishes a connection to a MongoDB database and stores retrieved data.
Transfer Data to SQL:

Transfers data from MongoDB to SQL for relational database management.
Utilizes pandas and SQLAlchemy libraries for data manipulation and interaction with SQL databases.
Streamlit Visualization:

Builds an interactive web application using the streamlit library.
Visualizes data fetched from the SQL database using Streamlit components like charts, tables, etc.
Usage:
Replace placeholders with actual API keys, MongoDB URI, SQL database details.
Customize the code to suit specific requirements and data schema.
Run the main script to execute the workflow and launch the Streamlit app for data visualization.



