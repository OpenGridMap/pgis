import os
import psycopg2
conn = psycopg2.connect("dbname=gis user=postgres")
cur = conn.cursor()

src_dir = "app/static/uploads/submissions/"
dirs = os.listdir(src_dir)
for dir in dirs:
    if dir == '.gitignore':
        continue
    submission_id = int(dir)
    print(submission_id)
    picture_dir = src_dir + dir + '/'
    pictures = os.listdir(picture_dir)
    cur2 = conn.cursor()
    cur2.execute("SELECT id from point where submission_id = %s and merged_to IS NULL", ([submission_id]))
    new_point_id_result = cur2.fetchone()
    new_point_id = -1
    if new_point_id_result != None:
        new_point_id = new_point_id_result[0]
    for picture in pictures:
        point_id = int(picture[:-4])
        cur.execute("SELECT point.submission_id, submission.user_id from point join submission on submission.id = point.submission_id where point.id = %s;",([point_id]))
        result = cur.fetchone()

        if result != None:
            user_id = result[1]
            filepath = "static/uploads/submissions/" + str(submission_id) + "/" + str(point_id) + ".jpg"
            #sql = "INSERT INTO picture (point_id, submission_id, user_id, filepath) VALUES (" + str(point_id) + "," + str(submission_id) + "," + str(result[1]) + "," + filepath + ");"
            #print(sql)
            if new_point_id == -1: # this is the case for an unmerged point
                new_point_id = point_id
            cur.execute("INSERT INTO picture (point_id, submission_id, user_id, filepath) VALUES(%s, %s, %s, %s)", (new_point_id, submission_id, user_id, filepath))
            conn.commit()
