# Description
This is a scraping project which fetches the videos metadata from the brightcove platform and compare with the youtube videos json data. It uses linear algebra formula to calculate the distance of the vectors stored in the postgresql. pg_vector extension of postgresql is used to store the vectors of broghtcove videos in database.

# Tools & Technologies Used
1. Python3
2. Brightcove API
3. Youtube videos JSON File
4. PostgreSQL
5. pg_vector

# How it works
The main.py file is used to fetch the videos data from brightcove API. There should be already a youtube videos data in json format for the comparison. The comparison.py file does the following tasks:
- It stores the brightcove video records into PostgreSQL with embeddings
- After storing the record comment the sql queries for the inserting the records again
- Now it compares the brightcove database records with the youtube json file
- It creates an output file of comparison named comparison_output.json which contains the similarity of the records of both platforms