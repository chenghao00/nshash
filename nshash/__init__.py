#!/usr/bin/env python
# coding:utf-8
# Author: veelion@ebuinfo.com

import pickle
import os
import re
import hashlib
import traceback


class HashDBLeveldb:
    def __init__(self, name):
        import leveldb
        db_name = name + '.hashdb'
        self.db = leveldb.LevelDB(db_name)

    def get(self, key):
        if isinstance(key, str):
            key = key.encode('utf8')
        elif isinstance(key, int):
            key = str(key).encode()
        try:
            value = self.db.Get(key).decode()
        except:
            value = None
        return value

    def put(self, key, value):
        if isinstance(key, str):
            key = key.encode('utf8')
        elif isinstance(key, int):
            key = str(key).encode('utf8')
        if isinstance(value, str):
            value = value.encode('utf8')
        elif isinstance(value, int):
            value = str(value).encode('utf8')
        self.db.Put(key, value)


class HashDBMemory:
    def __init__(self, name):
        self.name = name
        self.db_name = name + '.hashdb.pkl'
        self.db = {}
        if os.path.isfile(self.db_name):
            with open(self.db_name, 'rb') as f:
                try:
                    self.db = pickle.load(f)
                except:
                    traceback.print_exc()
                    self.db = {}

    def __del__(self):
        with open(self.db_name, 'wb') as f:
            pickle.dump(self.db, f)

    def get(self, key):
        return self.db.get(key)

    def put(self, key, value):
        self.db[key] = value


class NSHash:
    '''using top-n longest sentences' hashes to identify similar documents'''
    def __init__(self, name, hashfunc='md5', hashdb='memory'):
        '''
        hashfunc: md5, farmhash or others in module: hashlib
        '''
        if hashfunc == 'farmhash':
            import farmhash
            self.hashfunc = farmhash.hash64
        elif hashfunc == 'md5':
            def md5hash(s):
                if isinstance(s, str):
                    s = s.encode('utf8')
                return hashlib.md5(s).hexdigest()
            self.hashfunc = md5hash
        else:
            raise Exception('not supported hash function type')
        if hashdb == 'memory':
            self.db = HashDBMemory(name)
        else:
            self.db = HashDBLeveldb(name)
        self.max_similar_id = self.db.get('max_similar_id')
        if self.max_similar_id is None:
            self.max_similar_id = 0

    def get_nshash(self, doc, n=5):
        sentences = re.split(r':|：|；|？|。|！|】|\n', doc)
        ss = [s for s in sentences if len(s)>30]
        if not ss:
            ss = sentences
        ss.sort(key=lambda a: len(a), reverse=True)
        ss = ss[:n]
        hashes = [self.hashfunc(s) for s in ss]
        return hashes

    def get_similar(self, doc):
        hashes = self.get_nshash(doc)
        doc_similar_id = 0
        simids = []
        for h in hashes:
            simid = self.db.get(h)
            if simid:
                simids.append(simid)
        if simids:
            doc_similar_id = min(simids)
        else:
            self.max_similar_id += 1
            doc_similar_id = self.max_similar_id
        for h in hashes:
            self.db.put(h, doc_similar_id)
        return doc_similar_id
