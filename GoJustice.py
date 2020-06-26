import os
import re
import sys
import pytz
import glob
import json
import math
import time
import pathlib
import subprocess
from os import path
from pprint import pprint
from dateutil import parser
from datetime import datetime


optEnc = sys.stdout.encoding
error  = []


os.system('cls')
print( 'GoJustice 影片時間戳記助手\n' )


ffmpegBinPath   = ''
ffprobeBinPath  = ''


PATTERN = {
    'fileName'  : r'.+\.(mp4|mov|avi)$',
    'fileTime'  : r'^(\d{8}|\d{4})_(\d{6})',
    'fileParam' : r'(_@(.+)?\.)',

    'PARAM' : {
        'AllowAudio'  : r'^A$',
        'CropLength'  : r'^C(\d{4}):(\d{3,5})$',
        'CropRange'   : r'^C(\d{4})-(\d{4})$',
        'Bitrate'     : r'^B(\d)+(k|m)$',
        'Size'        : r'^S(\d)+(m)$',
        'Resize'      : r'^R(\d{4})$',
        'Framerate'   : r'^F\d{2}$'
    },

    'CODEC' : r'^codec_name=(h264|hevc|mjpeg)$'
}

fileListOrig    = []
fileList        = []
fileCfgedList   = []
fileResultList  = []

numSuccess      = 0
numFailed       = 0


# 主流程
while True:

    # 環境檢查
    while True:

        print( '正在檢查執行環境...', end = '' )

        # 資料夾檢查
        if path.exists( 'bin' ) == False :
            os.mkdir( 'bin' )

        if path.exists( 'config' ) == False :
            os.mkdir( 'config' )

        if path.exists( 'input' ) == False :
            os.mkdir( 'input' )

        if path.exists( 'output' ) == False :
            os.mkdir( 'output' )

        # 檢查是否有 ffmpeg
        if( path.exists( 'bin/ffmpeg.exe' ) == False
                or path.exists( 'bin/ffprobe.exe' ) == False ) :

            error.append( '[E0101] 找不到 ffmpeg 執行檔，請參閱使用說明修正。' )

            print( '中止' )
            break

        ffmpegBinPath  = 'bin/ffmpeg.exe'
        ffprobeBinPath = 'bin/ffprobe.exe'

        time.sleep( 0.1 )
        print( '完成' )

        break


    # 尋找檔案
    while True:
        print( '正在取得檔案清單與設定...', end = '' )

        fileListOrig = glob.glob( './input/*' )

        # 檢查每個檔案
        for i in range( len( fileListOrig ) ) :
            fileName = 'input/' + os.path.basename( fileListOrig[i] )

            # 檢查檔名是否為影片檔
            if re.search( PATTERN['fileName'], fileName, flags = re.IGNORECASE ) == None:
                continue

            videoItem = {
                'fileName' : fileName,
                'codec'    : None,
                'type'     : None,
                'Param'    : []
            }

            # 檢查檔案編碼
            pipeResult = subprocess.run([
                ffprobeBinPath,
                '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name', '-of', 'default=nw=1',
                fileName
            ], stdout = subprocess.PIPE)
            result = pipeResult.stdout.decode( 'utf-8' ).rstrip()
            match  = re.search( PATTERN['CODEC'], result, flags = re.IGNORECASE )

            if match == None :
                continue

            videoItem['codec'] = match.group(1)

            # 檢查設定的參數
            while True:

                # 1. 檢查是否有內建的時間戳記
                pipeResult = subprocess.run([
                    ffprobeBinPath,
                    '-v', 'quiet', '-print_format', 'json',
                    '-show_format',
                    fileName
                ], stdout = subprocess.PIPE)

                result = pipeResult.stdout.decode( 'utf-8' ).rstrip()
                pprint( result )

                break

            fileList.append( fileName )

        time.sleep( 0.1 )
        print( '找到' + str( len( fileList ) ) + '個支援的檔案' )

        pprint( fileList )

        break


    # 處理檔案
    while len( fileList ) > 0:

        break



    # 主流程結束
    break


if len( error ) > 0 :

    print( '\n發生錯誤：' )

    for i in range( len( error ) ):
        print( error[i] )

else :

    print( '\n完成。' )
