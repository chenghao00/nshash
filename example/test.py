#!/usr/bin/env python3
# coding:utf-8
# Author: veelion@ebuinfo.com

import time
import xlrd

import nshash


def read_xls(fn):
    print('reading...', fn)
    wb = xlrd.open_workbook(fn)
    data = {}

    for sheet in wb.sheets():
        dest = []
        keys = {}
        for j in range(sheet.ncols):
            key = sheet.cell(0, j).value.strip().strip(',')
            keys[j] = key
        print(sheet.name, keys)
        for i in range(1, sheet.nrows):
            row = {}
            for j in range(sheet.ncols):
                value = sheet.cell(i, j).value
                key = keys[j]
                row[key] = value
            dest.append(row)
        data[sheet.name] = dest
    print('reading... done!', fn)
    return data


def get_hot_news(data_news, topn=30):
    nsh = nshash.NSHash('test', hashfunc='farmhash', hashdb='memory')
    similarids = {}
    for doc_id, d in enumerate(data_news):
        simid = nsh.get_similar(d['内容'])
        if simid in similarids:
            similarids[simid].add(doc_id)
        else:
            similarids[simid] = set([doc_id])
    zz = sorted(similarids.items(), key=lambda a: len(a[1]), reverse=True)
    return zz[:topn]



def process(fn):
    all_data = read_xls(fn)

    for sheet_name, data in all_data.items():
        b = time.time()
        hots = get_hot_news(data, 30)
        print(sheet_name, 'time cost:', time.time()-b)
        for simid, docids in hots:
            print('similar_id:', simid, 'count:', len(docids))
            for docid in docids:
                print('\t', data[docid]['标题'])
            print('==='*10)


if __name__ == '__main__':
    from sys import argv
    fn = argv[1]
    process(fn)

