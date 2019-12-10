# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 19:15:20 2018

@author: Matthew
"""
from sqlite3 import connect
from urllib.parse import unquote
import sys
conn = connect('cElegan.sqlite')
curs = conn.cursor()

def readSource(gffFile):
    """Reads in source file and formats for further use in other functions to construct a database as well as generates a primary key for the database
    Args:gff file
    Returns: a formated string indexed in two separate ways to be used in other functions as well as a primary key"""
    with open(gffFile,'r') as lines:
        featureID=0
        initTable()
        for line in lines:
            if line.startswith('#'): #skips over comment section of gff file
                continue
            featureID+=1 #Generate primary key
            fields=line.strip().split('\t')
            makeFeat(featureID, fields[:-1])
            makeAtt(featureID, fields[-1])


def initTable():
    """creates the featers and attributes table for cElegan database.
    Args:none
    Returns:none"""
    sql = """CREATE TABLE IF NOT EXISTS features (
    featureid INTEGER UNIQUE NOT NULL,
    seqid TEXT,
    source TEXT,
    type TEXT,
    start INTEGER,
    end INTEGER,
    score REAL,
    strand TEXT,
    phase TEXT,
    PRIMARY KEY( featureid )
    );"""

    curs.execute(sql)

    sql ="""CREATE TABLE IF NOT EXISTS attributes (
    featureid INTEGER NOT NULL,
    tag TEXT,
    value TEXT,
    FOREIGN KEY (featureid) REFERENCES features(featureid)
    );"""

    curs.execute(sql)


def makeFeat(primaryKey, features):
    """Creates features table for cElegan database as well as creates the
    features from the string and primarykey provided by the last function Args:
    a string of features (list of strings) and a primary key (int)

    Returns: Should create a table in the database"""

    column = [primaryKey] + features #add primary key to features
    sql = 'INSERT INTO features VALUES (?,?,?,?,?,?,?,?,?);' #Features table needs 9 columns, so have 9 "?s"
    curs.execute(sql, column)

def makeAtt(primaryKey, attributes):
    """Creates attributes table for cElegans database by further formating the last element of the gff file in the previous function
    Args:a integer that acts as a primary key and a list of strings 
    Returns: should creat a table in the cElegans database"""
    attributes = attributes.split(';')
    for item in attributes:
        tag, value = item.split('=')
        values = value.split(',')
        for val in values:
            unquoted=[primaryKey]+[tag]+[unquote(val)]
            sql = 'INSERT INTO attributes VALUES (?,?,?);'
            curs.execute(sql, unquoted)
            
def makeIndex():
    sql="""CREATE INDEX foreign_keyid ON attributes(featureid);"""
    curs.execute(sql)
    sql="""CREATE INDEX type_id ON features(type);"""
    curs.execute(sql)
    sql="""CREATE INDEX value_id ON attributes(value);"""
    curs.execute(sql)
    sql="""CREATE INDEX start_id ON features(start);"""
    curs.execute(sql)
    sql="""CREATE INDEX stop_id ON features(end);"""
    curs.execute(sql)
    sql="""CREATE INDEX seqid_id ON features(seqid)"""
    curs.execute(sql)
    
def main():
    sourceFile=sys.argv[1]
    readSource(sourceFile)
    makeIndex()
    conn.commit()
    curs.close()
    conn.close()

if __name__ == '__main__':
        main()
