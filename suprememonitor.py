import requests
from bs4 import BeautifulSoup
from time import sleep
from discord_hooks import Webhook
from user_agent import generate_user_agent
import threading
from random import choice
from multiprocessing.pool import ThreadPool
import urllib3


headers = {'authority': 'www.supremenewyork.com', 'cache-control': 'max-age=0', 'upgrade-insecure-requests': '1', 'user-agent': generate_user_agent(), 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_proxies():
    proxys = open('<PROXY PATH>', 'r', encoding='utf-8').read().splitlines()
    proxy = choice(proxys)
    proxies = {'http': str(proxy), 'https': str(proxy)}
    return proxies


def webhook(link, currency, photo, title, description, ino):
    link = 'https://www.supremenewyork.com' + link.rstrip()
    url = "<WEBHOOK>"
    embed = Webhook(url, color=123123)
    embed.set_desc("RESTOCK: [{0}]({1})".format(title, link))
    embed.add_field(name="Description", value=description)
    embed.add_field(name="Ino", value=ino)
    embed.add_field(name="Currency", value=currency)
    embed.add_field(name="Link", value=link)
    embed.set_thumbnail(photo)
    embed.set_footer(text='Powered by <COMPANY NAME>', ts=True, icon='<FOOTER ICON>')
    embed.post()

def supreme():
    session = requests.session()
    try:
        soup = BeautifulSoup(session.get('https://www.supremenewyork.com/shop/all', headers=headers, proxies=get_proxies, timeout=10,verify=False).text, 'lxml')
        work = True
    except:
        try:
            soup = BeautifulSoup(session.get('https://www.supremenewyork.com/shop/all', headers=headers, proxies=get_proxies(),timeout=10, verify=False).text, 'lxml')
            work = True
        except:
            try:
                soup = BeautifulSoup(session.get('https://www.supremenewyork.com/shop/all', headers=headers, proxies=get_proxies(),timeout=10, verify=False).text, 'lxml')
                work = True
            except:
                soup = None
                work = False
    info = []
    info.append(work)
    info.append(soup)
    return info


def main():
    lastitems = []
    soldout = []
    lastitems.clear()
    soldout.clear()

    info = supreme()

    if info[0]:
        try:
            a = 0
            soup = info[1]
            for inner in soup.find_all('div', class_='inner-article')[1:]:
                lastitems.append(inner.find_previous('a').get('href'))
                if a == 10:
                    break
                else:
                    a = a + 1
        except Exception as error:
            print(error)
    else:
        main()

    for get_div in soup.find_all('div', class_='sold_out_tag'):
        if get_div.text == 'sold out':
            if get_div.parent.name == 'a':
                soldout.append(get_div.parent.get('href'))

    with open('soldout.txt', 'w', encoding='utf-8') as sold:
        sold.write('\n'.join(soldout))
    with open('last.txt', 'w', encoding='utf-8') as sold:
        sold.write('\n'.join(lastitems))


def monitor():
    soldlinks = open('soldout.txt', 'r', encoding='utf-8').read().splitlines()
    lastlinks = open('last.txt', 'r', encoding='utf-8').read().splitlines()
    newitems = []
    restockitems = []
    restock = []
    new = []
    restock.clear()
    newitems.clear()
    restockitems.clear()
    new.clear()

    retail = 0
    while retail == 0:
        info = supreme()

        if info[0]:
            try:
                a = 0
                soup = info[1]
                for inner in soup.find_all('div', class_='inner-article')[1:]:
                    newitems.append(inner.find_previous('a').get('href'))
                    if a == 10:
                        break
                    else:
                        a = a + 1
            except Exception as error:
                print(error)
        else:
            sleep(5)
            monitor()

        for data_new in newitems:
            if data_new in tuple(lastlinks):
                sleep(0.1)
            else:
                new.append(data_new)

        soup = info[1]
        for get_div in soup.find_all('div', class_='sold_out_tag'):
            if get_div.text == 'sold out':
                if get_div.parent.name == 'a':
                    restockitems.append(get_div.parent.get('href'))

        for data_restock in restockitems:
            if data_restock in tuple(soldlinks):
                pass
            else:
                restock.append(data_restock)

        if len(new) == 0:
            pass
        else:
            for link in new:
                base = 'https://www.supremenewyork.com{0}'.format(link)
                parse = base.rstrip() + '.json'
                type = 'NEW: '
                info = get_product(parse, base, type)

        if len(restock) == 0:
            pass
        else:
            for rlink in restock:
                base = 'https://www.supremenewyork.com{0}'.format(rlink)
                parse = base.rstrip() + '.json'
                type = 'RESTOCK: '
                info = get_product(parse, base, type)
                setting(info, type)


def setting(info, type):
    if info[0]:
        base = info[1]
        data = info[2]


    else:
        error_hooking(base=info[1], type=info[3])


def get_product(parse, base, type):
    session = requests.session()
    try:
        data = session.get(parse, headers=headers, proxies=get_proxies, timeout=10, verify=False).json()
        work = True
    except:
        try:
            data = session.get(parse, headers=headers, proxies=get_proxies(), timeout=10, verify=False).json()
            work = True
        except:
            try:
                data = session.get(parse, headers=headers, proxies=get_proxies(), timeout=10, verify=False).json()
                work = True
            except:
                data = None
                work = False

    info = [work, base, data]
    return info


def error_hooking(base, type):
    url = "<WEBHOOK>"
    embed = Webhook(url, color=123123)
    embed.set_desc(type.strip(':'))
    embed.add_field(name="Link", value=base)
    embed.add_field(name="Error", value="Can't get this product. Please contact with developer")
    embed.set_footer(text='Powered by <COMPANY NAME>', ts=True,icon='<ICON>')
    embed.post()


if __name__ == '__main__':
    print('Supreme Monitor Started')
    main()
