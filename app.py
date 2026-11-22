#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""karimenquiz — 仮免（仮免許）学科試験対策 ○×カードクイズ.

普通自動車の仮免許学科試験に向けた、○×（まるばつ）形式の学習用クイズ。
問題は道路交通法の基本的な内容をもとに独自に作成した学習用問題であり、
公式の試験問題ではない。

目次（Unit 一覧）
  Unit 1: 問題データ（全100問・4カテゴリ×25問）
  Unit 2: Web ルート（ページ配信 / API / ヘルスチェック）
  Unit 3: 画面（HTML / CSS / JavaScript）
"""

import json

from flask import Flask, Response, jsonify

app = Flask(__name__)

# ============================================================
# Unit 1: 問題データ（全100問・4カテゴリ×25問）
# ============================================================
# answer が true の文は「正しい（○）」、false の文は「誤り（×）」。
QUESTIONS = [
    # ---- 交通ルールの基礎（25問） ----
    {"q": "青信号は、「進むことができる」という意味である。", "answer": True,
     "explanation": "青信号は命令ではなく、進むことができることを示します。ただし、交差点内が混んでいて進むと止まってしまうようなときは、入ってはいけません。",
     "category": "交通ルールの基礎"},
    {"q": "黄色信号では、安全に止まれない場合でも、必ず急ブレーキをかけて止まらなければならない。", "answer": False,
     "explanation": "黄色信号は停止の合図ですが、停止位置で安全に止まれないときは、そのまま進むことができます。急ブレーキは追突の危険があります。",
     "category": "交通ルールの基礎"},
    {"q": "赤信号では、停止位置を越えて進んではならない。", "answer": True,
     "explanation": "赤信号は「止まれ」の意味です。停止線がある場合はその手前で止まります。",
     "category": "交通ルールの基礎"},
    {"q": "信号のない交差点では、右方から来る車を優先させなければならない。", "answer": False,
     "explanation": "信号や優先の指定がない交差点では、左方から来る車が優先です（左方優先）。",
     "category": "交通ルールの基礎"},
    {"q": "一般道路での自動車の法定最高速度は、時速60キロメートルである。", "answer": True,
     "explanation": "法定速度は、一般道路では時速60キロメートル、高速自動車国道では原則として時速100キロメートルです。",
     "category": "交通ルールの基礎"},
    {"q": "原動機付自転車の法定最高速度は、時速50キロメートルである。", "answer": False,
     "explanation": "原動機付自転車の法定最高速度は時速30キロメートルです。",
     "category": "交通ルールの基礎"},
    {"q": "高速自動車国道の本線車道での普通自動車の法定最高速度は、原則として時速100キロメートルである。", "answer": True,
     "explanation": "その通りです。ただし、標識で別の速度が指定されている場合はそちらに従います。",
     "category": "交通ルールの基礎"},
    {"q": "最高速度の標識がない道路では、時速40キロメートルを超えて走ってはならない。", "answer": False,
     "explanation": "標識がない場合は法定速度が適用され、一般道路では時速60キロメートルまで認められています。",
     "category": "交通ルールの基礎"},
    {"q": "運転するときは、免許証を必ず携帯しなければならない。", "answer": True,
     "explanation": "免許証の携帯は義務です。忘れて運転すると携帯義務違反になります。",
     "category": "交通ルールの基礎"},
    {"q": "免許証を携帯せずに運転しても、後から提示すれば違反にはならない。", "answer": False,
     "explanation": "提示しても携帯義務違反は成立します。運転の前に必ず確認しましょう。",
     "category": "交通ルールの基礎"},
    {"q": "飲酒運転は、飲んだ量が少なくても禁止されている。", "answer": True,
     "explanation": "酒気を帯びての運転は量にかかわらず禁止です。酒を飲んだら運転しない、が原則です。",
     "category": "交通ルールの基礎"},
    {"q": "自転車は、酒を飲んで運転しても罰せられない。", "answer": False,
     "explanation": "自転車も軽車両として飲酒運転が禁止されており、罰則があります。",
     "category": "交通ルールの基礎"},
    {"q": "初心運転者期間は、免許を取得してから1年間である。", "answer": True,
     "explanation": "初心運転者期間は取得後1年間で、この期間は初心者マークの表示義務があります。",
     "category": "交通ルールの基礎"},
    {"q": "自動車を運転するときは、その自動車の自動車検査証（車検証）を備え付けておかなければならない。", "answer": True,
     "explanation": "車検証の備え付けは義務です。検査標章（ステッカー）も表示します。",
     "category": "交通ルールの基礎"},
    {"q": "黄色の点滅信号は、「止まれ」の意味である。", "answer": False,
     "explanation": "黄色の点滅は「他の交通に注意して進むことができる」という意味です。一時停止に近い意味なのは赤色の点滅信号です。",
     "category": "交通ルールの基礎"},
    {"q": "赤色の点滅信号では、停止位置で一時停止しなければならない。", "answer": True,
     "explanation": "赤色の点滅は、一時停止して安全を確認してから進むことができるという意味です。",
     "category": "交通ルールの基礎"},
    {"q": "青色の矢印信号が出ているときは、信号が赤でも、その矢印の方向に進むことができる。", "answer": True,
     "explanation": "矢印信号は、赤信号でも示された方向への進行を認めるものです。",
     "category": "交通ルールの基礎"},
    {"q": "右折の青色矢印信号が出ているときは、転回（Uターン）もできる。", "answer": False,
     "explanation": "右折の矢印信号では転回はできません。転回ができるのは青信号のときなどに限られます。",
     "category": "交通ルールの基礎"},
    {"q": "歩行者用信号が青色の点滅に変わったら、横断中の歩行者は速やかに横断を終えるか、引き返さなければならない。", "answer": True,
     "explanation": "青色の点滅は「横断を始めてはいけない、横断中なら急ぐ」という意味です。",
     "category": "交通ルールの基礎"},
    {"q": "片側一車線の道路では、対向車がいなければ、道路の中央から右側の部分を通行してもよい。", "answer": False,
     "explanation": "日本は左側通行です。中央から右側の部分は、追い越しなど決められた場合を除いて通行できません。",
     "category": "交通ルールの基礎"},
    {"q": "追い越しをするときは、原則として前の車の右側を通らなければならない。", "answer": True,
     "explanation": "追い越しは右側からが原則です。ただし、前の車が右折のため中央に寄っているときなどは左側を通ります。",
     "category": "交通ルールの基礎"},
    {"q": "左折するときは、あらかじめ道路の中央に寄っておく。", "answer": False,
     "explanation": "左折は、あらかじめ道路の左側端に寄って、徐行しながら曲がります。中央に寄るのは右折のときです。",
     "category": "交通ルールの基礎"},
    {"q": "右折するときは、あらかじめ道路の中央に寄らなければならない。", "answer": True,
     "explanation": "右折は中央に寄り、交差点の中心の直後あたりで徐行しながら曲がるのが基本です。",
     "category": "交通ルールの基礎"},
    {"q": "警察官が腕を垂直に上げている手信号は、対面する交通に対して「進め」の意味である。", "answer": False,
     "explanation": "腕を垂直に上げる手信号は、対面する交通に対しては黄色信号と同じ意味です。",
     "category": "交通ルールの基礎"},
    {"q": "交差点に警察官がいて手信号をしているときは、信号機の表示より警察官の手信号を優先する。", "answer": True,
     "explanation": "警察官や交通巡視員の手信号は、信号機の表示に優先します。",
     "category": "交通ルールの基礎"},

    # ---- 標識・標示（25問） ----
    {"q": "「止まれ」の標識（一時停止）は、逆三角形の形をしている。", "answer": True,
     "explanation": "一時停止の標識は、ほかの標識と区別できるよう逆三角形になっています。",
     "category": "標識・標示"},
    {"q": "一方通行の標識がある道路では、矢印の方向と反対向きに進んではならない。", "answer": True,
     "explanation": "一方通行では、指定された方向にしか進めません。出口側には車両進入禁止の標識が置かれることがあります。",
     "category": "標識・標示"},
    {"q": "車両進入禁止の標識は、その標識のある方向から車が進入することを禁止するものである。", "answer": True,
     "explanation": "赤地に白い横棒の標識で、一方通行の出口側などに設置されます。",
     "category": "標識・標示"},
    {"q": "駐車禁止の標識がある場所では、短時間の停車も一切できない。", "answer": False,
     "explanation": "駐車禁止の場所でも、人の乗り降りなどのための停車はできます。停車も禁止されるのは駐停車禁止の場所です。",
     "category": "標識・標示"},
    {"q": "駐停車禁止の標識がある場所では、人の乗り降りのための短い停車もできない。", "answer": True,
     "explanation": "駐停車禁止は、駐車と停車の両方を禁止する規制です。",
     "category": "標識・標示"},
    {"q": "最高速度50の標識がある道路では、交通がすいていれば時速60キロメートルまで出してもよい。", "answer": False,
     "explanation": "標識で指定された速度が法定速度より優先されます。50の標識があれば時速50キロメートルが上限です。",
     "category": "標識・標示"},
    {"q": "横断歩道の標識には、歩行者が横断歩道を渡っている図柄が描かれている。", "answer": True,
     "explanation": "指示標識の一つで、横断歩道があることを示します。青地に白い図柄です。",
     "category": "標識・標示"},
    {"q": "「学校、幼稚園、保育所等あり」の標識は、子どもの飛び出しに注意すべき場所に設置される。", "answer": True,
     "explanation": "警戒標識の一つです。この標識を見たら速度を落とし、子どもの動きに注意します。",
     "category": "標識・標示"},
    {"q": "徐行の標識がある場所では、時速10キロメートル以下で走れば、徐行したことになる。", "answer": False,
     "explanation": "徐行とは「直ちに停止できるような速度」のことで、具体的な数値で決まっているわけではありません。",
     "category": "標識・標示"},
    {"q": "追越し禁止の標識がある場所では、原動機付自転車だけは追い越しをしてもよい。", "answer": False,
     "explanation": "追越し禁止は車両全般に適用されます。原動機付自転車も例外ではありません。",
     "category": "標識・標示"},
    {"q": "転回禁止の標識がある場所では、転回（Uターン）をしてはならない。", "answer": True,
     "explanation": "転回禁止の場所のほか、歩行者や他の車の通行を妨げるおそれがある場所でも転回は禁止されます。",
     "category": "標識・標示"},
    {"q": "歩行者用路側帯は歩行者のための部分だが、徐行すれば自動車も通行できる。", "answer": False,
     "explanation": "歩行者用路側帯（白線が2本のもの）は歩行者専用で、自動車は通行できません。",
     "category": "標識・標示"},
    {"q": "導流帯（ゼブラゾーン）の上は、絶対に通行してはならない。", "answer": False,
     "explanation": "導流帯は通行が禁止されているわけではありません。ただし、駐停車は避けるべき場所です。",
     "category": "標識・標示"},
    {"q": "停止線は、信号や一時停止の際に、車の前部がこの線を越えないよう止まるための標示である。", "answer": True,
     "explanation": "停止線がない場合は、横断歩道や交差点の手前が停止の目安になります。",
     "category": "標識・標示"},
    {"q": "中央線が黄色（オレンジ色）の実線で示されている場所では、追い越しのためにはみ出して通行できる。", "answer": False,
     "explanation": "黄色の実線の中央線は、追い越しのためのはみ出し禁止を示します。はみ出せるのは白色の破線の中央線です。",
     "category": "標識・標示"},
    {"q": "中央線が白色の破線（点線）で示されている場所では、対向車線にはみ出して追い越しができる。", "answer": True,
     "explanation": "白色の破線ははみ出し可能を示します。ただし、対向車や周囲の安全確認が前提です。",
     "category": "標識・標示"},
    {"q": "安全地帯は、路面電車の乗客や歩行者の安全のための場所で、自動車は通行できない。", "answer": True,
     "explanation": "安全地帯のそばを通るときは徐行しなければなりません。",
     "category": "標識・標示"},
    {"q": "「踏切あり」の標識は、この先に踏切があることを知らせる警戒標識である。", "answer": True,
     "explanation": "警戒標識は黄色地に黒い図柄が基本です。踏切の手前では一時停止の準備をします。",
     "category": "標識・標示"},
    {"q": "警戒標識は、青色の地に白い図柄で示される。", "answer": False,
     "explanation": "警戒標識は黄色の地に黒の図柄です。青地に白い図柄は指示標識などに使われます。",
     "category": "標識・標示"},
    {"q": "規制標識は、特定の交通方法を禁止したり、指定したりする標識である。", "answer": True,
     "explanation": "駐車禁止や最高速度、一方通行などが規制標識の例です。",
     "category": "標識・標示"},
    {"q": "「車両通行止め」の標識がある道路は、歩行者も通行できない。", "answer": False,
     "explanation": "車両通行止めは車両だけが対象で、歩行者は通行できます。歩行者の通行止めには別の標識があります。",
     "category": "標識・標示"},
    {"q": "一時停止の標識がある場所では、停止線の手前で一時停止し、左右の安全を確認しなければならない。", "answer": True,
     "explanation": "停止線がない場合は、交差点（横断歩道）の直前で一時停止します。",
     "category": "標識・標示"},
    {"q": "「駐車可」の標識がある場所では、何時間でも駐車してよい。", "answer": False,
     "explanation": "同じ場所に引き続き12時間以上（夜間は8時間以上）の駐車は禁止されています。",
     "category": "標識・標示"},
    {"q": "「左折可」の標示板がある交差点では、赤信号でも、他の交通に注意しながら左折できる。", "answer": True,
     "explanation": "左折可の標示板がある場合に限ります。歩行者や横向きの交通に十分注意が必要です。",
     "category": "標識・標示"},
    {"q": "「大型貨物自動車等通行止め」の標識は、すべての自動車の通行を禁止するものである。", "answer": False,
     "explanation": "この標識は大型貨物自動車など特定の車両だけを対象とする規制です。",
     "category": "標識・標示"},

    # ---- 運転の基本（25問） ----
    {"q": "後部座席の同乗者も、シートベルトを着用しなければならない。", "answer": True,
     "explanation": "シートベルトは全席で着用が義務づけられています。運転者は同乗者に着用させる必要があります。",
     "category": "運転の基本"},
    {"q": "シートベルトは、一般道路を低速で走るときは着けなくてもよい。", "answer": False,
     "explanation": "速度や道路の種類にかかわらず、シートベルトの着用は義務です。",
     "category": "運転の基本"},
    {"q": "前の車が急に止まっても追突しないよう、十分な車間距離を保たなければならない。", "answer": True,
     "explanation": "車間距離は速度や路面の状態に応じて保ちます。雨の日などは特に長めに取ります。",
     "category": "運転の基本"},
    {"q": "雨の日は、前が見えにくいので、晴れの日より車間距離を短くしたほうがよい。", "answer": False,
     "explanation": "雨の日は制動距離が長くなるため、車間距離はいつもより長く取る必要があります。",
     "category": "運転の基本"},
    {"q": "踏切の直前では、原則として一時停止し、左右の安全を確認しなければならない。", "answer": True,
     "explanation": "遮断機や警報機がない踏切でも一時停止が必要です。列車の見落としに注意します。",
     "category": "運転の基本"},
    {"q": "踏切の先が渋滞していても、踏切の手前まで来たら、そのまま踏切内に進んで止まってよい。", "answer": False,
     "explanation": "踏切内で止まるおそれがあるときは、踏切に入ってはいけません。先の状況を確認してから進みます。",
     "category": "運転の基本"},
    {"q": "交差点や横断歩道とその付近では、歩行者や自転車がいないことが明らかな場合を除き、止まれる速度で進まなければならない。", "answer": True,
     "explanation": "歩行者保護のための減速の義務です。「いないことが明らか」でなければ減速します。",
     "category": "運転の基本"},
    {"q": "横断歩道の近くに歩行者が見当たらなければ、減速せずにそのまま進んでよい。", "answer": False,
     "explanation": "歩行者がいないことが明らかでない限り、横断歩道の手前では止まれる速度に減速しなければなりません。",
     "category": "運転の基本"},
    {"q": "左右の見通しのきかない交差点では、徐行しなければならない。", "answer": True,
     "explanation": "徐行場所の代表例です。道路の曲がり角付近や、坂の頂上付近も徐行場所です。",
     "category": "運転の基本"},
    {"q": "坂の頂上付近と、こう配の急な下り坂では、徐行しなければならない。", "answer": True,
     "explanation": "下り坂では速度が出やすく、頂上付近は見通しが悪いため徐行が必要です。",
     "category": "運転の基本"},
    {"q": "横断歩道とその前後5メートル以内の場所では、駐車は禁止だが停車はできる。", "answer": False,
     "explanation": "横断歩道とその前後5メートル以内は、駐車も停車も禁止です。",
     "category": "運転の基本"},
    {"q": "交差点とその側端から5メートル以内の場所は、駐車も停車も禁止されている。", "answer": True,
     "explanation": "交差点付近の駐停車は、見通しを悪くし事故のもとになります。",
     "category": "運転の基本"},
    {"q": "踏切とその前後10メートル以内の場所は、駐車も停車も禁止されている。", "answer": True,
     "explanation": "踏切のほか、トンネルや坂の頂上付近なども駐停車禁止場所です。",
     "category": "運転の基本"},
    {"q": "バス停の標示柱から10メートル以内の場所は、路線バス等の運行時間中は駐車も停車も禁止されている。", "answer": True,
     "explanation": "バスの停車の妨げになるためです。運行していない時間帯は規制の対象外です。",
     "category": "運転の基本"},
    {"q": "夜間、対向車とすれ違うときは、前照灯を下向きに切り替えなければならない。", "answer": True,
     "explanation": "走行用前照灯（上向き）のままだと対向車の運転者をまぶしくさせます。すれ違い用前照灯（下向き）に切り替えます。",
     "category": "運転の基本"},
    {"q": "夜間でも、街灯が明るい道路では、前照灯をつけなくてよい。", "answer": False,
     "explanation": "夜間は街灯の有無にかかわらず前照灯をつけなければなりません。",
     "category": "運転の基本"},
    {"q": "車両通行帯のないトンネル内では、追い越しをしてはならない。", "answer": True,
     "explanation": "トンネル（車両通行帯がある場合を除く）は追い越し禁止場所の一つです。",
     "category": "運転の基本"},
    {"q": "交差点では、左折や右折をしようとしている車を追い越してもよい。", "answer": False,
     "explanation": "交差点とその手前30メートル以内の場所では、追い越しが禁止されています。",
     "category": "運転の基本"},
    {"q": "前の車が右折しようとして道路の中央に寄っているときは、その左側を通って進むことができる。", "answer": True,
     "explanation": "右折車の左側を通る場合は、右折車の動きと対向車に十分注意します。",
     "category": "運転の基本"},
    {"q": "原動機付自転車の二段階右折は、交通量の多い交差点でのみ必要である。", "answer": False,
     "explanation": "二段階右折が必要かどうかは、片側3車線以上の道路かどうかで決まります。交通量の多さでは決まりません。",
     "category": "運転の基本"},
    {"q": "高速道路の路肩には、故障などの緊急の場合を除いて、停車してはならない。", "answer": True,
     "explanation": "路肩は走行車線ではありません。緊急時以外は停車や本線車道への出入りに使えません。",
     "category": "運転の基本"},
    {"q": "後退（バック）するときは、徐行さえすれば、後ろの安全を確認しなくてよい。", "answer": False,
     "explanation": "後退するときは、後方の安全を直接目で確認しなければなりません。死角に特に注意します。",
     "category": "運転の基本"},
    {"q": "運転中に携帯電話を手に持って通話したり、画面を注視したりしてはならない。", "answer": True,
     "explanation": "ハンズフリー装置を使う場合や停車中の操作は対象外ですが、走行中の保持・注視は禁止です。",
     "category": "運転の基本"},
    {"q": "6歳未満の幼児を自動車に乗せるときは、チャイルドシートを使用させなければならない。", "answer": True,
     "explanation": "幼児の体格に合ったチャイルドシートを使います。助手席より後部座席が安全です。",
     "category": "運転の基本"},
    {"q": "雨でぬれた路面でも、タイヤの溝が十分にあれば、晴れの日と同じ距離で止まれる。", "answer": False,
     "explanation": "ぬれた路面では制動距離が長くなります。速度を落とし、車間距離を長く取ることが大切です。",
     "category": "運転の基本"},

    # ---- 歩行者と安全（25問） ----
    {"q": "信号のない横断歩道で、横断しようとする歩行者がいるときは、その手前で一時停止して歩行者を通さなければならない。", "answer": True,
     "explanation": "横断歩道では歩行者が絶対に優先です。歩行者の横断を妨げてはいけません。",
     "category": "歩行者と安全"},
    {"q": "横断歩道を渡っている歩行者の少し後ろを通るなら、止まらずに進んでもよい。", "answer": False,
     "explanation": "歩行者が横断しているときは、一時停止して横断が終わるまで待たなければなりません。",
     "category": "歩行者と安全"},
    {"q": "横断歩道のない交差点やその近くで歩行者が横断しているときも、歩行者の通行を妨げてはならない。", "answer": True,
     "explanation": "横断歩道がない場所でも、横断中の歩行者は保護しなければなりません。",
     "category": "歩行者と安全"},
    {"q": "横断歩道を渡っている歩行者がいても、歩行者が車から離れたら、渡り終わる前に発進してよい。", "answer": False,
     "explanation": "歩行者の横断が完全に終わるまで発進してはいけません。",
     "category": "歩行者と安全"},
    {"q": "身体の不自由な人や高齢者が道路を横断しているときは、一時停止や徐行をして、安全に横断できるようにしなければならない。", "answer": True,
     "explanation": "歩行に困難のある人を保護する義務です。急かしたり警音器で威嚇したりしてはいけません。",
     "category": "歩行者と安全"},
    {"q": "白い杖を持った人が横断しようとしているときは、警音器（クラクション）を鳴らして知らせれば、そのまま進んでよい。", "answer": False,
     "explanation": "白い杖を持った人は視覚に障害のある人です。一時停止して安全に横断できるようにしなければなりません。",
     "category": "歩行者と安全"},
    {"q": "子どもや高齢者が通行している近くでは、徐行するか一時停止して、安全を確認しなければならない。", "answer": True,
     "explanation": "子どもは急に飛び出すことがあります。十分な間隔が取れないときは徐行・一時停止します。",
     "category": "歩行者と安全"},
    {"q": "スクールゾーンでは、決められた時間帯に歩行者用道路となり、許可のない車は通行できないことがある。", "answer": True,
     "explanation": "登下校の時間帯に規制されることが多い場所です。標識と補助標識の時間帯を確認します。",
     "category": "歩行者と安全"},
    {"q": "歩道と車道の区別がある道路では、自動車は歩道を通行することはできない。", "answer": True,
     "explanation": "歩道は歩行者のための部分です。横切るときは直前で一時停止します。",
     "category": "歩行者と安全"},
    {"q": "自転車は、歩道では歩行者より優先して通行できる。", "answer": False,
     "explanation": "歩道では歩行者が優先です。自転車は車道寄りを徐行し、歩行者の通行を妨げるおそれがあるときは一時停止します。",
     "category": "歩行者と安全"},
    {"q": "自転車は、原則として車道の左側を通行する。", "answer": True,
     "explanation": "自転車は軽車両です。歩道を通れるのは、標識がある場合や13歳未満・70歳以上などの決められた場合です。",
     "category": "歩行者と安全"},
    {"q": "歩行者は、歩道のない道路では、道路の左側を通らなければならない。", "answer": False,
     "explanation": "歩行者は右側通行が原則です。車と対面して歩くことで、危険に気づきやすくするためです。",
     "category": "歩行者と安全"},
    {"q": "自動車が歩道や路側帯を横切るときは、その直前で一時停止し、歩行者の通行を妨げてはならない。", "answer": True,
     "explanation": "駐車場への出入りなどで歩道を横切るときのルールです。",
     "category": "歩行者と安全"},
    {"q": "横断中の歩行者がいても、信号が青に変われば、すぐに発進してよい。", "answer": False,
     "explanation": "青信号でも、横断中の歩行者がいれば発進してはいけません。安全が確認できてから発進します。",
     "category": "歩行者と安全"},
    {"q": "安全地帯のそばを通るときは、徐行しなければならない。", "answer": True,
     "explanation": "安全地帯には路面電車の乗客などがいます。そのそばでは徐行が義務です。",
     "category": "歩行者と安全"},
    {"q": "路面電車が停留所に止まって乗客が乗り降りしているときは、後方から速度を落とさずに追い越してよい。", "answer": False,
     "explanation": "路面電車の乗降があるときは徐行し、乗客の安全を確認します。安全地帯がない停留所では特に注意が必要です。",
     "category": "歩行者と安全"},
    {"q": "通学路であることを示す標識がなければ、通学路でも一般の道路と同じ注意でよい。", "answer": False,
     "explanation": "通学路では子どもの飛び出しが想定されます。標識の有無にかかわらず十分な注意が必要です。",
     "category": "歩行者と安全"},
    {"q": "歩行者は、道路を斜めに横断してはならない。", "answer": True,
     "explanation": "歩行者の横断のルールです。横断はできるだけ直角に、短い距離で渡ります。",
     "category": "歩行者と安全"},
    {"q": "近くに横断歩道があっても、急いでいるときは歩行者は横断歩道を使わずに横断してよい。", "answer": False,
     "explanation": "歩行者は、近くに横断歩道がある場所では、横断歩道を横断しなければなりません。",
     "category": "歩行者と安全"},
    {"q": "幼児や子どもが一人で歩いているのを見かけたら、飛び出しに備えて速度を落として注意する。", "answer": True,
     "explanation": "子どもは車の接近に気づかないことがあります。早めの減速が事故防止につながります。",
     "category": "歩行者と安全"},
    {"q": "ベビーカーを押している人は歩行者ではないので、横断歩道での優先の対象にはならない。", "answer": False,
     "explanation": "ベビーカーを押している人は歩行者として扱われ、横断歩道では優先されます。",
     "category": "歩行者と安全"},
    {"q": "盲導犬を連れた人が横断しているときは、一時停止して安全に横断できるようにする。", "answer": True,
     "explanation": "盲導犬を連れた人は視覚に障害のある人です。静かに見守り、安全に渡れるようにします。",
     "category": "歩行者と安全"},
    {"q": "歩道を通行する自転車は、歩行者の通行を妨げそうなときでも、ベルを鳴らせば速度を落とさなくてよい。", "answer": False,
     "explanation": "歩道では歩行者が優先です。自転車は徐行し、妨げるおそれがあるときは一時停止しなければなりません。",
     "category": "歩行者と安全"},
    {"q": "電動車椅子などで通行している人は、歩行者として扱われる。", "answer": True,
     "explanation": "身体障害者用車椅子（電動を含む）で通行する人は、歩行者と同じ扱いです。",
     "category": "歩行者と安全"},
    {"q": "夜間は、反射材をつけていない歩行者には、運転者は注意しなくてよい。", "answer": False,
     "explanation": "夜間は歩行者が見えにくくなります。反射材の有無にかかわらず、運転者は歩行者に十分注意しなければなりません。",
     "category": "歩行者と安全"},
]

CATEGORIES = ["交通ルールの基礎", "標識・標示", "運転の基本", "歩行者と安全"]

# ============================================================
# Unit 2: Web ルート（ページ配信 / API / ヘルスチェック）
# ============================================================


@app.route("/")
def index():
    page = HTML_PAGE.replace(
        "__QUESTIONS_JSON__",
        json.dumps(QUESTIONS, ensure_ascii=False))
    return Response(page, mimetype="text/html")


@app.route("/api/questions")
def api_questions():
    return jsonify(QUESTIONS)


@app.route("/healthz")
def healthz():
    return jsonify(status="ok")


# ============================================================
# Unit 3: 画面（HTML / CSS / JavaScript）
# ============================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>仮免対策 ○×カード</title>
<style>
  :root {
    --bg: #f4f6f8; --card: #ffffff; --text: #1c2430; --muted: #5b6b7d;
    --border: #d5dde5; --accent: #2563eb; --ok: #15803d; --ng: #dc2626;
    --okbg: #e7f6ec; --ngbg: #fdeaea;
  }
  html[data-theme="dark"] {
    --bg: #12161c; --card: #1d242e; --text: #e8edf3; --muted: #9fb0c3;
    --border: #33404f; --accent: #6ea8fe; --ok: #4ade80; --ng: #f87171;
    --okbg: #17351f; --ngbg: #3d1d1d;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; overflow-x: hidden; }
  body {
    background: var(--bg); color: var(--text);
    font-family: -apple-system, "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
    line-height: 1.6;
  }
  .wrap { max-width: 640px; margin: 0 auto; padding: 16px 12px 40px; }
  header { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
  h1 { font-size: 1.4rem; margin: 8px 0; }
  .theme-btn {
    background: var(--card); color: var(--text); border: 1px solid var(--border);
    border-radius: 8px; padding: 6px 12px; font-size: .9rem; cursor: pointer;
  }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 14px;
    padding: 20px 16px; margin-top: 14px;
  }
  .disclaimer { color: var(--muted); font-size: .85rem; margin-top: 6px; }
  .mode-btn {
    display: block; width: 100%; margin: 10px 0; padding: 14px;
    font-size: 1.05rem; border-radius: 10px; cursor: pointer;
    background: var(--card); color: var(--text); border: 2px solid var(--accent);
  }
  .mode-btn:active { opacity: .7; }
  .cat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .cat-grid .mode-btn { margin: 0; font-size: .95rem; }
  .meta { display: flex; justify-content: space-between; color: var(--muted); font-size: .9rem; }
  .bar { height: 8px; background: var(--border); border-radius: 4px; margin: 10px 0 4px; }
  .bar > div { height: 100%; background: var(--accent); border-radius: 4px; width: 0%; }
  .q-cat { color: var(--accent); font-size: .85rem; font-weight: bold; }
  .q-text { font-size: 1.15rem; font-weight: bold; margin: 10px 0 18px; word-break: break-all; }
  .ox { display: flex; gap: 12px; }
  .ox button {
    flex: 1; font-size: 2.6rem; padding: 18px 0; border-radius: 12px; cursor: pointer;
    background: var(--card); color: var(--text); border: 2px solid var(--border);
  }
  .ox button:disabled { opacity: .55; cursor: default; }
  .ox button.picked-ok { border-color: var(--ok); background: var(--okbg); }
  .ox button.picked-ng { border-color: var(--ng); background: var(--ngbg); }
  .feedback { margin-top: 16px; padding: 14px; border-radius: 10px; display: none; }
  .feedback.show { display: block; }
  .feedback.ok { background: var(--okbg); }
  .feedback.ng { background: var(--ngbg); }
  .feedback .verdict { font-size: 1.2rem; font-weight: bold; }
  .feedback.ok .verdict { color: var(--ok); }
  .feedback.ng .verdict { color: var(--ng); }
  .next-btn {
    display: block; width: 100%; margin-top: 14px; padding: 13px; font-size: 1.05rem;
    border-radius: 10px; cursor: pointer; border: none;
    background: var(--accent); color: #fff;
  }
  .score-big { font-size: 2rem; font-weight: bold; text-align: center; margin: 6px 0; }
  .passline { text-align: center; font-weight: bold; }
  .passline.ok { color: var(--ok); }
  .passline.ng { color: var(--ng); }
  .missed-item { border-top: 1px solid var(--border); padding: 10px 0; }
  .missed-item .ans { font-weight: bold; }
  .hidden { display: none; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>仮免対策 ○×カード</h1>
    <button class="theme-btn" id="themeBtn" type="button">🌙 ダーク</button>
  </header>

  <!-- トップ画面 -->
  <section id="home">
    <div class="card">
      <p>仮免許の学科試験対策として、交通ルールの基本を○×形式で練習できます。全100問・4カテゴリ。</p>
      <p class="disclaimer">学習用の自作問題です。公式の試験問題ではありません。</p>
      <button class="mode-btn" type="button" id="btnRandom">ランダム10問</button>
      <button class="mode-btn" type="button" id="btnAll">全問100問</button>
      <button class="mode-btn hidden" type="button" id="btnReviewHome">間違えた問題だけ復習</button>
      <p style="margin:16px 0 6px; font-weight:bold;">カテゴリ別（各25問）</p>
      <div class="cat-grid" id="catGrid"></div>
    </div>
  </section>

  <!-- クイズ画面 -->
  <section id="quiz" class="hidden">
    <div class="card">
      <div class="meta"><span id="progress">第 1 問 / 全 10 問</span><span id="scoreNow">正解 0</span></div>
      <div class="bar"><div id="barFill"></div></div>
      <div class="q-cat" id="qCat"></div>
      <div class="q-text" id="qText"></div>
      <div class="ox">
        <button type="button" id="btnMaru">○</button>
        <button type="button" id="btnBatsu">×</button>
      </div>
      <div class="feedback" id="feedback">
        <div class="verdict" id="verdict"></div>
        <div id="expText"></div>
        <button class="next-btn" type="button" id="btnNext">次の問題</button>
      </div>
    </div>
  </section>

  <!-- 結果画面 -->
  <section id="result" class="hidden">
    <div class="card">
      <div class="score-big" id="scoreBig"></div>
      <p class="passline" id="passLine"></p>
      <button class="mode-btn hidden" type="button" id="btnReview">間違えた問題だけ復習</button>
      <button class="mode-btn" type="button" id="btnHome">トップへ戻る</button>
      <div id="missedList"></div>
    </div>
  </section>
</div>

<script>
const QUESTIONS = __QUESTIONS_JSON__;
const CATEGORIES = ["交通ルールの基礎", "標識・標示", "運転の基本", "歩行者と安全"];
const MISSED_KEY = "karimen_missed";
const THEME_KEY = "karimen_theme";

// テーマ（ライト/ダーク）
const rootEl = document.documentElement;
function applyTheme(t) {
  rootEl.setAttribute("data-theme", t);
  document.getElementById("themeBtn").textContent = (t === "dark") ? "☀️ ライト" : "🌙 ダーク";
}
applyTheme(localStorage.getItem(THEME_KEY) || "light");
document.getElementById("themeBtn").addEventListener("click", function () {
  const next = rootEl.getAttribute("data-theme") === "dark" ? "light" : "dark";
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
});

// 画面切り替え
function show(id) {
  ["home", "quiz", "result"].forEach(function (s) {
    document.getElementById(s).classList.toggle("hidden", s !== id);
  });
}

function shuffled(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = a[i]; a[i] = a[j]; a[j] = tmp;
  }
  return a;
}

function getMissedStored() {
  try { return JSON.parse(localStorage.getItem(MISSED_KEY) || "[]"); }
  catch (e) { return []; }
}
function refreshReviewHome() {
  document.getElementById("btnReviewHome").classList.toggle(
    "hidden", getMissedStored().length === 0);
}

// クイズ状態
let quizList = [], quizIdx = 0, quizScore = 0, quizMissed = [], answered = false;

function startQuiz(list) {
  quizList = list; quizIdx = 0; quizScore = 0; quizMissed = [];
  show("quiz");
  renderQuestion();
}

function renderQuestion() {
  answered = false;
  const q = quizList[quizIdx];
  document.getElementById("progress").textContent =
    "第 " + (quizIdx + 1) + " 問 / 全 " + quizList.length + " 問";
  document.getElementById("scoreNow").textContent = "正解 " + quizScore;
  document.getElementById("barFill").style.width =
    ((quizIdx) / quizList.length * 100) + "%";
  document.getElementById("qCat").textContent = q.category;
  document.getElementById("qText").textContent = q.q;
  const fb = document.getElementById("feedback");
  fb.className = "feedback";
  const maru = document.getElementById("btnMaru");
  const batsu = document.getElementById("btnBatsu");
  [maru, batsu].forEach(function (b) {
    b.disabled = false; b.classList.remove("picked-ok", "picked-ng");
  });
}

function answer(userAnswer) {
  if (answered) return;
  answered = true;
  const q = quizList[quizIdx];
  const correct = (userAnswer === q.answer);
  const maru = document.getElementById("btnMaru");
  const batsu = document.getElementById("btnBatsu");
  maru.disabled = true; batsu.disabled = true;
  const picked = userAnswer ? maru : batsu;
  picked.classList.add(correct ? "picked-ok" : "picked-ng");
  if (correct) { quizScore++; } else { quizMissed.push(q); }
  document.getElementById("scoreNow").textContent = "正解 " + quizScore;
  const fb = document.getElementById("feedback");
  fb.className = "feedback show " + (correct ? "ok" : "ng");
  document.getElementById("verdict").textContent = correct
    ? "正解！"
    : "不正解…（正解は " + (q.answer ? "○" : "×") + "）";
  document.getElementById("expText").textContent = q.explanation;
  document.getElementById("btnNext").textContent =
    (quizIdx + 1 >= quizList.length) ? "結果を見る" : "次の問題";
}

function finishQuiz() {
  const total = quizList.length;
  const pct = Math.round(quizScore / total * 100);
  document.getElementById("scoreBig").textContent =
    quizScore + " / " + total + " 問正解（" + pct + "%）";
  const pl = document.getElementById("passLine");
  if (pct >= 90) {
    pl.className = "passline ok";
    pl.textContent = "合格ライン目安（90%）に届いています。この調子でいきましょう。";
  } else {
    pl.className = "passline ng";
    pl.textContent = "合格ライン目安は90%です。間違えた問題を復習しましょう。";
  }
  // 間違えた問題を localStorage に保存
  localStorage.setItem(MISSED_KEY, JSON.stringify(quizMissed.map(function (q) { return q.q; })));
  document.getElementById("btnReview").classList.toggle("hidden", quizMissed.length === 0);
  const list = document.getElementById("missedList");
  if (quizMissed.length === 0) {
    list.innerHTML = "<p>間違えた問題はありませんでした。</p>";
  } else {
    list.innerHTML = "<h3>間違えた問題（" + quizMissed.length + "問）</h3>" +
      quizMissed.map(function (q) {
        return '<div class="missed-item"><div>' + escapeHtml(q.q) + "</div>" +
          '<div class="ans">正解： ' + (q.answer ? "○" : "×") + "</div>" +
          "<div>" + escapeHtml(q.explanation) + "</div></div>";
      }).join("");
  }
  refreshReviewHome();
  show("result");
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function questionsByTexts(texts) {
  return QUESTIONS.filter(function (q) { return texts.indexOf(q.q) >= 0; });
}

// イベント
document.getElementById("btnMaru").addEventListener("click", function () { answer(true); });
document.getElementById("btnBatsu").addEventListener("click", function () { answer(false); });
document.getElementById("btnNext").addEventListener("click", function () {
  quizIdx++;
  if (quizIdx >= quizList.length) { finishQuiz(); } else { renderQuestion(); }
});
document.getElementById("btnRandom").addEventListener("click", function () {
  startQuiz(shuffled(QUESTIONS).slice(0, 10));
});
document.getElementById("btnAll").addEventListener("click", function () {
  startQuiz(shuffled(QUESTIONS));
});
document.getElementById("btnReview").addEventListener("click", function () {
  startQuiz(shuffled(quizMissed));
});
document.getElementById("btnReviewHome").addEventListener("click", function () {
  startQuiz(shuffled(questionsByTexts(getMissedStored())));
});
document.getElementById("btnHome").addEventListener("click", function () { show("home"); });

const catGrid = document.getElementById("catGrid");
CATEGORIES.forEach(function (cat) {
  const b = document.createElement("button");
  b.type = "button"; b.className = "mode-btn"; b.textContent = cat;
  b.addEventListener("click", function () {
    startQuiz(shuffled(QUESTIONS.filter(function (q) { return q.category === cat; })));
  });
  catGrid.appendChild(b);
});

refreshReviewHome();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
