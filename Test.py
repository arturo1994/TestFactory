
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm 
from datetime import datetime





def CreateDataBase(database, user, password, host, port, newBase):
    
    '''
   function that creates the database

    database str : database name
    user str : user name
    password str : paswowrd of database
    host str: host of database
    port str: number of port
    newBase str: dabase to be create
    :return: null
   '''

    sqlQuery = 'CREATE database ' + newBase
    
    engine = create_engine(str('postgresql://postgres:'+password+'@'+host+':'+port+'/'+database))
    conn = engine.connect()
    conn.execute("commit")

    try:
        conn.execute(sqlQuery)
        print("Database " + newBase +" created successfully........")
    except:
        print("Database " + newBase +" created unsuccessfully........")        
    
    conn.close()


    engine.dispose()




def createTable(data, table, database, user, password, host, port):
    
    '''
   function that creates the table
   
    data pandas.DataFrame: data to be insert
    table str: name of table
    database str : database name
    user str : user name
    password str : paswowrd of database
    host str: host of database
    port str: number of port
    newBase str: dabase to be create
    :return: null
   '''
    
    
    data.location = data.location.apply(lambda x: str(x).replace("'", "’"))
    
    engine = create_engine(str('postgresql://postgres:'+password+'@'+host+':'+port+'/'+database))

    k = []
    for n in range(len(data.dtypes)):
        if data.dtypes[n] == 'object':
            k.append(data.dtypes.index[n] + " TEXT")
        if data.dtypes[n] == 'int64' or data.dtypes[n] == 'float64':
            k.append(data.dtypes.index[n] + " FLOAT")


    k1 = list(data.dtypes.index)

    sql = 'CREATE TABLE '+table+'(' + ", ".join(k) + ", UNIQUE (" + ", ".join(k1)+"))" 
    data = data.fillna("NoValue")
    data = data.set_index(data.columns[0])
    
    try:
        engine.execute(sql)
    except:
        print("table" + table +" created unsuccessfully........")

    data = data.reset_index()



    for m in tqdm(range(len(data))):
        k1 = list(data.loc[m].fillna("NoValue").index)
        k1 = [str(a) for a in k1]
        k1 = ", ".join(k1)


        k = data.loc[m].fillna("NoValue").to_list()
        for i in range(len(k)):
            if str(type(k[i])) == "<class 'str'>":
                k[i] = "'" + k[i] + "'"
        k = [str(a) for a in k]
        k = [a.replace(",", "") for a in k]
        k = ", ".join(k)

        try:
            sql = '''INSERT INTO public.'''+ table +'''('''+k1+ ") VALUES ("+k+ ") ON CONFLICT DO NOTHING"
            engine.execute(sql)
        except:
            print("Fila " + str(m) +" no insertada")



def Views(database, user, password, host, port, sqlQuery):
    
    '''
   function that creates a view
   
    database str : database name
    user str : user name
    password str : paswowrd of database
    host str: host of database
    port str: number of port
    sqlQuery str: Query to be execute 
    :return: null
   '''
    
    engine = create_engine(str('postgresql://postgres:'+password+'@'+host+':'+port+'/'+database))


    sql = sqlQuery
    try:
        engine.execute(sql)
    except:
        print("View " + " created unsuccessfully........") 
            
    engine.dispose()


def InsertInTable(data, table, database, user, password, host, port):
    
    '''
   function that insert from DataFrame
   
    data pandas.DataFrame:: data to be insert
    database str : database name
    user str : user name
    password str : paswowrd of database
    host str: host of database
    port str: number of port
    :return: null
   '''
    
    engine = create_engine(str('postgresql://postgres:'+password+'@'+host+':'+port+'/'+database))

    data.location = data.location.apply(lambda x: str(x).replace("'", "’"))


    for n in tqdm(range(len(data))):
        k1 = list(data.loc[n].fillna("NoValue").index)
        k1 = [str(a) for a in k1]
        k1 = ", ".join(k1)


        k = data.loc[n].fillna("NoValue").to_list()
        for i in range(len(k)):
            if str(type(k[i])) == "<class 'str'>":
                k[i] = "'" + k[i] + "'"
        k = [str(a) for a in k]
        k = [a.replace(",", "") for a in k]
        k = ", ".join(k)


        sql = '''INSERT INTO public.'''+ table +'''('''+k1+ ") VALUES ("+k+ ") ON CONFLICT DO NOTHING"
        try:
            engine.execute(sql)
        except:
            print("Fila " + str(n) +" no insertada")
            
    engine.dispose()




def ReadView(sqlQuery, database, user, password, host, port):
    
    '''
   function that read a view
   
    database str : database name
    user str : user name
    password str : paswowrd of database
    host str: host of database
    port str: number of port
    sqlQuery str: Query to be execute 
    :return: null
   '''
    
    engine = create_engine(str('postgresql://postgres:'+password+'@'+host+':'+port+'/'+database))

    
    try:
        data = pd.read_sql_query(sqlQuery,con=engine)
    except:
        print("could not be read view")

    engine.dispose()
    return(data)


def Graf(view1, view2):
    
    '''
   function that create some images
   
    view1 pandas.DataFrame:: data from the first view
    view2 pandas.DataFrame:: data from the second view
    :return: null
   '''
    

    view1.date = view1.date.apply(lambda x: datetime.fromtimestamp(x))
    view2.date = view2.date.apply(lambda x: datetime.fromtimestamp(x))

    data = view1[view1["date"]>="2021-07-28"][["date", 'avg_positive', "avg_neutral", "avg_negative"]]
    data = data.resample('60min', on='date').mean().reset_index()

    fig = px.bar(data, x='date', y=["avg_positive", "avg_neutral","avg_negative"],color_discrete_sequence = ["blue","gray","red"])
    fig.write_image("avarage_senti.png")


    data = view2[view2["date"]>="2021-07-28"][["date", 'count_positive', "count_neutral", "count_negative"]]
    df = data.resample('60min', on='date').sum()

    fig = px.line(df)
    fig.write_image("count1.png")

    df = data.resample('60min', on='date').sum()
    df1 = df.drop("count_neutral", axis = 1)

    fig = px.line(df1)
    fig.write_image("count2.png")




