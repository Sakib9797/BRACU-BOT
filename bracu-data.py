import requests

url = "https://www.daraz.com.bd/groceries-dairy-chilled-milk-butter-eggs-margarine-spread/?up_id=207636186&clickTrackInfo=matchType--20___description--6K%252B%2B%25E0%25A6%2585%25E0%25A6%25A8%25E0%25A7%2581%25E0%25A6%25B8%25E0%25A6%25A8%25E0%25A7%258D%25E0%25A6%25A7%25E0%25A6%25BE%25E0%25A6%25A8___seedItemMatchType--c2i___bucket--0___spm_id--category.hp___seedItemScore--0.0___abId--379344___score--0.1___pvid--ffad0646-d741-4fc3-a974-228577a05543___refer--___appId--7253___seedItemId--207636186___scm--1007.17253.379344.0___categoryId--10002505___timestamp--1748457387192&from=hp_categories&item_id=207636186&version=v2&q=%E0%A6%AE%E0%A6%BE%E0%A6%B0%E0%A7%8D%E0%A6%9C%E0%A6%BE%E0%A6%B0%E0%A6%BF%E0%A6%A8%2B%E0%A6%93%2B%E0%A6%9B%E0%A6%A1%E0%A6%BC%E0%A6%BF%E0%A6%AF%E0%A6%BC%E0%A7%87&params=%7B%22catIdLv1%22%3A%223752%22%2C%22pvid%22%3A%22ffad0646-d741-4fc3-a974-228577a05543%22%2C%22src%22%3A%22ald%22%2C%22categoryName%22%3A%22%25E0%25A6%25AE%25E0%25A6%25BE%25E0%25A6%25B0%25E0%25A7%258D%25E0%25A6%259C%25E0%25A6%25BE%25E0%25A6%25B0%25E0%25A6%25BF%25E0%25A6%25A8%2B%25E0%25A6%2593%2B%25E0%25A6%259B%25E0%25A6%25A1%25E0%25A6%25BC%25E0%25A6%25BF%25E0%25A6%25AF%25E0%25A6%25BC%25E0%25A7%2587%22%2C%22categoryId%22%3A%2210002505%22%7D&src=hp_categories&spm=a2a0e.tm80335411.categoriesPC.d_9_10002505"

r = requests.get(url)

# ...existing code...
with open("file1.html", "w", encoding="utf-8") as f:
    f.write(r.text)
# ...existing code...