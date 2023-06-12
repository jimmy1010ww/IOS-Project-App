import requests
from bs4 import BeautifulSoup

class NTUSTBulletinBot:
    bulletin_board_url = "https://www.ntust.edu.tw/p/403-1000-168-1.php?Lang=zh-tw"

    def get_bulletin_board_page(self, page):
        url = self.bulletin_board_url.replace("403-1000-168-1", f"403-1000-168-{page}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="listTB")
        if table:
            rows = table.find_all("tr")[1:]  # Exclude the table header row

            bulletin_list = []

            for row in rows:
                date = row.find("td", attrs={"data-th": "日期"}).text.strip()
                title = row.find("td", attrs={"data-th": "標題"}).text.strip()
                url = row.find("a")["href"]

                bulletin_dict = {
                    "date": date,
                    "title": title,
                    "url": url
                }

                bulletin_list.append(bulletin_dict)
            return bulletin_list
        else:
            print("Table not found on the webpage.")
            return []

    
# 使用範例
# bot = NTUSTBulletinBot()
# bulletin_list = bot.get_bulletin_board_page(1)  # 爬取第1頁的資訊

# 檢查爬取的資訊列表
# for item in bulletin_list:
#     print("日期:", item["date"])
#     print("標題:", item["title"])
#     print("URL:", item["url"])
#     print("-----------------------")
