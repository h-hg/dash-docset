import base64
import os
import re
import json
import sqlite3
import tarfile
from urllib import request

'''
Thanks:
    [gist-makeneovimdoc]: https://gist.github.com/ianding1/d02b9e03de68e4b11913b9afa1d56399
'''

resources = {
    'info_plist':'''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
    <dict>
        <key>CFBundleIdentifier</key><string>neovim</string>
        <key>CFBundleName</key><string>Neovim</string>
        <key>DocSetPlatformFamily</key><string>neovim</string>
        <key>isDashDocset</key><true/>
    </dict>
</plist>
''',
    'icon': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAC1klEQVQ4EVVTTUhUURQ+9703P01DRi1CAyEoIogWLRI1Lcg06WeRTJQ1tSrMMCUMSjezt0UIVlLRpkU4C6ko0wamTW5EohZBEq3MFJMcdeb57t/p3Duj1oX73rv3fOe73/nueQBmIDL7pkdX9mJv73jzNbNOYcqhl411vN0duTtac70nU7Xjn5gNGgCazRuZ5E0HdF9ZaPaz5yydT9VN/DAkKZbSJn5npHaUkKvSXW691/QljwjMKaYC1Dx7fpUL1ScVcqlgu1CRTkiVkgloCESABTfqnlGF+KOu4aNbGQN0KITRJ9PHxvOHbs3n9uYQCyCUuyIla7hdl20xiYl0wpRC+4grOQHgwCWtVrvNng1oycuBxdyPc40zy4W41hgwoZiSEtu6X9XvSp9LKwOmNQjKDwIELljlOgEvCBkWeWeel4up2RO/g2AxLIQTELiSM+g0QDO4QJSSlJgpNFGVFIDUjAcKPO2HJv4cnFnx909qnY+RF0tS66b2l7VnDVhIZDStEiKyvtgSgJNCOwUDYl9YPDUgpf+TFES5BBUo1tE2VL2TknwiNUTkh6FcU2CShWSSKwxpP/Yme3JK48JD8iFMM1CKVa4yr51zdIWgZDpECnuzRRPt6UQAUhGJ1lDxffPjll/DSrIMOV9GJy4Tvkk7rMrPy2IJ/ykw1tLphhpJWxkTtjSuo/dpa44LIFPRcyLuNqUJYlTQ3ChBSI8sDkNAxQWS5Xxp9aWT775RYz2QiFQKmcccxSLe2k2ENggCNUmuTBFJnFRoUHR5diDzYhUvpICsEhAXHBRGPMdchJbqQ5GA2hUG679Sn3YyoadZIGOgiwoSQ2nHNJHSrI8qnCM1dLWovE1e91jPp6fFQ8wzRS1txuWRAyw5+hpax/bYNSBLJBKu+W4crL3SMFCzeHyger2xaLuk1CDWSJLv98GFjP1lSwALau5v3nKk//BpA7Wj9IP9BbiivOvG51SQAAAAAElFTkSuQmCC',
    'icon@2x': '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',
}

def get_github_realse_latest_tag(repo):
    api_url = f'https://api.github.com/repos/{repo}/releases/latest'
    r = request.urlopen(api_url)
    return json.load(r)['tag_name']

def get_github_release_code_url(repo, tag):
    return f'https://github.com/{repo}/archive/refs/tags/{tag}.tar.gz'

def download(url, path):
    request.urlretrieve(url, path)
    r = request.urlopen(url)
    with open(path, mode='wb') as f:
        f.write(r.read())

def uncompress_tar_gz(src, dest):
    try:
        t = tarfile.open(src)
        t.extractall(path=dest)
        return os.path.commonprefix(t.getnames())
    except Exception as e:
        print(e)
        return None

def make_doc(src):
    global resources

    doc_path = os.path.join(src, 'runtime', 'doc')
    # Making tag
    print('Making tag...')
    os.system(f"nvim '+helptags {doc_path}' +q")

    # Generate HTML files
    print('Generate HTML files...')
    os.system(f'cd {doc_path} && make html >> makeneovimdoc.log 2>&1')
    
    # Creating docset directory
    print('Creating docset directory...')
    docset_path = 'Neovim.docset'
    docset_content_path = os.path.join(docset_path, 'Contents')
    docset_res_path = os.path.join(docset_content_path, 'Resources')
    docset_doc_path = os.path.join(docset_res_path, 'Documents')
    if not os.path.isdir(docset_doc_path):
        os.makedirs(docset_doc_path)

    # Creating Info.plist
    print('Creating Info.plist...')
    with open(os.path.join(docset_content_path, 'Info.plist'), 'w') as info_plist:
        info_plist.write(resources['info_plist'])

    # Coping HTML files
    print('Coping HTML files...')
    os.system(f'cp -r {doc_path}/*.html {docset_doc_path}')

    # Indexing
    print('Indexing...')
    def get_tag_type(tag):
        return 'Function'
    with open(os.path.join(doc_path, 'tags')) as tagfile:
        index_conn = sqlite3.connect(os.path.join(docset_res_path, 'docSet.dsidx'))
        index_cursor = index_conn.cursor()
        index_cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        index_cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

        for line in tagfile:
            tag, location_txt, pattern = line.split('\t')
            location_html = location_txt.replace('.txt', '.html')
            url_html = location_html + '#' + tag
            type_ = get_tag_type(tag)
            index_cursor.execute(
                'INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?);',
                (tag, type_, url_html))

        index_conn.commit()
        index_conn.close()

    # Making ICON
    print('Making ICON...')
    with open(os.path.join(docset_path, 'icon.png'), mode='wb') as f:
        f.write(base64.b64decode(resources['icon']))
    with open(os.path.join(docset_path, 'icon@2x.png'), mode='wb') as f:
        f.write(base64.b64decode(resources['icon@2x']))
    
    # Compressing the docset
    print('Compressing the docset...')
    os.system("tar --exclude='.DS_Store' -czf Neovim.tgz Neovim.docset")
    
def main():
    repo = 'neovim/neovim'
    tag = get_github_realse_latest_tag(repo)
    src_url = get_github_release_code_url(repo, tag)
    tar_gz_filename = os.path.basename(src_url)
    print(f'Downloading the Neovim {tag} source code...')
    # download(src_url, tar_gz_filename)
    dir = uncompress_tar_gz(tar_gz_filename, './')
    make_doc(dir)

if __name__ == '__main__':
    main()