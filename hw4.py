from flask import Flask, request
import requests as rq
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.route("/")
def index():
    return "<a href=\"/news_api?q=新垣結衣,結婚&n=3&w=50\">api在這裡</a>"


@app.route("/news_api")
def news_api():
    q = request.args.get('q')
    n = request.args.get('n')
    w = request.args.get('w')

    data = {
        "query": {
            "q": q,
            "n": n,
            "w": w
        },
        "content": {},
        "error": []
    }

    res = rq.get("https://tw.news.yahoo.com/search?p={}&fr=news".format(q))
    soup = bs(res.text, features="lxml")
    container = soup.find(id="stream-container-scroll-template")
    maga_item = container.find_all("li", {"class": "StreamMegaItem"})

    if not n.isdigit():
        data["error"].append("n不是正整數")
        return data
    if not w.isdigit():
        data["error"].append("w不是正整數")
        return data

    n = int(n)
    w = int(w)

    if n > len(maga_item):
        data["error"].append("找到的文章數只有{}篇,比目標{}偏少".format(len(maga_item), n))

    i = 0
    for item in maga_item:
        url = "https://tw.news.yahoo.com/"+item.find("a")["href"]
        text = rq.get(url).text
        soup = bs(text, "lxml")

        # 文章主體的block放在class為"caas-body"的區域
        contentBody = soup.find(class_="caas-body")
        if contentBody:
            i += 1
            if i > n:
                break
            # 將content分成多句存成陣列
            content = []
            for p in contentBody.find_all("p"):
                if p.text != "":
                    content.append(p.text)

            content = "".join(content)[:w]
            data["content"][str(i)] = content

    return data


app.run(debug=True)
