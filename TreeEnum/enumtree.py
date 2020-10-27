#!/usr/bin/env python3

import pandas as pd
import hashlib
import time
import os
import sys


def compute_md5(filename):
    with open(filename, "rb") as fd: data = fd.read()
    return hashlib.md5(data).hexdigest()

class FileTree:
    def __init__(self):
        self.columns = ['path', 'filename', 'date_create', 'md5', 'sha256']
        self.df_dirent = pd.DataFrame(columns = self.columns)

    def add_dirent(self, path, filename):        
        hexmd5 = compute_md5(path + "/" + filename)
        mtime = time.strftime("%Y %m %d %H:%M:%S",
                              time.gmtime(os.path.getmtime(path +
                                                           "/" + filename)))
        data = [path, filename, mtime, hexmd5, 'NOTCOMPUTED/NOTCOMPUTED']
        df_newdirent = pd.DataFrame([data], columns=self.columns)
        self.df_dirent = self.df_dirent.append(df_newdirent, ignore_index=True)
        
    def add_path(self, path, dirent=None):
        if dirent == None:
            realpath = path
            self.recursive = 0
        else:
            realpath = path + "/" + dirent
            self.recursive = self.recursive + 1
        for newdirent in os.listdir(realpath):
            print(newdirent)
            if os.path.isdir(realpath + "/" + newdirent):                
                if self.recursive < 2:
                    self.add_path(realpath, newdirent)
            else:
                self.add_dirent(realpath, newdirent)
        self.recursive = self.recursive - 1

    def gen_excel(self, filename):
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        self.df_dirent.to_excel(writer, sheet_name="FileListing")  # send df to writer
        worksheet = writer.sheets["FileListing"]  # pull worksheet object
        for idx, col in enumerate(self.df_dirent):  # loop through all columns
                series = self.df_dirent[col]
                max_len = max((
                    series.astype(str).map(len).max(),  # len of largest item
                    len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
                worksheet.set_column(idx, idx, max_len)  # set column width
        writer.save()
        #self.df_dirent.to_excel(filename)

def main():
    if len(sys.argv[1]):
        print("Usage: %s <file.xml> <path1> [<path2> ...]" % sys.argv[0])
        sys.exit(-1)
    ft = FileTree()
    for path in sys.argv[2:]:
        ft.add_path(path)
    ft.gen_excel(sys.argv[1])


if __name__ == "__main__":
    main()
