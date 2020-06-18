from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import datetime
import time
import sys
import os
from DNS import DNSCache
from HTTPParser import extract_html_page
from Header import coada_de_explorare, Q,robots_dictionary
import robots as rb
import shutil



class MyWebCrawler:
    def __init__(self):
        self.adresses_for_domains = {}
        self.limita = 0
        self.old_time = None
        self.current_time = None
        self.old_domain = None


    def start_crawler(self):

        for Link in Q:
            Page = None
            if coada_de_explorare[Link]['explorat'] == True:
                continue

            domain = urlparse(Link).netloc
            PagePath = urlparse(Link).path
            baselink = urlparse(Link).scheme + '://' + domain

            #daca nu exista deja fac folder pt domeniu
            if not (os.path.isdir(os.path.join('work_directory', domain))):
                os.mkdir(os.path.join('work_directory', domain))

            #verific daca am permisiune de la robots,daca nu dau skip la pagina
            if domain not in robots_dictionary:
                robo = rb.get_robo(baselink)
            else:
                robo = robots_dictionary[domain]
            if robo is not None:
                if not rb.canfetch(robo, PagePath, 'RIWEB_CRAWLER'):
                    continue

            path = domain + PagePath
            #verific daca am descarcat deja pagina
            if path.split('/')[-1] == '':
                if os.path.isfile(os.path.join('work_directory',path,'index.html')):
                    continue
            else:
                if os.path.isfile(os.path.join('work_directory',path)):
                    continue

            # verific daca am o adresa ip pentru newLink
            if domain not in self.adresses_for_domains:
                self.adresses_for_domains[domain] = {}

            if self.adresses_for_domains[domain] == {}:
                self.adresses_for_domains[domain] = DNSCache(domain, self.adresses_for_domains[domain])
            if self.adresses_for_domains[domain] is None:
                continue

            ip_adr = self.adresses_for_domains[domain]['ip_address']

            #respect delay ul de 1 secunda pe pagini din acelasi domeniu
            if ip_adr is not None or ip_adr != '':
                current_time = datetime.datetime.now()
                if self.old_time is None:
                    Page = extract_html_page(PagePath, domain, ip_adr, Link)
                    old_domain = domain
                elif (current_time - self.old_time).total_seconds() < 1 and self.old_domain == domain:
                    time.sleep(1)
                    Page = extract_html_page(PagePath, domain, ip_adr, Link)
                    old_time = current_time
                else:
                    Page = extract_html_page(PagePath, domain, ip_adr, Link)
                    self.old_time = current_time
                    self.old_domain = domain
            #extrag pagina pentru parsare
            if Page is not None:
                try:
                    getpage_soup = BeautifulSoup(Page, 'html.parser')
                except Exception as e:
                    print(e)
                    pass

                metas = getpage_soup.find_all('meta')
                #daca pot descarca pagina local
                permission1 = False
                # daca pot lua linkurile din pagina
                permission2 = False

                #parcurg toate tagurile meta din pagina si actualizez permisiunile
                for meta in metas:
                    if meta.get('name') == 'robots':
                        if 'all' in meta.get('content') or 'index' in meta.get('content'):
                            permission1 = True

                        if 'all' in meta.get('content') or 'follow' in meta.get('content'):
                            permission2 = True

                # daca n am nicio restrictie
                if not any(meta.get('name') == 'robots' for meta in metas):
                    permission1, permission2 = True, True

                #  salvez pagina si creez structura de directoare corespunzatoare
                if permission1 == True:
                    path = domain + PagePath
                    path = path.split('/')
                    current_path = os.path.join(os.getcwd(), 'work_directory')
                    for var in path[:-1]:
                        if (os.path.isdir(os.path.join(current_path, var))):
                            current_path = os.path.join(current_path, var)
                        else:
                            current_path = os.path.join(current_path, var)
                            os.mkdir(current_path)
                    if path[-1] == '':
                        nume_fisier = 'index.html'
                    else:
                        nume_fisier = path[-1]
                    with open('{}\{}.html'.format(current_path, nume_fisier.split('.')[0]), 'wb') as file:
                        file.write(Page.encode('utf8'))
                        self.limita += 1


                #salvez toate linkurile din pagini in vederea gasirii de  noi legaturi
                if permission2 == True:
                    a_tags = getpage_soup.find_all('a', href=True)
                    for a_tag in a_tags:
                        newLink = a_tag['href']

                        #daca pot extrage domeniu inseamna ca linkul e absoult
                        if bool(urlparse(newLink).netloc):
                            if newLink[:newLink.find(':')] == 'http':
                                newLink = newLink.split('#')[0]
                                if newLink not in coada_de_explorare.keys():
                                    #verifica robots pentru domeniu
                                    if urlparse(newLink).netloc not in robots_dictionary:
                                        robo = rb.getrobo(urlparse(newLink).scheme + '://' + urlparse(newLink).netloc)
                                    else:
                                        robo = robots_dictionary[urlparse(newLink).netloc]
                                    if robo is not None:
                                        if not rb.canfetch(robo, urlparse(newLink).path, 'RIWEB_CRAWLER'):
                                            continue

                                    path = urlparse(newLink).netloc + urlparse(newLink).path
                                    if path.split('/')[-1] == '':
                                        if os.path.isfile(os.path.join('work_directory', path, 'index.html')):
                                            continue
                                    else:
                                        if os.path.isfile(os.path.join('work_directory', path)):
                                            continue

                                    #daca are permisiune de roboti si nu este deja descarcata
                                    coada_de_explorare[newLink] = {'retry': 0, 'explorat': False}
                                    Q.append(newLink)
                        #daca nu este absolut si avem doar calea relativa
                        else:
                            newLink = urljoin(Link, newLink)
                            newLink = newLink.split('#')[0]

                            #verific permisiunea IN robots
                            if newLink not in coada_de_explorare.keys() and os:
                                if urlparse(newLink).netloc not in robots_dictionary:
                                    robo = rb.getrobo(urlparse(newLink).scheme + '://' + urlparse(newLink).netloc)
                                else:
                                    robo = robots_dictionary[urlparse(newLink).netloc]
                                if robo is not None:
                                    if not rb.canfetch(robo, urlparse(newLink).path, 'RIWEB_CRAWLER'):
                                        continue
                                #verific daca exista deja un fisier cu acest nume
                                path = urlparse(newLink).netloc + urlparse(newLink).path
                                if path.split('/')[-1] == '':
                                    if os.path.isfile(os.path.join('work_directory', path, 'index.html')):
                                        continue
                                else:
                                    if os.path.isfile(os.path.join('work_directory', path)):
                                        continue
                                # daca are permisiune de roboti si nu este deja descarcata
                                coada_de_explorare[newLink] = {'retry': 0, 'explorat': False}
                                Q.append(newLink)

            if self.limita == 100:
                break


if __name__ == "__main__":

    folder = 'work_directory'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            pass

    #apel crawler
    myWC=MyWebCrawler();

    start_time = datetime.datetime.now()
    print('Start la: ', start_time)
    myWC.start_crawler()
    print('Durata:', str(datetime.datetime.now() - start_time))
