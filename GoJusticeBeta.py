import os
import re
import sys
import glob
import json
import math
import time
import pathlib
import subprocess
from os import path
from pprint import pprint


# h264_nvenc  # Nvidia GPU (win/linux)
# h264_amf    # AMD GPU (windows only)
# h264_qsv    # Intel Quick Sync Video (hardware embedded in modern Intel CPU)
# h264_mf     # MediaFoundation (win)


DEBUG  = False
RUNENC = True
DELSRT = True


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
print( 'GoJustice 影片時間戳記燒錄器 0.981' )
print( 'https://github.com/cacaplus/gojustice\n' )


ffmpegBinPath   = ''
ffprobeBinPath  = ''


PATTERN = {
    'fileName'  : r'.+\.(mp4|mov|avi)$',
    'fileTimeGP': r'^((\d{8})([-_])(\d{9}))',
    'fileTime'  : r'^((\d{8})([-_])(\d{6}))',
    'fileTimeS' : r'^((\d{4})([-_])(\d{6}))',
    'fileParam' : r'(_@(.+)?\.)',

    'PARAM' : {

        # 一般參數
        'AllowAudio'   : r'^A$',
        'CutLength'    : r'^C(\d{2})(\d{2})L(\d{3,5})$',
        'CutRange'     : r'^C(\d{2})(\d{2})-(\d{2})(\d{2})$',
        'Bitrate'      : r'^B(\d+)(k|m)$',
        'Size'         : r'^S(\d+)m$',
        'Resize'       : r'^R(\d{3,4})$',
        'Framerate'    : r'^F(\d.+)$',
        'Watermark'    : r'^(W(\d+)?)$',
        'DisableTime'  : r'^TX$',
        'Turn'         : r'^(T|TL|TR)$',
        'Flip'         : r'^(FH|FV)$',
        'Crop'         : r'^CR(\d+)(x(\d+)((\-[N|S|E|W]{1,2}))?)?$',
        'Predefined'   : r'^Z(.+)$',
    },

    'CODEC' : r'^codec_name=(h264|hevc|mjpeg)$'
}

fileListOrig     = []
videoListOrig    = []
videoList        = []
invalidVideoList = []
videoResultList  = []

encoder = None
encoderList = [ 'h264_amf', 'h264_nvenc', 'h264_qsv', 'h264_mf' ]

numSuccess      = 0
numFailed       = 0

defaultBitrateMax =   10000  # 10000 Kbps
defaultSizeMax    =      29  # 30 MB


