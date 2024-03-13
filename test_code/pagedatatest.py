from requests_html import HTMLSession

session = HTMLSession()

url = "https://www.tiktok.com/@dr.kojosarfo/video/7321974504731790634"

response = session.get(url)

response.html.render(sleep=1, keep_page=True, scrolldown=1)

username = response.html.find("span.css-1c7urt-SpanUniqueId")

with open("tiktok_html.txt", "w") as file:
    file.write(response.html.html)

print(username)