import mysql.connector as m
import os
import time

def genreselection(l_movietype):
        l_genres = list()
        for c_g in l_movietype:
                c_g = c_g.strip().lower()
                if c_g != "" and c_g!='all':
                        l_genres.append(c_g)
        if l_movietype[0].lower()=='all':
                l_genres=['action', 'horror', 'drama', 'comedy', 'documentary', 'thriller', 'romance', 'sci-fi',
                          'fantasy', 'adventure', 'biography', 'crime', 'family', 'animation', 'music', 'western', 'history', 'mystery', 'sport', 'musical']
        return l_genres
def erasplit(s_era):
        while True:
                l_era_parts = s_era.split("-")
                if len(l_era_parts) != 2 or not (l_era_parts[0].isdigit() and l_era_parts[1].isdigit()):
                        print("Invalid era format. Expected 'YYYY-YYYY'")
                        s_era = input('Enter the era of movie: Enter 0000-9999 for any era\nFormat: YYYY-YYYY')
                        cur.execute('UPDATE user SET era = %s' %(s_era,))
                        db_obj.commit()
                        continue
                else:
                        i_era_start = int(l_era_parts[0])
                        i_era_end = int(l_era_parts[1])
                        return i_era_start, i_era_end
                        break
        
def moviedisplay(l_genres, i_era_start, i_era_end, i_age, i_runtime, i_userid):
        if i_age < 18:
                s_permission_input = input("Do you have parental permission to watch restricted movies? (y/n): ").strip().lower()
                i_parental_permission = 1 if s_permission_input.lower() == "y" else 0
        else:
                i_parental_permission = 1
        cur.execute('CREATE TABLE IF NOT EXISTS watchedmovie(userid INTEGER, movie VARCHAR(150));')
        db_obj.commit()
        cur.execute('SELECT movie FROM watchedmovie WHERE userid = %s;' %(i_userid,))
        t_t_movienodisplay = cur.fetchall()
        s_movienodisplay = "("
        if t_t_movienodisplay:   
                for i in t_t_movienodisplay:
                        s_movienodisplay += "'%s'" %(i[0])
                        if i!=t_t_movienodisplay[-1]:
                                s_movienodisplay +=','
                s_movienodisplay += ")"
        else:
                s_movienodisplay = "('')"
        s_genre_conditions = ""
        for i in range(len(l_genres)):
                if i > 0:
                        s_genre_conditions += " OR "
                s_genre_conditions += "m.genre = '%s'" %(l_genres[i],)
        s_query = 'SELECT DISTINCT m.name, m.genre, m.release_year, m.user_rating, m.movie_rating, m.runtime \
        FROM movie m,\
        rating_age ra WHERE ra.rating = m.movie_rating AND \
        (%s)\
        AND (m.release_year BETWEEN %s AND %s)\
        AND (\
             (%s >= ra.min_age) OR\
             (%s >= ra.min_parental_age AND %s = 1)\
             ) AND runtime <= %s \
        AND m.name NOT IN %s \
        ORDER BY m.user_rating DESC;' %(s_genre_conditions, i_era_start, i_era_end, i_age, i_age, i_parental_permission, i_runtime, s_movienodisplay)
        cur.execute(s_query)
        results = cur.fetchmany(100)
        if len(results) == 0:
                print("No movies found. Try widening your genre or era selection.")
        else:
                print("\nTop Movies for You:\n")
                count = 1
                for row in results:
                        name, genre, year, user_rating, movie_rating, runtime = row
                        print("{}. {} ({})".format(count, name, year))
                        print("   Genre: {}".format(genre))
                        print("   IMDb: {} | Rated: {} | Runtime: {} mins\n".format(user_rating, movie_rating, runtime))
                        count += 1
        
def checkpassword(i_userid, s_password):
        cur.execute('SELECT password FROM user where userid = %s;' %(i_userid,))
        t_savedpassword = cur.fetchone()
        #No data retrieved => UserID is wrong
        if not t_savedpassword:
                print('User does not exist')
                return False
        elif t_savedpassword[0]!=s_password:
                print('Wrong password')
                return False
        else:
                return True
        
#Creating db object
db_obj = m.connect(host='localhost',
                   user='root',
                   password='12345@MySQL',
                   database = 'Project')
cur=db_obj.cursor()

