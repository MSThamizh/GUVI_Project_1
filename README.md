# YouTube Data Harvesting and Warehousing using SQL & Streamlit

## Workflow

The workflow of this project can be summarized as follows:

1. **YouTube API Data Retrieval**: Utilize the YouTube API to fetch data such as video metadata, statistics, and comments. Requires a valid API key from the Google Developer Console.
2. **Storing Data in MongoDB**: SInteracts with MongoDB and Establishes a connection to a MongoDB database and stores the retrieved data (Temporary Storage) in a suitable format.
3. **Transfer Data to SQL**: Extract data from MongoDB collections, facilitating smooth conversion into a DataFrame. Converts the DataFrame into SQL tables, ensuring seamless data transformation.
4. **Streamlit Visualization**: Utilize Streamlit to build an interactive web application for visualizing and exploring the data.


## Technologies Used

- **Python**: Main programming language used for scripting and development.
- **YouTube API**: Used for retrieving data from YouTube.
- **MongoDB**: NoSQL database used for storing raw data.
- **MySQL**: Relational database used for data transformation and warehousing.
- **Streamlit**: Python library for building interactive web applications.

## References

- **Python**: [https://docs.python.org/3/](https://docs.python.org/3/)
- **Youtube API**: [https://developers.google.com/youtube](https://developers.google.com/youtube/v3/getting-started)
- **MongoDB Documentation**: [https://www.mongodb.com/](https://www.mongodb.com/)
- **MySQL Documentation**: [https://www.mysql.com/](https://www.mysql.com/)
- **Streamlit Documentation**: [https://docs.streamlit.io/library/api-reference](https://docs.streamlit.io/library/api-reference)
  


