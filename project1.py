import googleapiclient.discovery
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import streamlit as st

# Youtube API Connection
def Api_Connection():
    api_service_name = "youtube"
    api_version = "v3"
    key = "AIzaSyCBJNadog4QVMgTWyONuytTXZQv3BHUQAs"
    youtube_data = googleapiclient.discovery.build(api_service_name, api_version, developerKey=key)

    return youtube_data

youtube=Api_Connection()


# Getting Channel Information
def get_channel_info(channelID):
    channel_details = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channelID
        )
    channel_data = channel_details.execute()

    channel_info={
        'channel_id':channel_data['items'][0]['id'],
        'channel_name':channel_data['items'][0]['snippet']['title'],
        'channel_subscription':channel_data['items'][0]['statistics']['subscriberCount'],
        'channel_views':channel_data['items'][0]['statistics']['viewCount'],
        'channel_video_count':channel_data['items'][0]['statistics']['videoCount'],
        'channel_description':channel_data['items'][0]['snippet']['description']
    }

    return channel_info


# Getting Video ID
def get_videoId(channelID):

    channel_details = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channelID
        )
    channel_data = channel_details.execute()

    playlist_id=channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads'] 
    next_Page_Token=None
    video_id=[]

    while True:
        video_details = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_Page_Token
        )
        video_info=video_details.execute()
        
        for i in range(len(video_info['items'])):
            data=video_info['items'][i]['snippet']['resourceId']['videoId']
            video_id.append(data)
        next_Page_Token=video_info.get('nextPageToken')
        if next_Page_Token is None:
            break
    
    return video_id


# Get Video Details
def get_video_info(video_id):
    video_details_info=[]
    for vid in video_id:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=vid
        )
        response = request.execute()
        
        for i in response['items']:
            video_information = {                   
                            "Channel_Id": i['snippet']['channelId'],
                            "Channel_Name": i['snippet']['channelTitle'] if 'channelTitle' in response['items'][0]['snippet'] else "Not Available",
                            "Video_Id": i['id'],
                            "Video_Name": i['snippet']['title'] if 'title' in i['snippet'] else "Not Available",
                            "Video_Description": i['snippet']['description'],
                            "Video_Published": i['snippet']['publishedAt'],
                            "Video_Views": i['statistics']['viewCount'],
                            "Video_Likes": i['statistics']['likeCount'],
                            "Video_Comment_Count": i['statistics']['commentCount'],
                            "Video_Duration": i['contentDetails']['duration'],
                            "Video_Thumbnail": i['snippet']['thumbnails']['default']['url'],
                            "Video_Caption_Status": i['contentDetails']['caption']
                            }
            
            video_details_info.append(video_information)

    return video_details_info


# Get Comment Information
def get_comment_info(video_id):
    comment_details_info=[]
    try:
        for vid in video_id:
            request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=vid
                )
            response = request.execute()

            for i in response['items']:
                comment_information=dict(Comment_ID=i['snippet']['topLevelComment']['id'],
                                        Comment_Text=i['snippet']['topLevelComment']['snippet']['textDisplay'],
                                        Comment_Author=i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                        Comment_Published=i['snippet']['topLevelComment']['snippet']['publishedAt'],
                                        Video_ID=i['snippet']['topLevelComment']['snippet']['videoId'])
                
                comment_details_info.append(comment_information)
                
    except:
        pass # Some time Channel owners may disabled some comments, that time some will error will be thrown, to avoid that we are using try except here
    
    return comment_details_info


# Upload Data to MongoDB
connection = MongoClient("mongodb+srv://thamizhvanan2000:8dRl4X258bBAnMN6@cluster0.pculefa.mongodb.net/")
db=connection['Youtube']
col = db['Channel_Data']

def channel_data(channelID):
    channel_details=get_channel_info(channelID)
    videoID=get_videoId(channelID)
    video_details=get_video_info(videoID)
    comment_details=get_comment_info(videoID)
   
    col.insert_one({'channel_info':channel_details,'video_info':video_details,'comment_info':comment_details})

    return "Data Uploaded to MongoDB sucessfully"


