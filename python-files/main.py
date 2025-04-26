import webbrowser

html_code = """
<script>
window.$ecu = {lang:"eng",width:"800",BackgroundColor:"#395694",BoxColor:"#323a4e",FontColor:"#ffffff",ButtonColor:"#1f99f7",ButtonFontColor:"#ffffff",APIID:"1074"};
(function() {
    d = document;
    s = d.createElement("script");
    s.src = "https://xremover.net/calculator/ecuob.js?_="+new Date();
    s.async = 1;
    d.body.parentNode.insertBefore(s, document.body.nextSibling);
})();
</script><div id="ecuCalculateTool"></div>
"""

# Erstelle eine temporäre HTML-Datei
with open("temp.html", "w") as f:
    f.write(html_code)

# Öffne die temporäre HTML-Datei im Standard-Webbrowser
webbrowser.open("temp.html")