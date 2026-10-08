from flask import Flask

from sections import bfla, bola, unsafe_consumption

INDEX_HTML = """<!doctype html>
<title>api-custom-lab (REST track)</title>
<style>body{font-family:sans-serif;max-width:720px;margin:40px auto;line-height:1.5}
code{background:#eee;padding:2px 5px;border-radius:3px}</style>
<h1>api-custom-lab (REST track)</h1>
<p>Custom labs for REST issues kept in-house so BOLA/BFLA have a fully self-verified instance
alongside the public-lab coverage, plus OWASP API10 (unsafe consumption) which no public lab
covered well. See the training repo's <code>COVERAGE-MATRIX.md</code> for why each exists. No
solutions here - see each phase's <code>workshop.md</code>.</p>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>Path</th><th>Covers</th></tr>
<tr><td><code>/api/bola/1</code></td>
    <td>OWASP API1:2023 - a valid token from any user reaches any other user's resource</td></tr>
<tr><td><code>/api/bfla/1</code></td>
    <td>OWASP API5:2023 - a valid token is checked, but not its owner's role</td></tr>
<tr><td><code>/api/unsafe-consumption/1</code></td>
    <td>OWASP API10:2023 - unsafe consumption of a trusted upstream API's response</td></tr>
</table>
"""


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bola.bp)
    app.register_blueprint(bfla.bp)
    app.register_blueprint(unsafe_consumption.bp)

    @app.get("/")
    def index():
        return INDEX_HTML

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
