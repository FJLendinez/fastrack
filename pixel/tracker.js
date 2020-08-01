var fastrack_start = new Date();

function httpGetAsync(theUrl) {{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, true);
    xmlHttp.send(null);
}}

function fastrack_identify(email) {{
    var e = encodeURIComponent;
    var h = localStorage.getItem('h');
    if (!h) {{
        return false
    }};
    httpGetAsync('{domain}/identify?email=' + e(email) + '&h=' + h);
}}

function fastrack_trackview(e) {{
    try {{
        var time_spent = (new Date() - fastrack_start) / 1000;

        var h = localStorage.getItem('h');
        if (!h) {{
            localStorage.setItem('h', '{history_uuid}')
        }};
        h = localStorage.getItem('h');

        var s = sessionStorage.getItem('s');
        if (!s) {{
            sessionStorage.setItem('s', '{session_uuid}')
        }};
        s = sessionStorage.getItem('s');
        var d = document, e = encodeURIComponent;
        httpGetAsync('{domain}/a.gif?url=' + e(d.location.href) + '&ref=' + e(d.referrer) + '&t=' + e(d.title) + '&s=' + e(s) + '&h=' + e(h) + '&ts=' + (time_spent));
        fastrack_start = new Date();

    }} catch (error) {{
        localStorage.setItem('error', error.message)
    }}
}};
var pushState = history.pushState;
history.pushState = function () {{
    pushState.apply(history, arguments);
    fireEvents('pushState', arguments);  // Some event-handling function
}};
window.addEventListener('beforeunload', fastrack_trackview);
