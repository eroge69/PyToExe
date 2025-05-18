from flask import Flask, render_template, request
from duckduckgo_search import DDGS

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query']
        if query.strip():
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
