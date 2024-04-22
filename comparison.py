import psycopg2
import json
import numpy as np
import pandas as pd
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
# END IMPORTS

# INITIALIZE THE EMBEDDING MODEL
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


# Function to calculate the Euclidean distance between two vectors
def euclidean_distance(v1, v2):
    return np.linalg.norm(v1 - v2)


def time_to_milliseconds(time_str):
    time_str = time_str.replace('NaN', '0')
    hours, minutes, seconds = time_str.split('h')[0], time_str.split(
        'm')[0].split('h')[1], time_str.split('s')[0].split('m')[1]

    total_milliseconds = (int(hours) * 60 * 60 * 1000) + \
        (int(minutes) * 60 * 1000) + (int(seconds) * 1000)

    return total_milliseconds


conn = psycopg2.connect(
    dbname="brightcove",
    user="postgres",
    password="123456",
    host="localhost",
    port="5432"
)
register_vector(conn)

cur = conn.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS brightcove_metadata (id bigserial PRIMARY KEY, title VARCHAR, title_embedding vector, duration BIGINT);
'''

cur.execute(create_table_query)
conn.commit()


# UNCOMMENT ONLY WHEN BRIGHTCOVE DATA IS NOT IN DB
# READ JSON
# with open('bc_shortlist.json', 'r') as file:
#     data = json.load(file)

# data = data['bc_shortlist']


# sql = """INSERT INTO brightcove_metadata (title, title_embedding, duration)
#          VALUES (%s, %s, %s)"""

# for record in data:
#     title = record['Title']
#     duration = record['Duration']
#     embedding = model.encode(title)
#     cur.execute(sql, (title, embedding, duration))
#     conn.commit()


# QUERY TO FIND THE CLOSEST NEIGHBOUR INSIDE THE DATABASE
query = '''
SELECT * FROM brightcove_metadata ORDER BY title_embedding <-> %s < 1;
'''

# READ YOUTUBE DATA WHICH IS AN INPUT DATA
with open('youtube.json', 'r') as file:
    yt_data = json.load(file)

# FIELDS FOR THE EXCEL OUTPUT
yt_titles = []
brightcove_titles = []
distances = []
yt_links = []
yt_durations = []
brightcove_durations = []

for yt_record in yt_data:
    yt_title = yt_record['Title']
    duration = yt_record['Duration']
    yt_url = yt_record['URL']
    milliseconds = time_to_milliseconds(duration)
    yt_durations.append(milliseconds)
    yt_embedding = model.encode(yt_title)
    print(f'Youtube Title: {yt_title}')

    # Execute the query
    cur.execute(query, (yt_embedding,))
    rows = cur.fetchall()

    # INITIALIZE VARIABLES TO KEEP TRACK OF THE CLOSEST RECORD AND ITS DISTANCE
    closest_record = None
    min_distance = float('inf')

    # LOOP THROUGH THE FETCHED ROWS
    for row in rows:
        # EXTRACT THE EMBEDDING FROM THE ROW
        db_embedding = row[2]

        # CALCULATE THE DISTANCE BETWEEN THE EMBEDDINGS
        distance = euclidean_distance(yt_embedding, db_embedding)

        # CHECK IF THIS RECORD IS CLOSER THAN THE PREVIOUS CLOSEST ONE
        if distance <= 0.37:
            min_distance = distance
            closest_record = row

    if closest_record:
        yt_titles.append(yt_title)
        brightcove_titles.append(closest_record[1])
        distances.append(min_distance)
        yt_links.append(yt_url)
        brightcove_durations.append(closest_record[3])
        print(f'Closest record: {closest_record[1]}')
        print(min_distance)
    else:
        yt_titles.append(yt_title)
        brightcove_titles.append("No closest record found")
        distances.append(None)
        brightcove_durations.append(None)
        yt_links.append(yt_url)
        print("No closest record found")

# CREATE A DATAFRAME
data = {
    'Youtube Title': yt_titles,
    'Brightcove Title': brightcove_titles,
    'Distance': distances,
    'Youtube Link': yt_links,
    'Youtube Duration': yt_durations,
    'Brightcove Duration': brightcove_durations
}
df = pd.DataFrame(data)

# SAVE DATAFRAME INTO EXCEL FILE
df.to_excel('comparison_output.xlsx', index=False)


cur.close()
conn.close()
