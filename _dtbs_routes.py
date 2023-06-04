from flask import Flask, render_template, redirect, request, session
import mysql.connector
import _dtbs_init
from django import template

app = Flask(__name__, template_folder = "html_templates")
app.secret_key = 'theletenasasboithiso'

server_launched = False

def clean(text):
    ret = str(text).strip("[](),'")
    return ret

def clean_no_comma(text):
    ret = str(text).strip("'[]()")
    ret = ret.replace("',", "")
    return ret

def clean_list(lst):
    ret = []
    for text in lst:
        ret.append(clean(text))
    return lst

@app.before_request
def before_request():
    global server_launched
    if not server_launched:
        session['ACCESS'] = 'none'
        session['SCHOOL'] = 'none'
        server_launched = True

@app.route('/logout')
def logout():
    session['ACCESS'] = 'none'
    return redirect('/')

@app.route('/login', methods = ['GET','POST'])
def login():
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if username == '' or password == '':
            session['ACCESS'] = 'none'
            session['SCHOOL'] = 'none'
            return redirect('/login')
        
        mycursor.execute(f"SELECT username FROM users WHERE username = '{username}'")
        
        username_ = mycursor.fetchall()
        username_ = clean(username_)

        session['USER'] = username_
        
        mycursor.execute(f"SELECT password FROM users WHERE username = '{username_}'")
        password_ = mycursor.fetchall()
        password_ = clean(password_)

        print(username)
        print(password)
        print(username_)
        print(password_)
        
        if(password != password_):
            return redirect('/login')

        mycursor.execute(f"SELECT username FROM administrator WHERE username = '{username_}'")
        admin_ = mycursor.fetchall()
        admin_ = clean(admin_)

        mycursor.execute(f"SELECT username FROM manager WHERE username = '{username_}'")
        manager_ = mycursor.fetchall()
        manager_ = clean(manager_)

        mycursor.execute(f"SELECT username FROM students_teachers WHERE username = '{username_}'")
        studteach_ = mycursor.fetchall()
        studteach_ = clean(studteach_)
        
        if admin_ == username_:
            session['ACCESS'] = 'admin'
        elif manager_ == username_:
            session['ACCESS'] = 'manager'
        elif studteach_ == username_:
            mycursor.execute(f"SELECT role FROM students_teachers WHERE username = '{username_}'")
            user_ = mycursor.fetchall()
            user_ = clean(user_)
            session['ACCESS'] = user_
        else:
            session['ACCESS'] = 'none'
            return render_template("login.html")
        mycursor.execute(f"SELECT school_name FROM users WHERE username = '{username_}'")
        school_ = mycursor.fetchall()
        school_ = clean(school_)
        print(school_)
        session['SCHOOL'] = school_
        return redirect('/')
    else:
        return render_template("login.html")
    
    
@app.route('/')
def main():
    access = session.get('ACCESS')
    print(access)
    if(access == 'admin'):
        return render_template("admin.html")
    elif(access == 'manager'):
        return render_template("manager.html", school_name = session.get('SCHOOL'))
    elif(access == 'student'):
        return render_template("student.html", school_name = session.get('SCHOOL'))
    elif(access == 'teacher'):
        return render_template("teacher.html", school_name = session.get('SCHOOL'))
    elif(access == 'none'):
        return render_template("main.html")
    else:
        return render_template("error.html")

