# GoJustice 影片時間戳記助手

**GoJustice Video Timestamp Helper**

台灣的交通環境是個悲劇，從道路品質、道路規劃到用路人水準。許多車友會使用行車紀錄器自保，但有些機種並不會自動加上時間戳記，造成檢舉時的巨大問題。因此我寫了這個小工具，讓正義夥伴們有個快速好用的工具可以補上時間戳記。


## 主要功能

1. 批次將影片加上時間戳記。


### 細部功能

1. 以檔案名稱作為設定，方便快速作業。
2. 可設定起始時間。
3. 可裁切影片。
4. 自動縮小檔案。


### 限制

1. 目前僅支援 PC。
2. 目前沒有圖形介面。
3. 目前不支援一鍵檢舉，以後也不會有。


## 安裝與設定

### A. 懶人包安裝法

1. 前往 [Release](https://github.com/cacaplus/gojustice/releases) 分頁中下載最新的懶人包，解壓縮後就可以使用。

### B. 全自己來安裝

1. **安裝 Python** (Python 3.8)  
   請官方網站下載安裝包，安裝時請勾選 `Add Python 3.8 to PATH`

2. **安裝 Python Lib**  
   
       pip install pytz  
       pip install python-dateutil

3. **安裝 GoJustice**  
   下載並解壓縮 `GoJustice` 到一個資料夾，如 `C:\GoJustice`。

4. **安裝 ffmpeg**  
   前往 [官方網站](https://ffmpeg.org/) 下載；  
   Windows 版下載網址為 https://ffmpeg.zeranoe.com/builds/  
   將下載的 `ffmpeg` 壓縮檔 `bin` 資料夾中的所有檔案，解壓縮至 `GoJustice` 中的 `bin` 資料夾。


## 使用說明

1. 將原始影片複製至 `GoJustice/input` 資料夾。

2. 視需求將檔名加上設定參數。

3. 點兩下，執行 `GoJustice.py` 主執行檔，會跑出命令提示字元的黑框。

4. 命令提示字元的黑框將顯示目前的轉檔狀態。

5. 加上日期的影片檔將會出現在 `GoJustice/output` 資料夾。


## 設定轉檔參數

1. 使用 GoPro App 轉出的檔案不需要任何設定，將 **直接** 押上時間戳記。

2. 非 GoPro App 轉出的檔案，需要在檔案名稱前加上日期，檔案名稱後加上參數設定。  
   輸出的檔案將會移除檔名參數的部分。


### 設定範例

#### A. 啟動

1. **日期**  
   檔名最前為日期，格式為 `YYYYMMDD_HHMMSS` 或 `MMDD_HHMMSS`；  

   如以下範例：  

       20200701_081245_TP_AAA-0001.mp4  
       0701_081245_TP_AAA-0001.mp4

2. **參數**  
   位於檔名尾端，以 `_@` 開始，每個參數以 `,`（逗點）分隔，如：
   
       0701_081245_TP_AAA-0001_@A,C0135,510.mp4 
   
   意思為：  
   * 影片開始時間為今年的 7/1 日，早上8點12分45秒；
   * `A`：保留影片聲音；
   * `C:0135,510`：從影片 `1:35` 處剪 `5.10` 秒出來；

3. **修剪**  
   提供兩種修剪方式如下：

   如要剪出從 `01:35` 開始的 `5.1` 秒，參數格式為 `C0135:051`，如：  
   
       0701_081245_TP_AAA-0001_@C0135:510.mp4

   如要剪出從 `01:35` 到 `01:45` 秒，參數格式為 `C0135-0145`，如：  

       0701_081245_TP_AAA-0001_@C0135-0145.mp4

4. **聲音**  
   預設狀態下會移除聲音，若需要保留聲音，參數為 `A`，如：  
   
       0701_081245_TP_AAA-0001_@A.mp4


### 參數表

<div class="spec">

|參數|預設|功能
|--|--|--
|`A`              |不使用|輸出時包含聲音，預設不使用。
|`C[MMSS]:[SSS]`  |不使用|裁切，由影片時間 `[MMSS]` 開始，長度為 `[SSS]`；`SSS` 單位為 0.1 秒
|`C[MMSS]:[SSSS]` |不使用|裁切，由影片時間 `[MMSS]` 開始，長度為 `[SSSS]`；`SSSS` 單位為 0.01 秒
|`C[MMSS]-[mmss]` |不使用|裁切，由影片時間 `[MMSS]` 開始至 `[mmss]` 結束。
|`B[N][KM]`       |不使用|手動影片品質，如 `B8000K` 即為 `8000Kbps`；`B8M` 即為 `8Mbps`
|`S[N]M`          |`S30M`|手動設定目標影片大小，如 `S30M` 即為目標檔案大小 `30MB`。<br>以最小氣的台北市標準為預設值。
|`R[N]`           |不使用|手動設定影片大小，如 `R1920` 為輸出時縮放至寬 `1920`。
|`F[N]`           |不使用|手動設定影片FPS，如 `F30` 為輸出時將 FPS 調整為 `30`。

</div>


## 注意事項

1. 轉檔過程需要用到大量 CPU，請避免執行重要的運算工作。
   
2. 轉檔過程會產生暫存檔，轉完會自己刪掉。


## 建議的錄影設定

1. 晴天使用最高 `2.5K 60p` 即可，騎不快的話，用 `30p` 就好了。越高的 FPS 需要越高的位元率，同品質的畫質當然就需要越高的儲存空間。

2. 傍晚時間的檢舉需要技巧，不然調多少都沒用。


## 之後有時間會改善的

1. 更細的設定檔

2. 浮水印

3. 更好的轉檔品質

4. 提供其他平台的版本

5. 使用暴力法覆蓋錯誤的時間



## 注意事項

* 因為我沒有 GoPro，如果你在使用時遇到問題，請把出問題的順序跟檔案一起給我。