#Creates table user if it does not exist
cur.execute('CREATE TABLE IF NOT EXISTS user(userid INTEGER, age TINYINT, name VARCHAR(50), movietype VARCHAR(150), password VARCHAR(18), era char(9));')
db_obj.commit()
t_userdata = tuple()
s_userstatus = input('Are you a new user?\nEnter y/n as a response: ')

try:
    cur.execute('SELECT * FROM rating_age;')
    cur.fetchall()
except:
    cur.execute("CREATE TABLE rating_age(rating VARCHAR(10), min_age TINYINT, min_parental_age TINYINT);")
    db_obj.commit()
    l_ratinginsert = [('R', 18,17), ('PG', 7, 7), ('G', 0, 0), ('Not Rated', 0, 0), ('', 0, 0), ('NC-17', 17, 17), ('TV-PG', 14, 0),
                      ('PG-13', 13, 0), ('Unrated', 0, 0), ('X', 18, 18), ('TV-MA', 17, 0), ('TV-14', 14, 0)]
    for i in l_ratinginsert:
        cur.execute('INSERT INTO rating_age VALUES%s' %(i,))
        db_obj.commit()

while True:
        if s_userstatus.lower()=='y':
            try:
                i_age = int(input('Enter your age'))
                s_name = input('Enter your name')
                s_movietype = input('''Enter preferred movie types: Enter All if genre doesn't matter
Types: Action, Horror, Drama, Comedy, Documentary, Thriller, Romance, Sci-fi, Fantasy, Adventure, Biography, Crime,Family, Animation, Music, Western, History, Mystery, Sport, Musical
Format: Type1/Type2/....\n''')
                s_password = input('Enter the password for your account (Max:18 characters): ')
                os.system('cls')
                s_era = input('Enter the era of movie: Enter 0000-9999 for any era\nFormat: YYYY-YYYY\n')
                cur.execute('select max(userid) from user;')
                t_maxid = cur.fetchone()
                if not t_maxid[0]:
                    i_userid = 10000
                else:
                    i_userid = t_maxid[0] + 1
                print('Your userid is:', i_userid)
                time.sleep(2)
                cur.execute('insert into user values(%s,%s,"%s","%s","%s","%s");' %(i_userid, i_age, s_name, s_movietype, s_password, s_era))
                t_userdata = (s_name, i_age, s_movietype, s_password, s_era)
                db_obj.commit()
            except ValueError:
                print('Wrong Data! Try Again')
            else:
                break
        else:
            try:
                i_userid = int(input('Enter UserID: '))
                s_password = input('Enter password: ')
                os.system('cls')
                if checkpassword(i_userid, s_password):
                        cur.execute('SELECT name, age, movietype, password, era FROM user where userid = %s;' %(i_userid,))
                        t_userdata = cur.fetchone()
                        print('Welcome', t_userdata[0])
                else:
                        continue
            except ValueError:
                print('Try again')
            else:
                break

