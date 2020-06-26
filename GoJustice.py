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


# h264_nvenc  # Nvidia GPU (win/linux)
# h264_amf    # AMD GPU (windows only)
# h264_qsv    # Intel Quick Sync Video (hardware embedded in modern Intel CPU)
# h264_mf     # MediaFoundation (win)


def toTimecode( sec ) :
    m = math.floor( sec / 60 )
    s = sec % 60

    if m < 10 :
        m = '0' +  str( m )
    else :
        m = str( m )

    if s < 10 :
        s = '0' +  str( s )
    else :
        s = str( s )

    return '00:' + m + ':' + s + ',000'


optEnc = sys.stdout.encoding
error  = []


os.system('cls')
print( 'GoJustice 影片時間戳記燒錄器 1.0' )
print( 'https://github.com/cacaplus/gojustice\n' )


ffmpegBinPath   = ''
ffprobeBinPath  = ''


PATTERN = {
    'fileName'  : r'.+\.(mp4|mov|avi)$',
    'fileTimeGP': r'^((\d{8}|\d{4})_(\d{9}))',
    'fileTime'  : r'^((\d{8}|\d{4})_(\d{6}))',
    'fileParam' : r'(_@(.+)?\.)',

    'PARAM' : {

        # 一般參數
        'AllowAudio'  : r'^A$',
        'CutLength'   : r'^C(\d{2})(\d{2})L(\d{3,5})$',
        'CutRange'    : r'^C(\d{2})(\d{2})-(\d{2})(\d{2})$',
        'Bitrate'     : r'^B(\d)+(k|m)$',
        'Size'        : r'^S(\d+)m$',
        'Resize'      : r'^R(\d{4})$',
        'Framerate'   : r'^F(\d{2,3})$',

        # 區域預設
        'isHighway'   : r'^HW$',
        'isTaipei'    : r'^TP$',
        'isXinbei'    : r'^XB$',
    },

    'CODEC' : r'^codec_name=(h264|hevc|mjpeg)$'
}

FPS = {
    24 : 'fps=24000/1001',
    30 : 'fps=30000/1001',
    60 : 'fps=60000/1001',
}

fileListOrig    = []
videoListOrig   = []
videoList       = []
videoResultList = []

encoder = None
encoderList = [ 'h264_amf', 'h264_nvenc', 'h264_qsv', 'h264_mf' ]

numSuccess      = 0
numFailed       = 0

defaultBitrateMax =   10000  # 10000 Kbps
defaultSizeMax    =      29  # 30 MB


