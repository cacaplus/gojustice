# GoJustice 影片編輯助理

### 打字就能編輯影片！

有些攝影機，如 GoPro，無法在錄製的時候就加上時間戳記，若要另外進行剪輯、轉檔、浮水印、**加時間** 等，無論使用電腦還手機，都是既麻煩也沒效率。
因此我寫了 **GoJustice** 這個工具，只要在檔名上加好參數，就可以進行編輯。

如果您喜歡這個程式，可以稱讚一下我、可以 [請我一杯星巴克](https://p.ecpay.com.tw/06429)；  
若您的影片使用本程式產生，也歡迎在影片貼文加上標籤 `#gogojustice`。

* 版　本：0.981 (測試中)
* 首　頁：[GitHub](https://github.com/cacaplus/gojustice)
* 下載頁：[GitHub Release Page](https://github.com/cacaplus/gojustice/releases)

![輸出範例](https://caca.plus/project/gojustice/timestamp_sample_2.jpg)
上圖為輸出範例截圖，日期與時間皆為測試用，非實際發生時間。  
您也可以至 [YouTube](https://www.youtube.com/watch?v=PvK3Wrv6bQc) 瀏覽動態範本。


## 功能

**用檔名下參數** 就可以編輯影片，支援以下功能：

* 加上如行車紀錄器的時間戳記
* 剪下影片片段
* 影片縮放
* FPS 調整
* 加上圖片浮水印


**系統需求**

* Windows 7 32/64bit
* 使用 NVidia GPU、AMD GPU 與 Intel 較新的 CPU 會自動啟用硬體加速


**功能限制**

* 目前僅支援 PC。
* 目前沒有圖形介面。
* 目前不支援一鍵檢舉，以後也不會有。
* 可能會有 Bug，請多擔待。


## 安裝與設定

### A. 懶人包安裝法

1. **下載 GoJustice 執行檔**  
   前往 [Release](https://github.com/cacaplus/gojustice/releases) 下載最新版 `GoJustice` ，解壓縮到一個資料夾，如 `D:\GoJustice`。

2. **開始使用**


### B. 全自己來安裝

1. **安裝 Python** (Python 3.8)  
   請官方網站下載安裝包，安裝時請勾選 `Add Python 3.8 to PATH`

2. **下載 GoJustice 原始檔**  

3. **下載 ffmpeg**  
   前往 [官方網站](https://ffmpeg.org/) 下載；  
   Windows 版下載網址為 https://ffmpeg.zeranoe.com/builds/  
   將下載的 `ffmpeg` 壓縮檔 `bin` 資料夾中的所有檔案，解壓縮至 `GoJustice` 中的 `bin` 資料夾。


## 使用說明

1. 影片複製至 `input` 資料夾，依照需求修改檔名。

2. 點兩下 `GoJustice.exe`，進行轉檔作業。

3. **完成**。


**以下提供 3 種常用的情境說明用法：**

### A. 使用 GoPro 搭配 GoPro App，已抓出所需短片段，需加上時間戳記

1. 抓出的影片複製至 `input` 資料夾，**檔名前面的日期數字不要改**。
   
2. 點兩下 `GoJustice.exe`，進行轉檔作業。
   
3. 產生的影片檔將出現在 `output` 資料夾。

       GoPro 使用的是 UTC+0 時間，所以你會看到檔名比實際時間少了 8 小時。
       別擔心，程式會自動偵測是否為 GoPro 所拍攝，處理這個小問題。


### B. 直接從記憶卡取出檔案，已修剪完，需加上時間戳記

1. 將修剪後的影片複製至 `input` 資料夾。

2. 將檔名前端加上 **時間參數**，並視情況加上其他參數。
   
3. 點兩下，執行 `GoJustice.exe`，進行轉檔作業。

4. 產生的影片檔將出現在 `output` 資料夾。

### C. 直接從記憶卡取出檔案，需要修剪影片並加上時間戳記

1. 將修剪後的影片複製至 `input` 資料夾。

2. 將檔名前端加上 **時間參數**，並加上 **剪裁參數**。
   
3. 點兩下，執行 `GoJustice.exe`，進行轉檔作業。

4. 產生的影片檔將出現在 `output` 資料夾。


## 參數

### 參數速查表

|參數|位置|預設|功能
|--|--|--|--
|`[DATE]-[TIME]`  |開頭|不使用|設定影片字幕的時間，可接受多種格式
|**畫面編輯**
|`TR|TL|T`        |結尾|不使用|旋轉畫面，`TR` 為順時針轉90度；`TL` 為逆時針轉90度，`T` 為180度
|`FV|FH`          |結尾|不使用|翻轉影片，`FV` 為垂直翻轉；`FH` 為水平翻轉
|`CR[S]-[A]`      |結尾|不使用|裁切影片，`[S]` 為尺寸，格式如 `1600x900`；<br>`[A]` 為對齊，可使用 `N|S|W|E` （東南西北），如 `N`、`NW`。
|**時間編輯**
|`C[MMSS]L[S]`    |結尾|不使用|裁切，由影片時間 `[MMSS]` 開始，長度為 `[S]`；`S` 為`3-5`位數字，單位為 0.01 秒
|`C[MMSS]-[mmss]` |結尾|不使用|裁切，由影片時間 `[MMSS]` 開始至 `[mmss]` 結束。
|**畫面品質**
|`R[N]`           |結尾|不使用|以寬度設定影片大小，維持比例，如 `R1280` 為縮放成 `1280` 寬
|`F[N]`           |結尾|不使用|設定幀率（FPS），如 `F30` 可將 `120fps` 影片改為 `30fps`。
|`B[N][KM]`       |結尾|不使用|設定影片品質，如 `B8000K` 即為 `8000Kbps`；`B8M` 即為 `8Mbps`
|`S[N]M`          |結尾|不使用|設定目標影片大小，如 `S30M` 即為目標檔案大小 `30MB`。
|**其他**
|`W[N]`           |結尾|不使用|圖片浮水印，支援 `PNG`
|`A`              |結尾|不使用|輸出時包含聲音，預設不使用。


### 參數使用範例

1. **日期與參數**  
   檔名最前為日期，日期可接受多種格式：

       20200701_001245000.mp4  
       # GoPro App 匯出的自動檔名，時間會少 8 小時
       # Gojustice 會自動加回來所以不用改

       20200701_081245.mp4
       20200701-081245.mp4     # 中間用底線或減號都可以
       0701_081245.mp4
       0701-081245.mp4         # 今年的影片可以不用寫年，但需自行注意跨年度的問題

2. **其他參數**

   位於檔名尾端，以 `_@` 開始，每個參數以 `,`（逗點）分隔，如：
   
       20200701_081245_TP_AAA-0001_@A,C0135L510.mp4 
   
   意思為：  
   * `A`：保留影片聲音；
   * `C:0135,510`：從影片 `1:35` 處剪 `5.10` 秒出來；
   * 中間可以加上車牌等資訊。

   點選輸出後，會在 `output` 資料夾看到以下檔案：

       20200701_081245_TP_AAA-0001.mp4

   參數的部分會移除，並會在檔名加上 `.ts` 作為辨識用途。

3. **修剪**  
   提供兩種修剪方式如下：

   如要剪出從 `01:35` 開始的 `5.1` 秒，參數格式為 `C0135L051`，如：  
   
       20200701_081245_@C0135L510.mp4

   如要剪出從 `01:35` 到 `01:45` 秒，參數格式為 `C0135-0145`，如：  

       20200701_081245_@C0135-0145.mp4

4. **位元率**  
   若要設定影像位元率，使用 `B[N]K` 或是 `B[N]M`，如：  
   
       20200701_081245_@B1M.mp4
       20200701_081245_@B1000K.mp4  # 這兩個設定結果是相同的。

   預設為與原始影片相同；若設定值高於原始影片，則會與原始影片相同。

5. **目標大小**  
   若要設定目標影片大小，則使用 `S[N]M`，如：  
   
       20200701_081245_@S30M.mp4

   表示目標轉出來的檔案約 `30MB`，這個數值不可能精準。

       若同時設定位元率與目標大小，則以目標大小為主。

6. **浮水印**  
    支援 `PNG` 格式，會自動放大到與影片同尺寸；  
    檔案需放在 `watermark` 資料夾內，檔名以 `W` 開頭，如：  
   
       20200701_081245_@W1.mp4

7. **聲音**  
   預設狀態下會移除聲音，若需要保留聲音，參數為 `A`，如：  
   
       20200701_081245_@A.mp4


## 注意事項

1. 轉檔過程需要用到大量運算資源，請避免執行重要的運算工作。
   
2. 轉檔過程會產生暫存檔，轉完會自己刪掉。
   
3. 指定容量不會太精確，系統會自動打 95 折。


## 建議的錄影設定

1. 晴天使用最高 `2.5K 60p` 即可，騎不快的話，用 `30p` 就好了。越高的 `FPS` 需要越高的位元率，同品質的畫面畫質就需要越高的儲存空間。

2. 傍晚時間的檢舉需要技巧，不然調多少都沒用。


## 之後有時間會繼續做的

1. 更細的設定檔

2. 更好的轉檔品質

3. 提供其他平台的版本

4. 使用暴力法覆蓋錯誤的時間


## 注意事項

* 如果你在使用時遇到問題，請把出問題的順序跟檔案一起給我。
  
* 因為我沒有 Mac，所以目前沒辦法直接提供 Mac 上的狀態，但程式理論上小修改是可以執行的。


## 授權方式

* 本程式 **永遠免費**，且不會以任何方式向使用者收費。

* 為確保資訊安全，所有分享請連結回首頁下載。

* 本程式不開放改作，開放原始碼僅是證明不含惡意程式。