# Data from MongoDB to MySQL
def show_data():
    # Getting Data from MongoDB

    channel_list=[]
    for data in col.find({},{'_id':0,'channel_info':1}):
        channel_list.append(data['channel_info'])

    df_channel=pd.DataFrame(channel_list)

    video_list=[]
    for data in col.find({},{'_id':0,'video_info':1}):
        for video_info_details in data['video_info']:
            video_data = (
                video_info_details['Channel_Id'], 
                video_info_details['Channel_Name'],
                video_info_details['Video_Id'], 
                video_info_details['Video_Name'],
                video_info_details['Video_Description'], 
                video_info_details['Video_Published'],
                video_info_details['Video_Views'], 
                video_info_details['Video_Likes'],
                video_info_details['Video_Comment_Count'], 
                video_info_details['Video_Duration'],
                video_info_details['Video_Thumbnail'], 
                video_info_details['Video_Caption_Status']
            )
            video_list.append(video_data)

    df_videos=pd.DataFrame(video_list)

    comment_list=[]
    for data in col.find({},{'_id':0,'comment_info':1}):
        for comment_info_details in data['comment_info']: 
            comment_data = (
                comment_info_details['Video_ID'], 
                comment_info_details['Comment_ID'],
                comment_info_details['Comment_Text'], 
                comment_info_details['Comment_Author'],
                comment_info_details['Comment_Published']
            )
            comment_list.append(comment_data)
            
    df_comment=pd.DataFrame(comment_list)

    # Creating Tables in MySQL
    connection= mysql.connector.connect(host="localhost",user="root",password="SQL@2023",database="youtube_data")
    mycursor=connection.cursor()

    # channels table
    query_channel = '''create table if not exists channels(channelID varchar(100) primary key, 
                                                        channelName varchar(200), 
                                                        channelSubCount bigint,
                                                        channelViewCount bigint, 
                                                        channelVideoCount int, 
                                                        channelDesc text
            )'''
    mycursor.execute(query_channel)

    # videos table
    query_videos = '''create table if not exists videos(ChannelId varchar(100),
                                                        ChannelName varchar(200), 
                                                        VideoId varchar(100) primary key, 
                                                        VideoName varchar(255), 
                                                        VideoDescription text,
                                                        VideoPublished varchar(255), 
                                                        VideoViews bigint,
                                                        VideoLikes bigint,
                                                        VideoComment_Count bigint, 
                                                        VideoDuration varchar(255),
                                                        Video_Thumbnail text, 
                                                        VideoCaption_Status varchar(100)

            )'''
    mycursor.execute(query_videos)

    # comments table
    query_comments = '''create table if not exists comments(VideoId varchar(100),
                                                            Comment_ID varchar(100) primary key,
                                                            Comment_Text text,
                                                            Comment_Author varchar(200), 
                                                            Comment_Published datetime
                                                        
            )'''
    mycursor.execute(query_comments)


    # Inserting data to a Table
    data_set_channels = [tuple(x) for x in df_channel.to_numpy()]
    insert_query_channels = "insert ignore into channels values (%s,%s,%s,%s,%s,%s)"
    mycursor.executemany(insert_query_channels, data_set_channels)
    connection.commit()

    data_set_videos = [tuple(x) for x in df_videos.to_numpy()]
    insert_query_videos = "insert ignore into videos values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.executemany(insert_query_videos, data_set_videos)
    connection.commit()

    data_set_comments = [tuple(x) for x in df_comment.to_numpy()]
    insert_query = "insert ignore into comments values (%s,%s,%s,%s,%s)"
    mycursor.executemany(insert_query, data_set_comments)
    connection.commit()

# Channel Table View
def show_channel_table():
    channel_list=[]
    for data in col.find({},{'_id':0,'channel_info':1}):
        channel_list.append(data['channel_info'])

    df_channel=st.dataframe(channel_list)
    return df_channel

# Video Table View
def show_video_table():
    connection= mysql.connector.connect(host="localhost",user="root",password="SQL@2023",database="youtube_data")
    mycursor=connection.cursor()

    query_video = 'select * from videos'
    mycursor.execute(query_video)

    result = mycursor.fetchall()
    query_result=[]
    for data in result:
        query_result.append(data)

    df=pd.DataFrame(query_result,columns=['Channel_ID', 'Channel_Name','Video_ID', 'Video_Name',
                                            'Video_Description', 'Video_Published','Video_Views',
                                            'Video_Likes','Video_Comment_Count','Video_Duration',
                                            'Video_Thumbnail','Video_Caption_Status'])
    st.write(df)

