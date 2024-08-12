## 資料夾說明
* azure_projrct > deployment.py與azure的串接
* azure_projrct > settings.py 與linebot的串接
* azure_projrct > urls.py 設定linebot回話的callback以及api串接路徑
* firstapp > views.py  主要撰寫每個圖文選單的按鈕回覆以及偵測到關鍵字後呼叫func裡面的相對動作
* firstapp > module > func.py 撰寫每個按鈕即收到關鍵字後的動作，如呼叫圖片、選單等
* firstapp > module > models.py 定義Django模型，用於管理和儲存應用程式中的各種資料
* module > admin.py 設定和註冊模型的管理界面，以便在Django管理後台中對應用程式的資料進行管理