i_option = int(input('''Do you want to:
1. Edit your preference
2. Search for new movies
3. Search with altered preference
Enter appropriate index number\n'''))
while True:
        if i_option==1:
                try:
                    qn=input("Do you want to edit ur preferences?(y/n):").lower()
                    if qn=='y':
                            s_password = input("Re-enter your password:")
                            os.system('cls')
                            if checkpassword(i_userid, s_password):
                                     cur.execute("SELECT movietype,era from user where userid=%s"%(i_userid,))
                                     t_preference=cur.fetchone()
                                     s_movietype,s_era=t_preference
                                     print("\nYour current preferences:")
                                     print("1. Movie Types: %s" % s_movietype)
                                     print("2. Era: %s" % s_era)
                                     new_type = input("Enter new movie types (or press n to keep current): ")
                                     if new_type.strip().lower() != "n":
                                            s_movietype = new_type
                                     new_era = input("Enter new era (or press n to keep current): ")
                                     if new_era.strip() != "n":
                                            s_era = new_era
                                     cur.execute("UPDATE user SET movietype='%s', era='%s' WHERE userid=%s" %(s_movietype, s_era, i_userid))
                                     db_obj.commit()

                                     print("\nPreferences updated successfully ")
                            elif qn=='n':
                                     print("Alright,No changes made in your preferences")                
                            else:
                                     print("Invalid choice,Please type y or n")
                except ValueError:
                        print('Wrong Data! Please Try again')
                        continue
                        
        elif i_option==2:
                try:                        
                        s_movietype = t_userdata[2]
                        s_era = t_userdata[4]
                        i_age = t_userdata[1]
                        print("Enter the amount of time you have, Enter 99 for hours and minutes if time isn't a constraint")
                        i_hour = int(input('Enter the number of hours you have: '))
                        i_min = int(input('Enter the number of minutes you have: '))
                        i_runtime = i_hour * 60 + i_min
                        l_genres = genreselection(s_movietype.split('/'))
                        i_era_start, i_era_end = erasplit(s_era)
                        moviedisplay(l_genres, i_era_start, i_era_end, i_age, i_runtime, i_userid)
                except ValueError:
                        print('Please try again, Wrong Data!')
                        continue
                else:
                        break
        elif i_option==3:
                try:
                        i_age = t_userdata[1]
                        print("1 - Change only genre")
                        print("2 - Change only era")
                        print("3 - Change both genre and era")
                        print('Enter aprropriate index number')
                        i_choice = int(input("Enter your choice: "))
                        if i_choice == 1:
                                s_era = t_userdata[4]
                                s_new_genres = input('''Enter new genres separated by comma: Enter all if no genre is to be specified
Types: Action, Horror, Drama, Comedy, Documentary, Thriller, Romance, Sci-fi, Fantasy, Adventure, Biography, Crime,Family, Animation, Music, Western, History, Mystery, Sport, Musical\
''').strip()
                                i_era_start, i_era_end = erasplit(s_era)
                                if s_new_genres != "":
                                        s_movietype = s_new_genres
                                else:
                                        print('Try again')
                                        continue
                                l_genres = genreselection(s_movietype.split(','))
                                i_era_start, i_era_end = erasplit(s_era)
                        elif i_choice == 2:
                                s_movietype = t_userdata[2]
                                l_genres = genreselection(s_movietype.split(','))
                                i_era_start = int(input('Enter era start year'))
                                i_era_end = int(input('Enter era end year'))
                                assert 0<i_era_start<=i_era_end<10000
                        elif i_choice == 3:
                                s_era = t_userdata[4]
                                s_new_genres = input('''Enter new genres separated by comma: Enter all if no genre is to be specified
Types: Action, Horror, Drama, Comedy, Documentary, Thriller, Romance, Sci-fi, Fantasy, Adventure, Biography, Crime,Family, Animation, Music, Western, History, Mystery, Sport, Musical\
''').strip()
                                if s_new_genres != "":
                                        s_movietype = s_new_genres
                                else:
                                        print('Try again')
                                        continue
                                l_genres = genreselection(s_movietype.split(','))
                                i_era_start = int(input('Enter era start year'))
                                i_era_end = int(input('Enter era end year'))
                                assert 0<i_era_start<=i_era_end<10000
                        print("Enter the amount of time you have, Enter 99 for hours and minutes if time isn't a constraint")
                        i_hour = int(input('Enter the number of hours you have: '))
                        i_min = int(input('Enter the number of minutes you have: '))
                        i_runtime = i_hour * 60 + i_min
                        moviedisplay(l_genres, i_era_start, i_era_end, i_age, i_runtime, i_userid)    
                except AssertionError:
                        print('Years are not in the right format! Try again!')
                        continue
                except ValueError:
                        print('Wrong data, try again!')
                        continue
                else:
                        break
        else:
                print('Choice not listed')
        i_option = int(input('''Do you want to:
1. Edit your preference
2. Search for new movies
3. Search with altered preference
4. Exit
Enter appropriate index number\n'''))
        if i_option == 4:
                print('Bye bye')
                break
if i_option in (2,3):
        s_moviewatched = input('Enter the name of the movie you selected.\nThis movie will not be displayed again, if that is not needed enter n\n').lower()
        if s_moviewatched.strip().lower() != 'n':
                try:
                        cur1 = db_obj.cursor()
                        cur1.execute('INSERT INTO watchedmovie VALUES(%s,"%s");' %(i_userid, s_moviewatched))
                        db_obj.commit()
                except:
                        cur.fetchall()
                        cur1 = db_obj.cursor()
                        cur1.execute('INSERT INTO watchedmovie VALUES(%s,"%s");' %(i_userid, s_moviewatched))
                        db_obj.commit()
print('Bye bye!!!!!!')
time.sleep(5)
db_obj.close()