# Comments Table View
def show_comment_table():
    connection= mysql.connector.connect(host="localhost",user="root",password="SQL@2023",database="youtube_data")
    mycursor=connection.cursor()

    query_video = 'select * from comments'
    mycursor.execute(query_video)

    result = mycursor.fetchall()
    query_result=[]
    for data in result:
        query_result.append(data)

    df=pd.DataFrame(query_result,columns=['Video_ID', 'Comment_ID','Comment_Text', 
                                          'Comment_Author','Comment_Published'])
    st.write(df)


# Streamlit Application
def main():
    st.title('Welcome to :blue[Streamlit]:sparkles:')

    # Create a sidebar navigation menu
    st.sidebar.title(":red[YouTube] Data Harvesting and Warehousing")
    st.sidebar.subheader(":blue[Streamlit retrieving data from the YouTube API, storing the data in SQL as a warehouse, querying the data warehouse with SQL, and displaying the data in the Streamlit app.],")
    page = st.sidebar.selectbox("Select the Operation", ["Data to MongoDB", "MongoDB to MYSQL", "Table View", "Queries"])

    # Display different pages based on the selection
    if page == "Data to MongoDB":
        show_data_mongodb()
    elif page == "MongoDB to MYSQL":
        show_data_mysql()
    elif page == "Table View":
        show_table_view()
    elif page == "Queries":
        show_queries()

def show_data_mongodb():

    channel_id_input = st.text_input("Enter the Channel ID 👇")

    MongoDBButton = st.button('Data to MongoDB')

    if MongoDBButton:   
        try:
            ch_ids=[]
            db=connection['Youtube']
            col = db['Channel_Data'] 

            for channel_id_data in col.find({},{'_id':0,'channel_info':1}):
                ch_ids.append(channel_id_data['channel_info']['channel_id'])
            if channel_id_input in ch_ids:
                st.warning("The data already exists; Please try a new one")
            else:
                channel_details_insert=channel_data(channel_id_input)           
                st.success(channel_details_insert)

        except:
            st.error("Please enter a valid ChannelID")


def show_data_mysql():
    SQLButton = st.button('Transfer Data to MySQL')  
    if SQLButton:
        show_data()
        st.success("Tables created successfully in MySQL")


def show_table_view():
    table_options=["***Channels***📡", "***Videos***:movie_camera:","***Comments***📝"]
    table_view = st.radio('***Select the table*** 𝄜',table_options,
                            captions = ["Channel Information", "Video Information", "Comments Information"])

    if table_view == '***Channels***📡':
        show_channel_table()
    elif table_view == '***Videos***:movie_camera:':
        show_video_table()
    elif table_view == '***Comments***📝':
        show_comment_table()