@app.route('/queries/query1', methods = ['GET', 'POST'])
def queries_query1():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    if request.method == 'POST':
        mycursor = _dtbs_init.mydb.cursor()

        year = request.form.get("year")
        month = request.form.get("month")
        
        if len(month) == 1:
            month = '0' + month

        first_time = True
        for _ in mycursor.execute(f"CALL GetBorrowsByDate('{year}-{month}')", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        
        print(results)
        return render_template("query1.html", results = results)
    else:
        return render_template("query1.html")

@app.route('/queries/query2', methods = ['GET', 'POST'])
def queries_query2():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    mycursor.execute("SELECT category_name FROM categories")
    options_name = mycursor.fetchall()
    options_name = clean_list(options_name)
    if request.method == 'POST':

        category = request.form.get("category")

        first_time = True
        
        for _ in mycursor.execute(f"CALL GetCategoryTeacherAuthors('{category}')", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        
        return render_template("query2.html", opt_names = options_name, results = results)
    else:
        return render_template("query2.html", opt_names = options_name)

@app.route('/queries/query3')
def queries_query3():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
        
    for _ in  mycursor.execute("CALL GetYoungTeachers()", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("query3.html", results = results)

@app.route('/queries/query4')
def queries_query4():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
        
    for _ in  mycursor.execute("CALL GetAvailableAuthors()", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("query4.html", results = results)

@app.route('/queries/query5')
def queries_query5():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
        
    for _ in  mycursor.execute("CALL GetManagerSameBorrows()", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("query5.html", results = results)

@app.route('/queries/query6')
def queries_query6():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
        
    for _ in  mycursor.execute("CALL GetTopBorrowedCategory()", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("query6.html", results = results)

@app.route('/queries/query7')
def queries_query7():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
        
    for _ in  mycursor.execute("CALL GetLessThanFive()", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("query7.html", results = results)

@app.route('/queries/query21', methods = ['GET', 'POST'])
def queries_query21():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    for _ in mycursor.execute(f"CALL SearchBooksBySchool('{session.get('SCHOOL')}',NULL,NULL,NULL,NULL)", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    if request.method == 'POST':

        title = ''
        category = ''
        author_name = ''
        available_copies = ''
        results = []
        
        title = request.form.get("search_title")
        category = request.form.get("search_category")
        author_name = request.form.get("search_author_name")
        available_copies = request.form.get("search_available_copies")
        
        if title == '':
            title = 'NULL'
        else:
            title = "'" + title + "'"
        
        if category == '':
            category = 'NULL'
        else:
            category = "'" + category + "'"

        if author_name == '':
            author_name = 'NULL'
        else:
            author_name = "'" + author_name + "'"

        if available_copies == '':
            available_copies = 'NULL'
        else:
            available_copies = "'" + available_copies + "'"
                
        first_time = True
        
        for _ in mycursor.execute(f"CALL SearchBooksBySchool('{session.get('SCHOOL')}',{title},{category},{author_name},{available_copies})", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        
        return render_template("query21.html", results = results)
    else:
        return render_template("query21.html", results = results)

@app.route('/queries/query21/<int:ISBN>')
def queries_query21_ISBN(ISBN):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    for _ in mycursor.execute(f"CALL SelectBookByISBN({ISBN})", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    return render_template("query21all.html", results = results)

@app.route('/queries/query21/<int:ISBN>/addcopies', methods = ['GET','POST'])
def queries_query21_ISBN_addcopies(ISBN):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    mycursor.execute(f"SELECT available_copies FROM book_school_unit WHERE ISBN = {ISBN} AND school_name = '{session.get('SCHOOL')}'")
    available_copies = mycursor.fetchall()
    available_copies = clean(available_copies)
    if request.method == 'POST':

        add_copies = request.form.get('add_copies')
        
        first_time = True

        entry = f"CALL AddCopies({ISBN},'{session.get('SCHOOL')}',{add_copies})"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in mycursor.execute(entry, multi=True):
            pass
        return redirect(f'/queries/query21/{ISBN}')
    else:
        return render_template("copies.html", isbn = ISBN, school_name = session.get('SCHOOL'), available_copies = available_copies)

@app.route('/queries/query21/<int:ISBN>/edit', methods = ['GET','POST'])
def queries_query21_ISBN_edit(ISBN):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    
    first_time = True
    for _ in mycursor.execute(f"CALL SelectBookByISBN({ISBN})", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    if request.method == 'POST':

        title = request.form.get('title')
        image = request.form.get('image')
        languages = request.form.get('languages')
        keywords = request.form.get('keywords')
        publisher = request.form.get('publisher')
        page_num = request.form.get('page_num')
        summary = request.form.get('summary')
        authors = request.form.get('authors')
        categories = request.form.get('categories')
        copies = request.form.get('copies')
        
        first_time = True

        entry = f"CALL EditBook({ISBN},'{image}','{title}','{languages}','{keywords}','{publisher}',{page_num},'{summary}','{authors}','{categories}',{copies},'{session.get('SCHOOL')}')"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in mycursor.execute(entry, multi=True):
            pass
        
        return redirect(f'/queries/query21/{ISBN}')
    else:
        return render_template("managereditsbooks.html", results = results)

@app.route('/queries/query22', methods = ['GET', 'POST'])
def queries_query22():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    for _ in mycursor.execute(f"CALL GetUsersWithUnreturnedBooks('{session.get('SCHOOL')}',NULL,NULL,NULL)", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    if request.method == 'POST':

        first_name = ''
        last_name = ''
        overdue_days = ''
        results = []
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        overdue_days = request.form.get("overdue_days")
        
        if first_name == '':
            first_name = 'NULL'
        else:
            first_name = "'" + first_name + "'"
        
        if last_name == '':
            last_name = 'NULL'
        else:
            last_name = "'" + last_name + "'"

        if overdue_days == '':
            overdue_days = 'NULL'
                
        first_time = True
        
        for _ in mycursor.execute(f"CALL GetUsersWithUnreturnedBooks('{session.get('SCHOOL')}',{first_name},{last_name},{overdue_days})", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        return render_template("query22.html", results = results)
    else:
        return render_template("query22.html", results = results)

@app.route('/queries/query23', methods = ['GET', 'POST'])
def queries_query23():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    for _ in mycursor.execute("CALL GetUserAverageRatings(NULL)", multi=True):
        if first_time:
            results_users = mycursor.fetchall()
            first_time = False
    first_time = True
    for _ in mycursor.execute("CALL GetCategoryAverageRatings(NULL)", multi=True):
        if first_time:
            results_categories = mycursor.fetchall()
            first_time = False
    if request.method == 'POST':

        first_name = ''
        last_name = ''
        overdue_days = ''
        results = []
        
        username = request.form.get("search_username")
        category_name = request.form.get("search_category_name")
        
        if username == '':
            username = 'NULL'
        else:
            username = "'" + username + "'"
        
        if category_name == '':
            category_name = 'NULL'
        else:
            category_name = "'" + category_name + "'"        

        first_time = True
        for _ in mycursor.execute(f"CALL GetUserAverageRatings({username})", multi=True):
            if first_time:
                results_users = mycursor.fetchall()
                first_time = False
        first_time = True
        for _ in mycursor.execute(f"CALL GetCategoryAverageRatings({category_name})", multi=True):
            if first_time:
                results_categories = mycursor.fetchall()
                first_time = False
    
        return render_template("query23.html", results_users = results_users, results_categories = results_categories)
    else:
        return render_template("query23.html", results_users = results_users, results_categories = results_categories)

@app.route('/queries/query31', methods = ['GET', 'POST'])
def queries_query31():
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    for _ in mycursor.execute(f"CALL SearchBooksByCriteria('{session.get('SCHOOL')}',NULL,NULL,NULL)", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    if request.method == 'POST':

        title = ''
        category = ''
        author_name = ''
        results = []
        
        title = request.form.get("search_title")
        category = request.form.get("search_category")
        author_name = request.form.get("search_author_name")
        
        if title == '':
            title = 'NULL'
        else:
            title = "'" + title + "'"
        
        if category == '':
            category = 'NULL'
        else:
            category = "'" + category + "'"

        if author_name == '':
            author_name = 'NULL'
        else:
            author_name = "'" + author_name + "'"
                
        first_time = True
        
        for _ in mycursor.execute(f"CALL SearchBooksByCriteria('{session.get('SCHOOL')}',{title},{category},{author_name})", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        
        return render_template("query31.html", results = results)
    else:
        return render_template("query31.html", results = results)

@app.route('/queries/query31/<int:ISBN>')
def queries_query31_ISBN(ISBN):
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    reserved = ''
    for status in ['reserved', 'pending', 'lended', 'due return', 'in queue']:
        mycursor.execute(f"SELECT borrow_id FROM borrow WHERE status = '{status}' AND ISBN = {ISBN} AND username = '{session.get('USER')}'")
        reserved = reserved + clean(mycursor.fetchall())
        
    reviewed = ''
    mycursor.execute(f"SELECT rating FROM book_reviews WHERE username = '{session.get('USER')}' AND ISBN = {ISBN}")
    reviewed = reviewed + clean(mycursor.fetchall())
        
    first_time = True
    for _ in mycursor.execute(f"CALL SelectBookByISBN({ISBN})", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    return render_template("bookdetails.html", results = results, reserved = reserved, reviewed = reviewed)

@app.route('/queries/query31/<int:ISBN>/review', methods = ['GET','POST'])
def queries_query31_ISBN_review(ISBN):
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':

        comment = request.form.get('comment')
        rating = request.form.get('rating')

        entry = f"CALL InsertBookReview('{session.get('USER')}',{ISBN},'{comment}',{rating})"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in mycursor.execute(entry, multi=True):
            pass
        
        return redirect(f'/queries/query31/{ISBN}')
    else:
        mycursor.execute(f"SELECT title FROM books WHERE ISBN = {ISBN}")
        title = mycursor.fetchall()
        title = clean(title)
        return render_template("makebookreview.html", title = title, ISBN = ISBN)

@app.route('/queries/query31/<int:ISBN>/reviews')
def queries_query31_ISBN_reviews(ISBN):
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    first_time = True
    for _ in mycursor.execute(f"CALL GetBookReviews({ISBN})", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("bookreviews.html", results = results)

@app.route('/queries/query31/<int:ISBN>/reserve')
def queries_query31_ISBN_reserve(ISBN):
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    entry = f"CALL UserBorrowRequest('{session.get('USER')}',{ISBN})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in mycursor.execute(entry, multi=True):
        pass
    
    return redirect(f'/queries/query31/{ISBN}')

@app.route('/queries/query32')
def queries_query32():
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    first_time = True
    for _ in mycursor.execute(f"CALL GetUserBorrowedBooks('{session.get('USER')}')", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template("query32.html", results = results)

@app.route('/myprofile')
def myprofile():
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    first_time = True
    for _ in mycursor.execute(f"CALL GetUserDetails('{session.get('USER')}')", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False

    if access == 'teacher':
        return render_template("tinfo.html", results = results)
    elif access == 'student':
        return render_template("sinfo.html", results = results)
    else:
        return render_template("error.html")

@app.route('/myprofile/edit', methods = ['GET','POST'])
def myprofile_edit():
    access = session.get('ACCESS')
    if access != 'teacher':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':

        f_name = request.form.get('first_name')
        l_name = request.form.get('last_name')
        b_date = request.form.get('birth_date')

        entry = f"CALL EditTeacherUser('{session.get('USER')}','{f_name}','{l_name}','{b_date}')"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        first_time = True
        for _ in mycursor.execute(entry, multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        print(results)
        return redirect('/myprofile')
    else:
        first_time = True
        for _ in mycursor.execute(f"CALL GetUserDetails('{session.get('USER')}')", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        return render_template("editteacher.html", results = results)

@app.route('/myprofile/changepassword', methods = ['GET','POST'])
def myprofile_changepassword():
    access = session.get('ACCESS')
    if access != 'teacher' and access != 'student':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':

        old_pass = request.form.get('old_password')
        new_pass = request.form.get('new_password')

        entry = f"CALL ChangePass('{session.get('USER')}','{old_pass}','{new_pass}')"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        first_time = True
        for _ in mycursor.execute(entry, multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        results = clean(results)
        print(results)
        if results == 'Password updated successfully.':
            return redirect('/')
        else:
            return redirect('/myprofile/changepassword')
    else:
        return render_template("changepassword.html")

@app.route('/users', methods = ['GET', 'POST'])
def users():
    access = session.get('ACCESS')
    if access == 'admin':
        mycursor = _dtbs_init.mydb.cursor()
        if request.method == 'POST':
    
            username = ''
            school = ''
            
            username = request.form.get("username")
            school = request.form.get("school")
    
            if username == '':
                username = 'NULL'
            else:
                username = "'" + username + "'"
            
            if school == '':
                school = 'NULL'
            else:
                school = "'" + school + "'"
                
            first_time = True
            
            for _ in  mycursor.execute(f"CALL GetAcceptedUsers({school},{username})", multi=True):
                if first_time:
                    results = mycursor.fetchall()
                    first_time = False
            
            return render_template("adminallusers.html", results = results)
        else:
            first_time = True
            
            for _ in  mycursor.execute("CALL GetAcceptedUsers(NULL,NULL)", multi=True):
                if first_time:
                    results = mycursor.fetchall()
                    first_time = False
            
            return render_template("adminallusers.html", results = results)
        
    elif access == 'manager':
        if request.method == 'POST':
    
            username = ''
            school = ''
            
            username = request.form.get("username")
    
            if username == '':
                username = 'NULL'
            else:
                username = "'" + username + "'"

            mycursor = _dtbs_init.mydb.cursor()
            first_time = True
            
            for _ in  mycursor.execute(f"CALL GetAcceptedUsersBySchool('{session.get('SCHOOL')}',{username})", multi=True):
                if first_time:
                    results = mycursor.fetchall()
                    first_time = False
            
            return render_template("allacceptedsts.html",school_name = session.get('SCHOOL'), results = results)
        else:

            mycursor = _dtbs_init.mydb.cursor()
            first_time = True
                
            for _ in  mycursor.execute(f"CALL GetAcceptedUsersBySchool('{session.get('SCHOOL')}',NULL)", multi=True):
                if first_time:
                    results = mycursor.fetchall()
                    first_time = False
            return render_template("allacceptedsts.html", school_name = session.get('SCHOOL'), results = results)
    else:
        return render_template("error.html")
    
@app.route('/users/managers', methods = ['GET', 'POST'])
def users_managers():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':
        first_time = True
    
        for _ in  mycursor.execute("CALL GetPendingManagers()", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False

        return render_template("adminapproves.html", results = results)
    else:
        first_time = True
    
        for _ in  mycursor.execute("CALL GetPendingManagers()", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False

        return render_template("adminapproves.html", results = results)

@app.route('/users/managers/accept/<string:username>')
def users_managers_accept(username):
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    entry = f"CALL UpdateUserStatusAndInsertManager('{username}')"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    mycursor.execute(entry)
    return redirect("/users/managers")

@app.route('/users/managers/deny/<string:username>')
def users_managers_deny(username):
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    entry = f"CALL UpdateUserStatusToDeniedManager('{username}')"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    mycursor.execute(entry)
    return redirect("/users/managers")

@app.route('/schools', methods = ['GET', 'POST'])
def schools():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':

        school_name = request.form.get('school_name')

        if school_name == '':
            school_name = 'NULL'
        else:
            school_name = "'" + school_name + "'"
        
        first_time = True
    
        for _ in  mycursor.execute(f"CALL GetSchools({school_name})", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False

        return render_template("admingetsallschools.html", results = results)
    else:
        first_time = True
        
        for _ in  mycursor.execute("CALL GetSchools(NULL)", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False

        return render_template("admingetsallschools.html", results = results)

@app.route('/schools/add', methods = ['GET', 'POST'])
def schools_add():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':

        school_name = request.form.get('school_name')
        principal = request.form.get('principal')
        manager_fn = request.form.get('lib_manager_fn')
        manager_ln = request.form.get('lib_manager_ln')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        email = request.form.get('email')
        phone = request.form.get('phone_num')

        entry = f"CALL InsertSchool('{school_name}','{principal}','{manager_fn}','{manager_ln}','{city}',{postal_code},'{email}',{phone})"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in  mycursor.execute(entry, multi=True):
            pass

        return redirect('/schools')
    else:
        return render_template("admininsertschool.html")

@app.route('/schools/<string:school_name>/edit', methods = ['GET', 'POST'])
def schools_edit(school_name):
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    if request.method == 'POST':

        principal = request.form.get('principal')
        manager_fn = request.form.get('lib_manager_fn')
        manager_ln = request.form.get('lib_manager_ln')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        email = request.form.get('email')
        phone = request.form.get('phone_num')

        entry = f"CALL UpdateSchool('{school_name}','{principal}','{manager_fn}','{manager_ln}','{city}',{postal_code},'{email}',{phone})"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in  mycursor.execute(entry, multi=True):
            pass

        return redirect('/schools')
    else:
        first_time = True
        print(school_name)
        for _ in  mycursor.execute(f"CALL GetSchools('{school_name}')", multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        return render_template("admineditsschool.html", results = results)

@app.route('/users/studentsteachers/delete/<string:username>')
def users_studentsteachers_delete(username):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL DeleteUser('{username}')"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    print(results)
    return redirect("/users")

@app.route('/users/studentsteachers/borrows')
def users_studentsteachers_borrows():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    
    for _ in  mycursor.execute(f"CALL SelectNonPendingBorrows('{session.get('SCHOOL')}')", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    return render_template("managerborrows.html", results = results)

@app.route('/users/studentsteachers/borrows/<int:borrow_id>/accept')
def users_studentsteachers_borrows_accept(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    entry = f"CALL ApproveBorrowRequest({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows')

@app.route('/users/studentsteachers/borrows/<int:borrow_id>/deny')
def users_studentsteachers_borrows_deny(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    entry = f"CALL DenyBorrowRequest({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows')

@app.route('/users/studentsteachers/borrows/<int:borrow_id>/lend')
def users_studentsteachers_borrows_lend(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL ChangeBorrowStatusToLended({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows')

@app.route('/users/studentsteachers/borrows/<int:borrow_id>/return')
def users_studentsteachers_borrows_return(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL ChangeBorrowStatusToReturned({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows')

@app.route('/users/studentsteachers/borrows/<int:borrow_id>/duereturn')
def users_studentsteachers_borrows_duereturn(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL ChangeBorrowStatusToDueReturn({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows')

@app.route('/users/studentsteachers/borrows/pending')
def users_studentsteachers_borrows_pending():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    
    for _ in  mycursor.execute(f"CALL ShowPendingBorrows('{session.get('SCHOOL')}')", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    return render_template("pendingborrows.html", results = results)

@app.route('/users/studentsteachers/borrows/pending/<int:borrow_id>/accept')
def users_studentsteachers_borrows_pending_accept(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL ApproveBorrowRequest({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows/pending')

@app.route('/users/studentsteachers/borrows/pending/<int:borrow_id>/deny')
def users_studentsteachers_borrows_pending_deny(borrow_id):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL DenyBorrowRequest({borrow_id})"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/studentsteachers/borrows/pending')

@app.route('/users/pending')
def users_pending():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    
    for _ in  mycursor.execute("CALL GetPendingUsers()", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    return render_template("managerappruser.html", results = results)

@app.route('/users/pending/<string:username>/accept_student')
def users_pending_accept_student(username):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL UpdateUserStatusAndInsert('{username}','student')"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/pending')

@app.route('/users/pending/<string:username>/accept_teacher')
def users_pending_accept_teacher(username):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL UpdateUserStatusAndInsert('{username}','teacher')"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/pending')

@app.route('/users/pending/<string:username>/deny')
def users_pending_deny(username):
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True

    entry = f"CALL UpdateUserStatusToDenied('{username}')"
    _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
    
    for _ in  mycursor.execute(entry, multi=True):
        pass
    return redirect('/users/pending')

@app.route('/books/add', methods = ['GET', 'POST'])
def books_add():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()

    ISBN = ''
    image = ''
    title = ''
    languages = ''
    keywords = ''
    publisher = ''
    page_num = ''
    summary = ''
    authors = ''
    categories = ''
    copies = ''
    
    if request.method == 'POST':
        
        ISBN = request.form.get('isbn')

        mycursor.execute(f"SELECT ISBN FROM books WHERE ISBN = {ISBN}")
        isbn_ = mycursor.fetchall()
        isbn_ = clean(isbn_)
        if isbn_ != '':
            return redirect(f'/queries/query21/{isbn_}')
        
        image = request.form.get('image')
        title = request.form.get('title')
        languages = request.form.get('languages')
        keywords = request.form.get('keywords')
        publisher = request.form.get('publisher')
        page_num = request.form.get('page_num')
        summary = request.form.get('summary')
        authors = request.form.get('authors')
        categories = request.form.get('categories')
        copies = request.form.get('copies')

        entry = f"CALL InsertBook({ISBN},'{image}','{title}','{languages}','{keywords}','{publisher}',{page_num},'{summary}','{authors}','{categories}',{copies},'{session.get('SCHOOL')}')"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in  mycursor.execute(entry, multi=True):
            pass
        
        return render_template("addbooks.html", school_name = session.get('SCHOOL'))
    else:
        return render_template("addbooks.html", school_name = session.get('SCHOOL'))

@app.route('/books/reservequeue')
def books_reservequeue():
    access = session.get('ACCESS')
    if access != 'manager':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    first_time = True
    
    for _ in  mycursor.execute(f"CALL SchoolReserveQueue('{session.get('SCHOOL')}')", multi=True):
        if first_time:
            results = mycursor.fetchall()
            first_time = False
    
    return render_template('reservequeues.html', results = results, school_name = session.get('SCHOOL'))

@app.route('/forms/manager', methods = ['GET', 'POST'])
def forms_manager():
    access = session.get('ACCESS')
    if access != 'none':
        return render_template("error.html")
    if request.method == 'POST':
        mycursor = _dtbs_init.mydb.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        b_date = request.form.get('b_date')
        school_name = request.form.get('school_name')
        key = request.form.get('key')
    
        first_time = True

        entry = f"CALL ManagerRegister('{username}','{password}','{f_name}','{l_name}','{b_date}','{school_name}',{key})"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in  mycursor.execute(entry, multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        results = clean(results)
        print(results)
        if results == 'Manager inserted successfully':
            return redirect('/')
        else:
            return redirect('/forms/manager')
    else:
        return render_template("managerform.html")

@app.route('/forms/studentteacher', methods = ['GET', 'POST'])
def forms_studentteacher():
    access = session.get('ACCESS')
    if access != 'none':
        return render_template("error.html")
    if request.method == 'POST':
        mycursor = _dtbs_init.mydb.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        b_date = request.form.get('b_date')
        school_name = request.form.get('school_name')
        user_type = request.form.get('user_type')
    
        first_time = True

        entry = f"CALL UserRegister('{username}','{password}','{f_name}','{l_name}','{b_date}','{school_name}','{user_type}')"
        _dtbs_init.allentries = _dtbs_init.allentries + '\n' + entry + ';'
        
        for _ in  mycursor.execute(entry, multi=True):
            if first_time:
                results = mycursor.fetchall()
                first_time = False
        results = clean(results)
        print(results)
        if results == 'User inserted successfully':
            return redirect('/')
        else:
            return redirect('/forms/studentteacher')
    else:
        return render_template("userform.html")

@app.route('/backup')
def backup():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    with open('backup.sql', 'w', encoding = 'utf-8') as file:
        file.write(_dtbs_init.allentries)
    return redirect('/')

@app.route('/restore')
def restore():
    access = session.get('ACCESS')
    if access != 'admin':
        return render_template("error.html")
    mycursor = _dtbs_init.mydb.cursor()
    backup_file_name = "backup.sql"
    
    print("Collecting backup.sql...")
    
    with open(backup_file_name, encoding = 'utf-8') as backup_file:
        backup = backup_file.read()
        
    print("Restoring last backup state...")
    
    first_time = True
    for _ in mycursor.execute(backup, multi=True):
        _ = mycursor.fetchall()
        
    return redirect('/')
    
