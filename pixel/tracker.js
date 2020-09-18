var fastrack_start = new Date();
var fastrack_time_count = 0

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

function fastrack_time_off() {{
    fastrack_time_count = fastrack_time_count + (new Date() - fastrack_start) / 1000;
    fastrack_start = null
}}

function fastrack_time_on() {{
    fastrack_start = new Date()

}}

document.addEventListener("visibilitychange", function() {{
  if (document.hidden){{
      fastrack_time_off()
  }} else {{
      fastrack_time_on()
  }}
}});

function fastrack_trackview(e) {{
    try {{
        var time_spent = 0
        if (fastrack_start) {{
            time_spent = fastrack_time_count + (new Date() - fastrack_start) / 1000;
        }} else {{
            time_spent = fastrack_time_count
        }}

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
