import sqlite3
import billboard
import pytube
import requests
from bs4 import BeautifulSoup
import os
import subprocess
import threading

class PeachData:

    def __init__(self):
        self.billboardMusicList = []
        self.conn = sqlite3.connect('music_database.db')
        self.c = self.conn.cursor()

    def initBillboard(self):
        l = billboard.charts()
        #hot-100 chart 가져오기
        s = billboard.ChartData('hot-100')

        chart_list = []
        for i in range(100):
            chart_list.append((s[i].title,s[i].artist,self.crawling(s[i].artist,s[i].title, 'h3 > a')))
        #print(chart_list)

        self.c.execute('''DELETE FROM chart_billboard''')

        cnt = 0
        for i in chart_list:
            cnt+=1
            self.c.execute('''INSERT INTO chart_billboard VALUES (?,?,?,?,DATETIME(\'NOW\'));''',(cnt,i[0],i[1],i[2]))

        # Save (commit) the changes
        self.conn.commit()

    def setBillboardMusicList(self):
        ret = []
        self.c.execute("SELECT * FROM chart_billboard")
        all_rows = self.c.fetchall()
        for i in all_rows:
            ret.append(i)
        self.billboardMusicList = ret

    def getBillboardMusicList(self):
        return self.billboardMusicList

    def crawling(self, artist, title,  parsingTag):
        link = 'https://www.youtube.com/results?search_query='
        link = link + artist+ "+" + title
        req = requests.get(link)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        try:
            resultLink = soup.select(
                parsingTag
            )[0]['href']
        except:
            print(link)
            return "Error"    
        return "https://www.youtube.com/"+resultLink

    def __del__(self):
        self.conn.commit()
        self.conn.close()

class YoutubeDownloader(threading.Thread):
    def __init__(self,link,directory):
        threading.Thread.__init__(self)
        self.link = link
        self.directory = directory
        
    def run(self):
        try:
            yt = pytube.YouTube(self.link)
            parent_dir = self.directory+"video/"
            parent_dir2 = self.directory+"audio/"

            vids = yt.streams.filter(mime_type = "video/mp4").first()

            default_filename = vids.default_filename
            vids.download(parent_dir)

        except:
            print("Download Error")
        else:
            new_filename = str(default_filename).replace(".mp4",".mp3")
            subprocess.Popen(['ffmpeg', '-i', parent_dir + default_filename, parent_dir2 + new_filename])
            print("Download Complete!")
