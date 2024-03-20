# YouTube Data Harvesting and Warehousing using SQL & Streamlit

## Workflow Overview

### 1. YouTube API Data Retrieval:
       * Utilizes the YouTube Data API to fetch channel data, video data, comments, likes, etc.
       * Requires a valid API key from the Google Developer Console.
  
### 2. Storing Data in MongoDB:
       * Interacts with MongoDB and Establishes a connection to a MongoDB database.
       * Stores the retrieved data (Temporary Storage) in a suitable format.
  
### 3. Transfer Data to SQL:
       * Extract data from MongoDB collections, facilitating smooth conversion into a DataFrame.
       * Converts the DataFrame into SQL tables, ensuring seamless data transformation.
  
### 4. Streamlit Visualization:
       * Builds an interactive web application using the streamlit library 
       * Users can enter Channel ID and view the Channel Details




