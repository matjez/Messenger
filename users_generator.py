def users_generator():
    import mysql.connector
    from random import randrange

    x = int(input("Ilu testowych użytkowników dodać?: "))
    try:
        conn = mysql.connector.connect(host="localhost",user="root",password="",database="messenger")
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(e)

    for i in range(x):

        def token_generator():
            chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
            ret = ""
            for i in range(24):
                ret += chars[randrange(62)]
            
            check_sql = "SELECT token FROM users WHERE token='%s'" % ret
            cursor.execute(check_sql)
            results = cursor.fetchall()
            if len(results) > 0:
                token_generator()
            return ret 

        def rand_nums():
            chars = "0123456789"
            ret = ""
            for i in range(9):
                ret += chars[randrange(10)]

            check_sql = "SELECT login FROM users WHERE login LIKE '%{}'".format(ret)
            cursor.execute(check_sql)
            results = cursor.fetchall()
            if len(results) > 0:
                ret = rand_nums()
            return ret 
        num = rand_nums()

        username = "TESTUSER{}".format(num)
        password = "123456789"
        email = "TEST-USER{}@test.pl".format(num)
        phone_number ="000000000"
        first_name = "TEST-USER"
        second_name = "TEST-USER"
        last_name  = "TEST-USER"
        birth_date = "0000-00-00"

        sql = "INSERT INTO users VALUES(null,'%s','%s','%s','%s','%s','%s','%s','test_user',1,'%s',%s,'%s');" % (username,password,email,phone_number,first_name,second_name,last_name,birth_date,'null',token_generator())
        cursor.execute(sql)
        conn.commit()
    return print("{} users added.".format(x))


print("""
Konsola administratora strony

1. Dodawanie testowych użytkowników
2. Zmiana ustawień serwera
 """)

while True:
    inp = input("Wybierz opcję: ")

    if inp == "1":
        users_generator()
    else:
        pass