# 主流程
while True:

    print( '取得設定：\n' )

    # 環境檢查
    while True:

        print( '    正在檢查執行環境...' )

        # 清除暫存檔
        srtList = glob.glob( './*.srt' )
        for i in range( len( srtList ) ) :
            os.remove( srtList[ i ]  )


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

            print( '    中止' )
            break

        ffmpegBinPath  = 'bin/ffmpeg.exe'
        ffprobeBinPath = 'bin/ffprobe.exe'

        time.sleep( 0.1 )

        break

    if len( error ) > 0 :
        break



    # 確認使用的 codec
    while True:

        print( '    正在確認編碼器...' )

        for i in range( len( encoderList ) ) :
            enc = encoderList[i]

            pipeResult = subprocess.run([
                ffmpegBinPath,
                '-y', '-f', 'lavfi', '-i', 'nullsrc',
                '-frames:v', '1', '-vcodec', enc,
                'codecTest.mp4'
            ], stdout = subprocess.PIPE, stderr = subprocess.PIPE )
            result = pipeResult.stderr.decode( 'utf-8' )

            os.remove( 'codecTest.mp4' )

            hasError = re.search( r'Conversion failed!', result )
            if hasError == None :
                encoder = enc
                break

        if encoder == None :

            error.append( '[E0102] 找不到可用的 h264 編碼器，請將此錯誤通知開發者。' )

            print( '    中止' )
            breakpoint

        break

    if len( error ) > 0 :
        break


    # 尋找檔案
    while True:
        print( '    正在取得檔案清單與設定...' )

        fileListOrig = glob.glob( './input/*' )

        # 檢查每個檔案
        for i in range( len( fileListOrig ) ) :
            fileName = os.path.basename( fileListOrig[i] )
            filePath = 'input/' + fileName

            # 檢查檔名是否為影片檔
            if re.search( PATTERN['fileName'], fileName, flags = re.IGNORECASE ) == None:
                continue

            videoFile = {
                'fileName' : fileName,
                'filePath' : filePath,
                'optName'  : None,
                'optPath'  : None,
                'subFile'  : str( round( time.time() ) ) + '.srt',
                'codec'    : None,
                'duration' : 0,
                'isGoPro'  : False,
                'videoTime': 0,
                'width'    : 0,
                'height'   : 0,
                'bitrate'  : 0,
                'framerate': None,
                'param'    : {}
            }

            # 取得檔案資訊
            pipeResult = subprocess.run([
                ffprobeBinPath,
                '-v', 'quiet', '-select_streams', 'v:0',
                '-print_format', 'json', '-show_streams', '-show_format',
                filePath
            ], stdout = subprocess.PIPE)
            result = json.loads( pipeResult.stdout.decode( 'utf-8' ) )

            if 'streams' not in result :
                continue

            fr = result['streams'][0]['r_frame_rate'].split('/')

            videoFile['codec']     =        result['streams'][0]['codec_name']
            videoFile['duration']  = float( result['streams'][0]['duration'] )
            videoFile['width']     =   int( result['streams'][0]['width'] )
            videoFile['height']    =   int( result['streams'][0]['height'] )
            videoFile['bitrate']   =   int( result['streams'][0]['bit_rate'][0:-3] )
            videoFile['framerate'] = round( int(fr[0]) / int(fr[1]), 2 )

            if 'tags' in result['streams'][0] :
                if 'handler_name' in result['streams'][0]['tags'] :
                    if result['streams'][0]['tags']['handler_name'].strip() == 'GoPro AVC' :
                        videoFile['isGoPro'] = True

            # 檢查設定的參數
            # 時間
            # 1. 檢查是否有內建的時間戳記 (因可能不準所以暫停使用)
            # 2. 檢查檔名的時間
            matchGP = re.search( PATTERN['fileTimeGP'], fileName, flags = re.IGNORECASE )
            match   = re.search( PATTERN['fileTime'],   fileName, flags = re.IGNORECASE )

            if match == None :
                continue

            if matchGP != None :
                videoTime = time.mktime( time.strptime( matchGP.group(1), '%Y%m%d_%H%M%S000' ) )
                videoTime += 28800  # fix for gopro +0800
            else :
                videoTime = time.mktime( time.strptime( match.group(1), '%Y%m%d_%H%M%S' ) )

            videoFile['videoTime'] = videoTime

            # 3. 檢查所有設定的參數
            match = re.search( PATTERN['fileParam'], fileName, flags = re.IGNORECASE )

            videoFile['param']['AllowAudio'] = False
            videoFile['param']['Cut']        = None
            videoFile['param']['Duration']   = None
            videoFile['param']['CutLength']  = None
            videoFile['param']['CutRange']   = None
            videoFile['param']['Bitrate']    = None
            videoFile['param']['Size']       = None
            videoFile['param']['Resize']     = None
            videoFile['param']['Framerate']  = None
            videoFile['param']['Size']       = '30'

            if match != None :
                paramStr   = match.group(2)
                paramArray = paramStr.split( ',' )

                for ppi in PATTERN['PARAM'] :
                    videoFile['param'][ ppi ] = None
                    for pi in range( len( paramArray ) ) :
                        paramItemMatch = re.search( PATTERN['PARAM'][ppi], paramArray[pi], flags = re.IGNORECASE )
                        if paramItemMatch != None :

                            if ppi == 'AllowAudio' :
                                videoFile['param'][ ppi ] = True

                            if ppi == 'CutLength' :
                                CutStart = int( paramItemMatch.group(1) ) * 60 + int( paramItemMatch.group(2) )
                                CutLen   = float( paramItemMatch.group(3) ) / 100
                                videoFile['param']['Cut'] = {
                                    'start' : CutStart,
                                    'len'   : CutLen
                                }
                                videoFile['param']['Duration'] = CutLen

                            if ppi == 'CutRange' :
                                CutStart = int( paramItemMatch.group(1) ) * 60 + int( paramItemMatch.group(2) )
                                CutEnd   = int( paramItemMatch.group(3) ) * 60 + int( paramItemMatch.group(4) )
                                videoFile['param']['Cut'] = {
                                    'start' : CutStart,
                                    'len'   : CutEnd - CutStart
                                }
                                videoFile['param']['Duration'] = CutEnd - CutStart

                            if ppi == 'Bitrate' :
                                rate = int( paramItemMatch.group(1) )
                                if paramItemMatch.group(2).lower() == 'm' :
                                    rate = rate * 1000
                                rate = round( rate * 0.97 )
                                videoFile['param'][ ppi ] = rate

                            if ppi == 'Size' :
                                videoFile['param'][ ppi ] = int( paramItemMatch.group(1) )

                            if ppi == 'Resize' :
                                videoFile['param'][ ppi ] = int( paramItemMatch.group(1) )

                            if ppi == 'Framerate' :
                                videoFile['param'][ ppi ] = int( paramItemMatch.group(1) )

                            continue

            # 確認設定是否無誤
            # 1. 檢查起始時間是否超過
            if 'Cut' in videoFile['param'] :
                if videoFile['param']['Cut'] != None :
                    if videoFile['param']['Cut']['start'] > videoFile['duration'] :
                        continue

            # 建立輸出的檔名
            optName = re.sub( r'(_@.*)?\.(.+)$', '.ts.mp4', fileName )
            videoFile['optName'] =             optName
            videoFile['optPath'] = 'output/' + optName

            # 加入佇列
            videoList.append( videoFile )


        time.sleep( 0.1 )

        break


    # 處理檔案
    while len( videoList ) > 0:

        print( '\n找到以下檔案：\n' )

        # 列出檔案
        for i in range( len( videoList ) ) :
            fileNo = i + 1
            print( str( fileNo ).rjust( 6, ' '), end = '' )
            print( '. ' + videoList[i]['fileName'] )

        time.sleep( 0.1 )
        print( '\n開始轉檔：\n' )

        # 轉檔
        for i in range( len( videoList ) ) :
            fileNo    = i + 1
            videoFile = videoList[i]


            print( str( fileNo ).rjust( 6, ' ') + '. ' + videoFile['fileName'] )

            duration = videoFile['duration']

            if videoFile['param']['Duration'] != None :
                duration = videoFile['param']['Duration']

            bitrate = str( min( videoFile['bitrate'], round( defaultSizeMax / duration * 1000 * 8 ) ) ) + 'k'

            # 產生時間碼字幕
            timestampSubtitle = ''
            start = videoFile['videoTime']
            for sec in range( math.ceil( videoFile['duration'] ) ) :

                t  = time.localtime( start + sec )
                no = sec + 1

                timestampSubtitle += str( sec ) + '\n'
                timestampSubtitle += toTimecode( sec ) + ' --> ' + toTimecode(sec + 1) + '\n'
                timestampSubtitle += time.strftime( '%Y/%m/%d %H:%M:%S', t ) + '\n\n'

            f = open( videoFile['subFile'] , "w")
            f.write( timestampSubtitle )
            f.close()

            vf = [ 'subtitles='+ videoFile['subFile'] +':force_style=\'Fontsize=12,PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=0,Shadow=0,Alignment=3,MarginR=8\'' ]

            # 縮放
            if videoFile['param']['Resize'] != None :
                if videoFile['width'] > videoFile['param']['Resize'] :
                    vf.append( 'scale='+ str(videoFile['param']['Resize']) +':-2:flags=lanczos' )

            # FPS

            # 產生 bitrate
            if videoFile['param']['Size'] != None :
                bitrate = str( min( videoFile['bitrate'], round( videoFile['param']['Size'] / duration * 1000 * 8 ) ) ) + 'k'
            else :
                if videoFile['param']['Bitrate'] != None :
                    bitrate = str( videoFile['param']['Bitrate'] ) + 'k'

            # 產生指令
            command = [ ffmpegBinPath,
                    '-y',
                    '-hide_banner',
                    '-loglevel',    'panic',
                    '-i',            videoFile['filePath'],
                    '-c:v',          encoder,
                    '-vf',          ','.join( vf ),
                    '-preset',      'slow',
                    '-b:v',          bitrate,
                ]

            if videoFile['param']['Cut'] != None :
                command.append( '-ss' )
                command.append( str( videoFile['param']['Cut']['start'] ) )
                command.append( '-t' )
                command.append( str( videoFile['param']['Cut']['len'] ) )
                command.append( '-pass' )
                command.append( '2' )

            if videoFile['param']['AllowAudio'] != True :
                command.append('-an')

            command.append( videoFile['optPath'] )

            pipeResult = subprocess.run(command, stdout = subprocess.PIPE)
            result = pipeResult.stdout.decode('utf-8')
            os.remove( videoFile['subFile']  )

        break


    # 主流程結束
    break


if len( error ) > 0 :

    print( '\n發生錯誤：\n' )

    for i in range( len( error ) ):
        print( '    ' + error[i] )

else :

    print( '\n轉檔完成，共 '+ str( len( videoList ) ) + ' 個檔案。' )
