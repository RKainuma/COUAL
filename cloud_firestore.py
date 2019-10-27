#!/usr/bin/env python
# -*- coding: utf-8 -*-
import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate("./coual-cefec-firebase-adminsdk-uv5bf-38b2fb2901.json") # ダウンロードした秘密鍵
firebase_admin.initialize_app(cred)

db = firestore.client()

# メインコレクションから親ドキュメントを取得
colors_ref = db.collection('colors')
main_docs = colors_ref.get()

parent_docs = []
print("\n\n=======ドキュメント(base_color)========")
for main_doc in main_docs:
    parent_docs.append(main_doc.id)
    print(main_doc.id)


print("\n\n=======サブコレクション(negative)========")
for parent_doc in parent_docs:
    bad_ref = colors_ref.document(parent_doc).collection('negative')
    bad_docs = bad_ref.get()
    print("\nドキュメントのID(base_color): {} ".format(parent_doc))
    for bad_doc in bad_docs:
        print("accent_color=> {}".format(bad_doc.id))

