var fastrack_start = new Date();

function httpGetAsync(theUrl) {{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, true);
    xmlHttp.send(null);
}}

function fastrack_identify(email) {{
    var e = encodeURIComponent;
    var h = localStorage.getItem('h');
    var i = localStorage.getItem('i');
    if (!h) {{
        return false
    }};
    if (i && h === i){{
        return false
    }}
    httpGetAsync('{domain}/identify?email=' + e(email) + '&h=' + h);
    localStorage.setItem('i', h)
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
        if (window.fastrack_metadata) {{
            var meta = JSON.stringify(window.fastrack_metadata)
        }}
        window.fastrack_metadata = null
        var d = document, e = encodeURIComponent;
        httpGetAsync('{domain}/a.gif?url=' + e(d.location.href) + '&ref=' + e(d.referrer) + '&t=' + e(d.title) + '&s=' + e(s) + '&h=' + e(h) + '&ts=' + (time_spent) + '&meta=' + e(meta));
        fastrack_start = new Date();

    }} catch (error) {{
        localStorage.setItem('error', error.message)
    }}
}};

window.addEventListener('beforeunload', fastrack_trackview);
