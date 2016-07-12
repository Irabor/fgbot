#!/usr/bin/env python
import socket
import string
import re
import urllib2
from sys import argv
from urllib import urlencode
import time
user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"
headers_ = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": user_agent,
    "Connection": "keep-alive",
}
#host = argv[1]
nick = "grep_bot"
PORT = 6667
#chan = argv[2]
readbuffer = ""
gnu = None
def irc(HOST, channel):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.recv(4000)
    s.send('USER duff duff duff :duff IRC\r\n')
    s.send('NICK %s\r\n' %nick)
    s.send('JOIN %s\r\n' %channel)
    while True:
        data = s.recv(1024)
        mss = data.split(':')[-1]
        if data.find('PING') != -1:
            s.send('PONG ' +  data.split()[1] +'\r\n')
        with open('log.txt','wb')as f:
            f.write(mss)
        if '.show ' in mss:
            x = mss.split('.show ')[-1]
            feild = {
            'query': x
            }
            urlsearch = 'https://trakt.tv/search?'
            get = urllib2.Request(urlsearch+urlencode(feild), headers=headers_)
            html = urllib2.urlopen(get)
            html = html.read()
            match = re.compile(r'(https\:\/\/\w+\.\w+\/\w{6}\/\S+\")')
            #match = re.compile(r'(\<meta\w{7})')
            match = re.search(match, html)
            if match == None:
                s.send('PRIVMSG %s :.....\r\n' %(channel))
            else:
                movie_link = match.group()
                movie_link = movie_link.replace('"','')
                html = urllib2.urlopen(movie_link)
                html = html.read()
            genre_ =''
            #match = re.compile(r'(\<meta\s\w{7}\=\"(https)+\S+)')
            match = re.compile(r'(\s\w{8}\=\"g\w+\"\>\w+)') #genre
            genres = re.finditer(match, html)
            if genres == None:
                s.send('PRIVMSG %s :.....\r\n' %(channel))
            else:
                for genre in genres:
                    genre_ += genre.group()
                tags = ['itemprop','"','genre','>','=']
                for tag in tags:
                    genre_ = genre_.replace(tag,'')
                s.send('PRIVMSG %s :GENRE:%s\r\n' %(channel,genre_))
            match = re.compile(r'(meta\s\w{8}\=\S+\:\w{11}\"\s\w+\=\"(.*?)\")') #description
            descrip = re.search(match,html)
            if descrip == None:
                s.send('PRIVMSG %s :SYNOPISIS: no synonpsis\r\n'%(channel))
            else:
                descrip = descrip.group()
                tags = ['meta property', '=','og:description','"', 'content']
                for tag in tags:
                    descrip = descrip.replace(tag,'')
                s.send('PRIVMSG %s :SYNOPSIS:%s\r\n' %(channel, descrip))
            #director
            match = re.compile(r'( href\=\"\/people\/\S+\")') #director
            director = re.search(match,html)
            if director == None:
                s.send('PRIVMSG %s :DIRECTOR: no director...\r\n'%(channel))
            else:
                director = director.group()
                tags_ = ['/people/','href','=','"']
                for tag in tags_:
                    director = director.replace(tag,'')
                director = director.capitalize()
                s.send('PRIVMSG %s :DIRECTOR:%s\r\n' %(channel, director))
if __name__ == '__main__':
    def main():
        irc(argv[1], argv[2])
    main()
