import sys
from urllib.parse import unquote
from sqlite3 import connect


def db_connect(db_name):
    conn = connect(db_name)
    curs = conn.cursor()
    
    drop = ['DROP TABLE IF EXISTS features',
            'DROP TABLE IF EXISTS attributes']
    for d in drop:
        curs.executemany(sql, d)
    
    create_features = '''CREATE TABLE features (
        featureid INTEGER PRIMARY KEY,
        seqid TEXT,
        source TEXT,
        type TEXT,
        start INTEGER,
        end INTEGER,
        score REAL,
        strand TEXT,
        phase TEXT
    );'''
    
    create_attributes = '''CREATE TABLE attributes (
        featureid INTEGER NOT NULL,
        tag TEXT,
        value TEXT,
        
        FOREIGN KEY(featureid) REFERENCES features(featureid)
    );'''
    
    curs.execute(create_features)
    curs.execute(create_attributes)
    return conn, curs


def insert_feature(feature_list, cursor):
    ins_feat = 'INSERT INTO features VALUES (?,?,?,?,?,?,?,?,?);'
    cursor.execute(ins_feat, feature_list)


def insert_attribute(featureid, attributes, cursor):
    ins_attr = 'INSERT INTO attributes VALUES (?,?,?);'
    attrs = attributes.split(';')
    for attr in attrs:
        tag, vals = attr.split('=')
        vals = vals.split(',')
        for val in vals:
            att = [featureid, tag, unquote(v)]
            cursor.execute(ins_attr, att)


def main():
    gff, db = sys.argv[:2]
    conn, curs = db_connect(db)
    with open(gff) as gff:
        featureid = 0
        for line in gff:
            if line.startswith('#'): continue
            featureid += 1
            line = line.strip().split('\t')
            insert_feature([featureid] + line[:-1], curs)
            insert_attribute(featureid, line[-1], curs)
    idxs = ['CREATE INDEX attributes_value_idx ON attributes(value);',
            'CREATE INDEX features_type_idx ON features(type);',
            'CREATE INDEX features_start_idx ON features(start);'
            'CREATE INDEX features_end_idx ON features(end);']
    for idx in idxs:
        curs.execute(idx)
    conn.commit()
    curs.close()
    conn.close()


if __name__ == '__main__':
    main()