from pytube import YouTube
from pytube import Channel
import xlsxwriter
import urllib3
import json
from data import videos, titles, names
from comments import getTopComments

http = urllib3.PoolManager()

counter = 0


def getVideoExtraData(videoUrl, worksheet, row, column):
    try:
        baseUrl = 'https://www.googleapis.com/youtube/v3/videos'
        apiKey = 'AIzaSyCd6enxNAQhq-W_s3pzE-F-TpQFg4pjZ0s'
        parts = 'snippet,statistics,contentDetails'
        videoId = videoUrl.replace('https://www.youtube.com/watch?v=', '')

        url = '{}?key={}&part={}&id={}'.format(
            baseUrl, apiKey, parts, videoId)

        videoDetails = http.request('GET', url).data.decode('utf-8')
        videoDetails = json.loads(videoDetails)

        statistics = videoDetails['items'][0]['statistics']

        commentCount = statistics['commentCount'] if 'commentCount' in statistics else 0
        print(f'Numero de comentarios: {commentCount}')
        worksheet.write(row, column, commentCount)
        column += 1

        likeCount = statistics['likeCount'] if 'likeCount' in statistics else 0
        print(f'Numero de likes: {likeCount}')
        worksheet.write(row, column, likeCount)
        column += 1

        favoriteCount = statistics['favoriteCount'] if 'favoriteCount' in statistics else 0
        print(f'Numero de favoritos: {favoriteCount}')
        worksheet.write(row, column, favoriteCount)
        column += 1

        print(f'DETAILS URL: {url}')

    except Exception as e:
        worksheet.write(row, column, url)
        print(f'FAILED EXTRA DATA: {e}')


for video in videos:
    videosData = []
    channel_info = Channel(video)

    filePath = f'files/{names[counter]}'

    workbook = xlsxwriter.Workbook(f'{filePath}.xlsx')
    worksheet = workbook.add_worksheet()
    row = 1
    column = 0

    for title in titles:
        worksheet.write(0, column, title)
        column += 1

    column = 0

    for url in channel_info.url_generator():
        try:
            video_details = YouTube(url)
            views = video_details.views
            title = video_details.title
            author = video_details.author
            publish_date = video_details.publish_date
            publish_year = publish_date.year
            publish_date = publish_date.strftime("%d/%m/%Y")
            duration = video_details.streaming_data["formats"][0]["approxDurationMs"]
            duration = int(duration)

            seconds = (duration/1000) % 60
            seconds = int(seconds)
            minutes = (duration/(1000*60)) % 60
            minutes = int(minutes)
            hours = (duration/(1000*60*60)) % 24

            duration = "%d:%d:%d" % (hours, minutes, seconds)

            print('---------------------------------------------------------')

            print(f'Titulo: {title}')
            worksheet.write(row, column, title)
            column += 1

            print(f'Numero de visitas: {views}')
            worksheet.write(row, column, views)
            column += 1

            print(f'Duracion: {duration}')
            worksheet.write(row, column, duration)
            column += 1

            print(f'A??o de publicacion: {publish_year}')
            worksheet.write(row, column, publish_year)
            column += 1

            print(f'Fecha de publicacion: {publish_date}')
            worksheet.write(row, column, publish_date)
            column += 1

            print(f'Autor: {author}')
            worksheet.write(row, column, author)
            column += 1

            print(f'URL: {url}')
            worksheet.write(row, column, url)
            column += 1

            getVideoExtraData(url, worksheet, row, column)

            print('---------------------------------------------------------\n')
            row += 1
            column = 0
        except Exception as e:
            worksheet.write(row, column, url)
            print(f'FAILED: {e}')

        videosData.append({
            'title': title,
            'views': views,
            'url': url,
        })
    top5 = []

    for i in range(5):
        topVideo = max(videosData, key=lambda ev: ev['views'])
        top5.append(topVideo)
        videosData.remove(topVideo)

    getTopComments(top5, filePath)

    counter += 1
    workbook.close()