def show_queries():
    connection= mysql.connector.connect(host="localhost",user="root",password="SQL@2023",database="youtube_data")
    mycursor=connection.cursor()

    question = st.selectbox(
    'SQL Query Output',
    ('1.What are the names of all the videos and their corresponding channels?', 
     '2.Which channels have the most number of videos, and how many videos do they have?', 
     '3.What are the top 10 most viewed videos and their respective channels?',
     '4.How many comments were made on each video, and what are their corresponding video names?', 
     '5.Which videos have the highest number of likes, and what are their corresponding channel names?', 
     '6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
     '7.What is the total number of views for each channel, and what are their corresponding channel names?', 
     '8.What are the names of all the channels that have published videos in the year 2022?', 
     '9.What is the average duration of all videos in each channel, and what are their corresponding channel names?',
     '10.Which videos have the highest number of comments, and what are their corresponding channel names?'))

    if question=='1.What are the names of all the videos and their corresponding channels?':

        query_1 = 'select VideoName,ChannelName from videos'
        mycursor.execute(query_1)

        result = mycursor.fetchall()
        query__result_1=[]
        for data in result:
            query__result_1.append(data)

        df_1=pd.DataFrame(query__result_1,columns=['Video_Name', 'Channel_Name'])
        st.write(df_1)

    elif question=='2.Which channels have the most number of videos, and how many videos do they have?':

        query_2 = 'select channelName,channelVideoCount from channels order by channelVideoCount desc'
        mycursor.execute(query_2)

        result = mycursor.fetchall()
        query__result_2=[]
        for data in result:
            query__result_2.append(data)

        df_2=pd.DataFrame(query__result_2,columns=['Channel_Name', 'Video_Count'])
        st.write(df_2)
        
    elif question=='3.What are the top 10 most viewed videos and their respective channels?':

        query_3 = 'select VideoName,ChannelName,VideoViews from videos order by VideoViews limit 10'
        mycursor.execute(query_3)

        result = mycursor.fetchall()
        query__result_3=[]
        for data in result:
            query__result_3.append(data)

        df_3=pd.DataFrame(query__result_3,columns=['Video_Name', 'Channel_Name', 'Video_Count'])
        st.write(df_3)

    elif question=='4.How many comments were made on each video, and what are their corresponding video names?':

        query_4 = 'select VideoName,VideoComment_Count from videos'
        mycursor.execute(query_4)

        result = mycursor.fetchall()
        query__result_4=[]
        for data in result:
            query__result_4.append(data)

        df_4=pd.DataFrame(query__result_4,columns=['Video_Name', 'Comment_Count'])
        st.write(df_4)

    elif question=='5.Which videos have the highest number of likes, and what are their corresponding channel names?':
        
        query_5 = 'select VideoName,ChannelName,VideoLikes from videos order by VideoLikes desc'
        mycursor.execute(query_5)

        result = mycursor.fetchall()
        query__result_5=[]
        for data in result:
            query__result_5.append(data)

        df_5=pd.DataFrame(query__result_5,columns=['Video_Name', 'Channel_Name', 'Video_Likes'])
        st.write(df_5)

    elif question=='6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        
        query_6 = 'select VideoName,VideoLikes from videos order by VideoLikes desc'
        mycursor.execute(query_6)

        result = mycursor.fetchall()
        query__result_6=[]
        for data in result:
            query__result_6.append(data)

        df_6=pd.DataFrame(query__result_6,columns=['Video_Name', 'Video_Like_Count'])
        st.write(df_6)

    elif question=='7.What is the total number of views for each channel, and what are their corresponding channel names?':
        
        query_7 = 'select channelName,channelViewCount from channels order by channelViewCount desc'
        mycursor.execute(query_7)

        result = mycursor.fetchall()
        query__result_7=[]
        for data in result:
            query__result_7.append(data)

        df_7=pd.DataFrame(query__result_7,columns=['Channel_Name', 'Channel_View_Count'])
        st.write(df_7)

    elif question=='8.What are the names of all the channels that have published videos in the year 2022?':
        
        query_8 = "select VideoName,ChannelName,VideoPublished from videos where YEAR(VideoPublished)='2022'"
        mycursor.execute(query_8)

        result = mycursor.fetchall()
        query__result_8=[]
        for data in result:
            query__result_8.append(data)

        df_8=pd.DataFrame(query__result_8,columns=['Video_Name', 'Channel_Name', 'Video_Published_Date'])
        st.write(df_8)

    elif question=='9.What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        
        query_9 = '''SELECT ChannelName,SEC_TO_TIME(
                AVG(
                    SUBSTRING_INDEX(SUBSTRING_INDEX(VideoDuration, 'M', 1), 'PT', -1) * 60 +
                    SUBSTRING_INDEX(SUBSTRING_INDEX(VideoDuration, 'S', 1), 'M', -1)
                    )
                ) AS average_duration
                    FROM videos group by ChannelName;'''
        mycursor.execute(query_9)

        result = mycursor.fetchall()
        query__result_9=[]
        for data in result:
            query__result_9.append(data)

        df_9=pd.DataFrame(query__result_9,columns=['Channel_Name','Video_Duration'])        #
        st.write(df_9)

    elif question=='10.Which videos have the highest number of comments, and what are their corresponding channel names?':
        
        query_10 = "select channelName,VideoName,VideoComment_Count from videos order by VideoComment_Count desc;"
        mycursor.execute(query_10)

        result = mycursor.fetchall()
        query__result_10=[]
        for data in result:
            query__result_10.append(data)

        df_10=pd.DataFrame(query__result_10,columns=['Channel_Name', 'Video_Name', 'Video_Comment_Count'])       
        st.write(df_10)

if __name__ == "__main__":
    main()