# 主流程
while True:

    print( '  # 取得設定：\n' )

    # 環境檢查
    while True:

        print( '     1. 正在檢查執行環境...' )

        # 清除暫存檔
        if DELSRT :
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

        if path.exists( 'watermark' ) == False :
            os.mkdir( 'watermark' )

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

        print( '     2. 正在確認編碼器...' )

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
            break

        break

    if len( error ) > 0 :
        break


    # 尋找檔案
    while True:
        print( '     3. 正在取得檔案清單與設定...' )

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
                'warn'     : [],
                'error'    : [],
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

            videoFile['codec']       =        result['streams'][0]['codec_name']
            videoFile['duration']    = float( result['streams'][0]['duration'] )
            videoFile['width']       =   int( result['streams'][0]['width'] )
            videoFile['height']      =   int( result['streams'][0]['height'] )
            videoFile['bitrate']     =   int( result['streams'][0]['bit_rate'][0:-3] )

            fr = result['streams'][0]['r_frame_rate' ]
            frMatch = re.search( r'^(\d+)(\/(\d+))?$', fr, flags = re.IGNORECASE )
            videoFile['framerate'] = [ int( frMatch.group(1) ), int( frMatch.group(3) ) ]

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
            matchS  = re.search( PATTERN['fileTimeS'],  fileName, flags = re.IGNORECASE )

            videoTime = None

            if matchGP != None :
                videoTime = time.mktime( time.strptime( matchGP.group(1), '%Y%m%d'+ matchGP.group(3) +'%H%M%S000' ) )
                videoTime += 28800  # fix for gopro +0800
            else :
                if match != None :
                    videoTime = time.mktime( time.strptime( match.group(1), '%Y%m%d'+ match.group(3) +'%H%M%S' ) )
                else :
                    if matchS != None :
                        y = time.strftime( '%Y' )
                        videoTime = time.mktime( time.strptime( time.strftime( '%Y' ) + matchS.group(1), '%Y%m%d'+ matchS.group(3) +'%H%M%S' ) )

            if videoTime == None :
                continue

            videoFile['videoTime'] = videoTime

            # 3. 檢查所有設定的參數
            match = re.search( PATTERN['fileParam'], fileName, flags = re.IGNORECASE )

            videoFile['param']['AllowAudio']  = False
            videoFile['param']['Cut']         = None
            videoFile['param']['Duration']    = None
            videoFile['param']['CutLength']   = None
            videoFile['param']['CutRange']    = None
            videoFile['param']['Bitrate']     = None
            videoFile['param']['Size']        = None
            videoFile['param']['Resize']      = None
            videoFile['param']['Framerate']   = None
            videoFile['param']['Size']        = None
            videoFile['param']['Watermark']   = None
            videoFile['param']['DisableTime'] = False

            if match != None :
                paramStr   = match.group(2)
                paramArray = paramStr.split( ',' )

                for ppi in PATTERN['PARAM'] :
                    videoFile['param'][ ppi ] = None
                    for pi in range( len( paramArray ) ) :
                        paramItemMatch = re.search( PATTERN['PARAM'][ppi], paramArray[pi], flags = re.IGNORECASE )
                        if paramItemMatch != None :

                            if ppi in [ 'AllowAudio', 'DisableTime' ] :
                                videoFile['param'][ ppi ] = True

                            if ppi == 'CutLength' :
                                CutStart = int( paramItemMatch.group(1) ) * 60 + int( paramItemMatch.group(2) )
                                CutLen   = float( paramItemMatch.group(3) ) / 100
                                if CutStart > videoFile['duration'] :
                                    videoFile['error'].append('開始時間錯誤')
                                if CutLen <= 0 :
                                    videoFile['error'].append('長度不得為0')
                                videoFile['param']['Cut'] = {
                                    'start' : CutStart,
                                    'len'   : CutLen
                                }
                                videoFile['param']['Duration'] = CutLen

                            if ppi == 'CutRange' :
                                CutStart = int( paramItemMatch.group(1) ) * 60 + int( paramItemMatch.group(2) )
                                CutEnd   = int( paramItemMatch.group(3) ) * 60 + int( paramItemMatch.group(4) )
                                if CutStart > videoFile['duration'] :
                                    videoFile['error'].append('開始時間錯誤')
                                if CutEnd ==  CutStart :
                                    videoFile['error'].append('長度不得為0')
                                if CutEnd < CutStart :
                                    videoFile['error'].append('結束時間錯誤')
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
                                videoFile['param']['Bitrate'] = rate

                            if ppi in [ 'Size', 'Resize' ]  :
                                videoFile['param'][ ppi ] = int( paramItemMatch.group(1) )

                            if ppi == 'Framerate' :
                                videoFile['param']['Framerate'] = paramItemMatch.group(1)

                            if ppi == 'Watermark' :
                                # 檢查水印是否存在
                                wmList = glob.glob( './watermark/' + paramItemMatch.group(1) + '.png' )
                                if( len( wmList ) >= 1 ) :
                                    videoFile['param']['Watermark'] = wmList[0]
                                else :
                                    videoFile['error'] = ['水印檔不存在']

                            continue

            # 確認設定是否無誤
            # 1. 檢查起始時間是否超過
            if 'Cut' in videoFile['param'] :
                if videoFile['param']['Cut'] != None :
                    if videoFile['param']['Cut']['start'] > videoFile['duration'] :
                        continue

            # 建立輸出的檔名
            optName = re.sub( r'(_@.*)?\.(.+)$', '.mp4', fileName )
            videoFile['optName'] =             optName
            videoFile['optPath'] = 'output/' + optName

            # 加入佇列
            if len( videoFile['error'] ) > 0 :
                invalidVideoList.append( videoFile )
            else :
                videoList.append( videoFile )


        time.sleep( 0.1 )

        break


    # 處理檔案
    while len( videoList ) > 0:

        print( '\n  # 找到以下檔案：\n' )

        # 列出檔案
        for i in range( len( videoList ) ) :
            fileNo = i + 1
            print( str( fileNo ).rjust( 6, ' '), end = '' )
            print( '. ' + videoList[i]['fileName'] )

        if len( invalidVideoList ) > 0 :
            print( '\n    以下檔案含有錯誤設定：\n' )

        # 列出檔案
        for i in range( len( invalidVideoList ) ) :

            fileNo = i + 1
            print( str( fileNo ).rjust( 6, ' '), end = '' )
            print( '. ' + invalidVideoList[i]['fileName'] + '...錯誤：', end = '' )
            print( '、'.join( invalidVideoList[i]['error'] ) )


        if RUNENC == False :

            print( '\n    測試模式，忽略轉檔。\n' )
            break


        time.sleep( 0.1 )
        print( '\n  # 開始轉檔：' )

        # 轉檔
        for i in range( len( videoList ) ) :
            fileNo    = i + 1
            videoFile = videoList[i]

            if len( videoFile['error'] ) > 0 :
                continue

            if videoFile['param']['Watermark'] != None :
                watermarkList = glob.glob( './watermark/' + videoFile['param']['Watermark'] + '.png' )

            vf = []

            print( '\n' + str( fileNo ).rjust( 6, ' ') + '. ' + videoFile['fileName'] )
            print( '          -> ' + videoList[i]['optName'] )

            duration = videoFile['duration']

            if videoFile['param']['Duration'] != None :
                duration = videoFile['param']['Duration']

            # 縮放
            vw = videoFile['width']
            vh = videoFile['height']

            if videoFile['param']['Resize'] != None :
                if videoFile['width'] > videoFile['param']['Resize'] :
                    vw = videoFile['param']['Resize']
                    vh = videoFile['height'] * ( videoFile['param']['Resize'] /  videoFile['width'] )

            # 產生 bitrate
            bitrate = str( videoFile['bitrate'] ) + 'k'
            if videoFile['param']['Size'] != None :
                bitrate = str( min( videoFile['bitrate'], round( videoFile['param']['Size'] / duration * 1000 * 8 ) ) ) + 'k'
            else :
                if videoFile['param']['Bitrate'] != None :
                    bitrate = str( videoFile['param']['Bitrate'] ) + 'k'

            # 產生指令
            command = [ ffmpegBinPath,
                    '-y',
                    '-hide_banner',
                    '-loglevel',       'panic',
                    '-i',               videoFile['filePath']
                ]

            # 取得水印
            if videoFile['param']['Watermark'] != None :
                size = str( vw ) + 'x' + str( vh )
                vf.append( '[1:v]scale=' + size + ' [ovrl], [0:v][ovrl]overlay=0:0' )
                command.extend([
                    '-i', videoFile['param']['Watermark']
                ])

            # 產生時間碼字幕
            if videoFile['param']['DisableTime'] == True :
                a = 1
            else :
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

                vf.append( 'subtitles='+ videoFile['subFile'] +':force_style=\'Fontsize=12,PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=0,Shadow=0,Alignment=3,MarginR=8\'' )

            # 產生 FPS
            if videoFile['param']['Framerate'] != None :

                # 分析原始
                frSrc = {
                    'i' : False,
                }

                if videoFile['framerate'][1] == 1001 :
                    frSrc[i] = True

                frDist = None

                # 分析參數
                while True :

                    frF1Match = re.search( r'^(\d+)$', str( videoFile['param']['Framerate'] ), flags = re.IGNORECASE )

                    if frF1Match != None :
                        if frSrc[i] == True :
                            frDist = frF1Match.group(0) + '000/1001'
                        else :
                            frDist = frF1Match.group(0) + '/1'

                        break

                    frF2Match = re.search( r'^(\d+.\d+)$', str( videoFile['param']['Framerate'] ), flags = re.IGNORECASE )
                    if frF2Match != None :
                        if frSrc[i] == True :
                            if frF2Match.group(0) in [ '23.976', '23.98' ] :
                                frDist = '24000/1001'
                            if frF2Match.group(0) in [ '29.97' ] :
                                frDist = '30000/1001'
                            if frF2Match.group(0) in [ '59.94' ] :
                                frDist = '60000/1001'
                            if frF2Match.group(0) in [ '119.88' ] :
                                frDist = '120000/1001'
                        else :
                            if frF2Match.group(0) in [ '23.976', '24.98' ] :
                                frDist =  '24/1'
                            if frF2Match.group(0) in [ '29.97' ] :
                                frDist =  '30/1'
                            if frF2Match.group(0) in [ '59.94' ] :
                                frDist =  '60/1'
                            if frF2Match.group(0) in [ '119.88' ] :
                                frDist = '120/1'
                        break
                    break

                if frDist != None :
                    vf.append('fps=fps=' + frDist )

            # FPS
            if videoFile['param']['Resize'] != None :
                vf.append( 'scale='+ str(videoFile['param']['Resize']) +':-2:flags=lanczos' )

            if len( vf ) > 0 :
                if videoFile['param']['Watermark'] == None :
                    command.extend([
                            '-vf', ','.join( vf ),
                            '-c:v',   encoder,
                        ])
                else :
                    command.extend([
                            '-filter_complex', ','.join( vf ),
                            '-c:v',             encoder,
                        ])
                command.extend([ '-preset', 'slow' ])

            command.extend([ '-b:v', bitrate ])

            if videoFile['param']['Cut'] != None :
                command.extend([
                    '-ss',   str( videoFile['param']['Cut']['start'] ),
                    '-t',    str( videoFile['param']['Cut']['len'] ),
                    # '-pass', '2'
                ])

            if videoFile['param']['AllowAudio'] != True :
                command.append('-an')

            command.append( videoFile['optPath'] )

            if DEBUG == True :
                print( ' '.join( command ) )

            pipeResult = subprocess.run(command, stdout = subprocess.PIPE)
            result = pipeResult.stdout.decode('utf-8')

            if DELSRT :
                if videoFile['param']['DisableTime'] == True :
                    a = 1
                else :
                    os.remove( videoFile['subFile']  )

        print( '' )

        break


    if len( videoList ) == 0 :
        print( '\n    找不到檔案。\n' )


    # 主流程結束
    break

print( '    ----------\n' )

if len( error ) > 0 :

    print( '  = 發生錯誤：\n' )

    for i in range( len( error ) ):
        print( '    ' + error[i] )

else :

    if len( videoList ) > 0 :
        print( '    執行完成，共處理 '+ str( len( videoList ) ) + ' 個檔案。' )


    else :
        print( '    執行完成，未處理任何檔案。' )


print( '' )
print( '    若您喜歡這個程式，歡迎分享；' )
print( '    若您的影片使用本程式產生，也歡迎在影片貼文加上 #gogojustice。' )
print( '' )

input('    請按 Enter 結束程式...')