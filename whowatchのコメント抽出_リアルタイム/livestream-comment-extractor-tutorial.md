# Pythonを使ったライブストリームコメント抽出ツール作成ガイド

## はじめに

このチュートリアルでは、Python と Selenium を使用して、whowatch.tv などのライブストリーミングプラットフォームから自動的にコメントを抽出するツールを作成する方法を段階的に学びます。初心者にもわかりやすいよう、各ステップで具体的な説明とコードを提供します。

## 目次

1. [必要な環境とライブラリのセットアップ](#1-必要な環境とライブラリのセットアップ)
2. [基本的なプロジェクト構造の作成](#2-基本的なプロジェクト構造の作成)
3. [ブラウザを起動してページにアクセスする](#3-ブラウザを起動してページにアクセスする)
4. [ヘッドレスモードの設定](#4-ヘッドレスモードの設定)
5. [コメント領域の特定](#5-コメント領域の特定)
6. [すべてのコメントを抽出（シンプルバージョン）](#6-すべてのコメントを抽出シンプルバージョン)
7. [ユーザー名とコメント内容を分離](#7-ユーザー名とコメント内容を分離)
8. [CSVファイルに保存する](#8-csvファイルに保存する)
9. [継続的にコメントを監視する](#9-継続的にコメントを監視する)
10. ["stale element reference"問題の対策](#10-stale-element-reference問題の対策)
11. [コマンドライン引数の追加](#11-コマンドライン引数の追加)
12. [結果の分析と統計情報の表示](#12-結果の分析と統計情報の表示)
13. [完成版コード](#13-完成版コード)
14. [使用方法](#14-使用方法)
15. [さらなる学習のためのチャレンジ](#15-さらなる学習のためのチャレンジ)

## 1. 必要な環境とライブラリのセットアップ

まず、必要なライブラリをインストールし、基本の環境を整えましょう。

```bash
pip install selenium webdriver-manager pandas
```

これらのライブラリの役割は：
- `selenium`: Webブラウザを自動操作するためのライブラリ
- `webdriver-manager`: Seleniumで使用するドライバーを自動で管理
- `pandas`: データ分析と処理のためのライブラリ

## 2. 基本的なプロジェクト構造の作成

```python
# whowatch_comment_extractor.py
# ライブラリのインポート
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    print("ライブストリームコメント抽出ツール")
    
if __name__ == "__main__":
    main()
```

このシンプルな構造から始めて、徐々に機能を追加していきます。

## 3. ブラウザを起動してページにアクセスする

まず、Seleniumを使ってブラウザを操作する基本部分を実装します。

```python
# whowatch_comment_extractor.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():
    # ブラウザの設定
    print("ブラウザを設定中...")
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    # ChromeDriverの設定
    service = Service(ChromeDriverManager().install())
    
    # ブラウザを起動
    print("ブラウザを起動中...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Whowatchページにアクセス
    url = "https://whowatch.tv/viewer/61932105"
    print(f"{url} にアクセス中...")
    driver.get(url)
    
    # ページが完全に読み込まれるまで待機
    time.sleep(5)
    
    # ページタイトルを取得して表示
    title = driver.title
    print(f"ページタイトル: {title}")
    
    # ページのHTMLを取得
    html = driver.page_source
    print(f"HTML取得成功！ 長さ: {len(html)}文字")
    
    # ブラウザを閉じる
    print("ブラウザを閉じています...")
    driver.quit()
    
if __name__ == "__main__":
    main()
```

**Seleniumの基本概念**:
- `Options()`: ブラウザの設定をカスタマイズします
- `Service()`: WebDriverのサービスを管理します
- `webdriver.Chrome()`: Chromeブラウザのインスタンスを作成します
- `driver.get(url)`: 指定したURLにアクセスします
- `driver.page_source`: ページのHTML全体を取得します

## 4. ヘッドレスモードの設定

Webブラウザを表示せずにバックグラウンドで実行する「ヘッドレスモード」を設定します。これはサーバー環境での実行や、リソース節約に役立ちます。

```python
# ブラウザの設定を修正
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")

# ヘッドレスモードを有効化（ブラウザウィンドウを表示しない）
print("ヘッドレスモードを有効化...")
chrome_options.add_argument("--headless")

# ヘッドレスモードで必要な追加設定
chrome_options.add_argument("--disable-gpu")  # GPUハードウェアアクセラレーションを無効化
chrome_options.add_argument("--no-sandbox")   # サンドボックスを無効化
chrome_options.add_argument("--disable-dev-shm-usage")  # 共有メモリの使用を無効化
```

**ヘッドレスモードの利点と注意点**:

- **利点**:
  - リソース効率が良い（メモリとCPU使用量が少ない）
  - バックグラウンドで実行できる
  - 通常より高速に動作することが多い

- **注意点**:
  - デバッグが難しい（画面が見えない）
  - ボットとして検出されやすい（CAPTCHA対策が必要）
  - 一部のウェブサイトでは正常に動作しないことがある

## 5. コメント領域の特定

次に、ページ内のコメント領域を特定します。この段階では、開発者ツールを使って要素を調査する方法を学びます。

```python
# whowatch_comment_extractor.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():
    # 前のコードと同じ
    # ...
    
    # Whowatchページにアクセス
    url = "https://whowatch.tv/viewer/61932105"
    print(f"{url} にアクセス中...")
    driver.get(url)
    
    # コメント領域を探す
    print("コメント領域を検索中...")
    try:
        # 明示的な待機：コメント領域が表示されるまで最大10秒待つ
        comment_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.pc-comments.live-viewer"))
        )
        print("コメント領域を発見しました！")
        
        # コメント領域の情報を表示
        print(f"コメント領域のサイズ: 幅={comment_area.size['width']}px, 高さ={comment_area.size['height']}px")
        print(f"コメント領域のテキスト（一部）: {comment_area.text[:100]}...")
        
    except Exception as e:
        print(f"コメント領域の検出に失敗しました: {e}")
    
    # ブラウザを閉じる
    driver.quit()
```

**新しい概念**:
- `WebDriverWait`: 特定の条件が満たされるまで待機する機能
- `By.CSS_SELECTOR`: CSSセレクタを使って要素を検索する方法
- `EC.presence_of_element_located`: 要素が存在するかどうかをチェックする条件

**開発者ツールでの要素の調査方法**:
1. Chrome上で右クリック→「検証」を選択
2. 要素の上でマウスを動かし、コメント領域を特定
3. HTML内の対応する要素を確認し、CSSセレクタを特定

## 6. すべてのコメントを抽出（シンプルバージョン）

次に、コメント領域内のすべてのコメントを抽出します。まずはシンプルに、見つかったすべてのコメントを表示します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）

def main():
    # 前のコードと同じ
    # ...
    
    try:
        # コメント領域を見つける
        comment_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.pc-comments.live-viewer"))
        )
        print("コメント領域を発見しました！")
        
        # コメント要素をすべて取得
        print("コメントを検索中...")
        comment_elements = comment_area.find_elements(By.CSS_SELECTOR, "[class*='comment-item']")
        print(f"合計 {len(comment_elements)} 件のコメントを見つけました")
        
        # 各コメントの情報を表示
        for i, comment in enumerate(comment_elements):
            print(f"\nコメント #{i+1}:")
            print(f"テキスト: {comment.text}")
            print(f"HTML: {comment.get_attribute('outerHTML')[:100]}...")
            
            # 少し待機して、ブラウザの負荷を減らす
            time.sleep(0.5)
            
    except Exception as e:
        print(f"エラー: {e}")
    
    # ブラウザを閉じる
    driver.quit()
```

**新しい概念**:
- `find_elements`: 複数の要素を検索する方法
- `[class*='comment-item']`: クラス名に特定の文字列を含む要素を検索するCSSセレクタ
- `element.text`: 要素のテキスト内容を取得
- `element.get_attribute('outerHTML')`: 要素のHTML全体を取得

## 7. ユーザー名とコメント内容を分離

コメント要素から、ユーザー名とコメント本文を分離して抽出します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）

def main():
    # 前のコードと同じ
    # ...
    
    try:
        # コメント領域を見つける
        comment_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.pc-comments.live-viewer"))
        )
        
        # コメント要素をすべて取得
        comment_elements = comment_area.find_elements(By.CSS_SELECTOR, "[class*='comment-item']")
        print(f"合計 {len(comment_elements)} 件のコメントを見つけました")
        
        # 各コメントからユーザー名とコメント内容を抽出
        for i, comment in enumerate(comment_elements):
            try:
                # ユーザー名を探す
                username = "不明"
                try:
                    # 複数のセレクタを試す（より堅牢なアプローチ）
                    selectors = ["[class*='username']", "[class*='user-name']", "[class*='author']"]
                    for selector in selectors:
                        try:
                            username_elem = comment.find_element(By.CSS_SELECTOR, selector)
                            username = username_elem.text.strip()
                            if username:
                                break
                        except:
                            continue
                except:
                    pass
                
                # コメントテキストを探す
                comment_text = ""
                try:
                    selectors = ["[class*='comment-text']", "[class*='message']", "[class*='content']"]
                    for selector in selectors:
                        try:
                            text_elem = comment.find_element(By.CSS_SELECTOR, selector)
                            comment_text = text_elem.text.strip()
                            if comment_text:
                                break
                        except:
                            continue
                except:
                    pass
                
                # コメントが空の場合、要素全体のテキストを使用
                if not comment_text:
                    full_text = comment.text.strip()
                    # ユーザー名部分を除外
                    if username != "不明" and username in full_text:
                        comment_text = full_text.replace(username, "", 1).strip()
                    else:
                        comment_text = full_text
                
                print(f"コメント #{i+1}: {username} - {comment_text}")
                
            except Exception as e:
                print(f"コメント #{i+1} の処理中にエラー: {e}")
            
    except Exception as e:
        print(f"エラー: {e}")
    
    # ブラウザを閉じる
    driver.quit()
```

**新しい概念**:
- 複数のセレクタを試すことで、ページの変更に強いコードにする
- テキスト処理によるユーザー名とコメントの分離
- 各コメント要素に対するエラー処理

## 8. CSVファイルに保存する

抽出したコメントをCSVファイルに保存する機能を追加します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）
import csv
from datetime import datetime

def main():
    # ブラウザの設定と起動
    # ...
    
    # CSVファイルの準備
    output_file = "comments.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'コメント'])
        
        try:
            # コメント領域を見つける
            # ...
            
            # 各コメントからユーザー名とコメント内容を抽出
            for i, comment in enumerate(comment_elements):
                try:
                    # ユーザー名とコメントの抽出（前のコードと同じ）
                    # ...
                    
                    # CSVに書き込む
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([timestamp, username, comment_text])
                    
                    print(f"コメント #{i+1}: {username} - {comment_text}")
                    
                except Exception as e:
                    print(f"コメント #{i+1} の処理中にエラー: {e}")
                
        except Exception as e:
            print(f"エラー: {e}")
        
        print(f"コメントを {output_file} に保存しました")
    
    # ブラウザを閉じる
    driver.quit()
```

**新しい概念**:
- `csv.writer`: CSVファイルに書き込むためのオブジェクト
- `writer.writerow()`: CSVに1行書き込む
- `datetime.now()`: 現在の日時を取得

## 9. 継続的にコメントを監視する

一定時間、継続的にコメントを監視し、新しいコメントのみを抽出する機能を追加します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）

def extract_comments(url, duration_minutes=5, output_file="comments.csv"):
    # ブラウザの設定
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print(f"{url} からコメントを {duration_minutes}分間 抽出します...")
    
    # CSVファイルの準備
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'コメント'])
        
        # 前回取得したコメントを記録するセット
        previous_comments = set()
        total_comments = 0
        
        try:
            # URLにアクセス
            driver.get(url)
            
            # コメント領域が表示されるまで待機
            print("コメント領域を検索中...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.pc-comments.live-viewer"))
            )
            print("コメント領域を発見しました！")
            
            # 終了時間を計算
            end_time = time.time() + (duration_minutes * 60)
            
            # メインループ
            while time.time() < end_time:
                try:
                    # コメント領域を取得
                    comment_area = driver.find_element(By.CSS_SELECTOR, "div.pc-comments.live-viewer")
                    
                    # コメント要素を取得
                    comment_elements = comment_area.find_elements(By.CSS_SELECTOR, "[class*='comment-item']")
                    
                    # 新しいコメントをカウント
                    new_comments = 0
                    
                    # 各コメントを処理
                    for comment in comment_elements:
                        try:
                            # ユーザー名とコメントの抽出（前のコードと同じ）
                            username = "不明"
                            try:
                                selectors = ["[class*='username']", "[class*='user-name']", "[class*='author']"]
                                for selector in selectors:
                                    try:
                                        username_elem = comment.find_element(By.CSS_SELECTOR, selector)
                                        username = username_elem.text.strip()
                                        if username:
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            comment_text = ""
                            try:
                                selectors = ["[class*='comment-text']", "[class*='message']", "[class*='content']"]
                                for selector in selectors:
                                    try:
                                        text_elem = comment.find_element(By.CSS_SELECTOR, selector)
                                        comment_text = text_elem.text.strip()
                                        if comment_text:
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            if not comment_text:
                                full_text = comment.text.strip()
                                if username != "不明" and username in full_text:
                                    comment_text = full_text.replace(username, "", 1).strip()
                                else:
                                    comment_text = full_text
                            
                            # 空のコメントはスキップ
                            if not comment_text:
                                continue
                            
                            # ユニークな識別子を作成
                            comment_id = f"{username}:{comment_text}"
                            
                            # 新しいコメントのみを処理
                            if comment_id not in previous_comments:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                writer.writerow([timestamp, username, comment_text])
                                file.flush()  # すぐにファイルに書き込む
                                previous_comments.add(comment_id)
                                new_comments += 1
                                total_comments += 1
                                print(f"{timestamp} - {username}: {comment_text}")
                                
                        except Exception as e:
                            print(f"コメント処理エラー: {e}")
                    
                    # 新しいコメントの数を表示
                    if new_comments > 0:
                        print(f"{new_comments}件の新しいコメントを検出しました。合計: {total_comments}件")
                    
                    # ページをスクロールして新しいコメントを表示（オプション）
                    try:
                        driver.execute_script("arguments[0].scrollTop = 0;", comment_area)
                    except:
                        pass
                    
                except Exception as e:
                    print(f"エラー: {e}")
                
                # 次のチェックまで待機
                time.sleep(3)
                
            print(f"\n抽出完了！合計{total_comments}件のコメントを {output_file} に保存しました")
            
        finally:
            # ブラウザを閉じる
            driver.quit()
    
    return total_comments

def main():
    # テスト用にコメント抽出関数を呼び出す
    url = "https://whowatch.tv/viewer/61932105"
    extract_comments(url, duration_minutes=1)

if __name__ == "__main__":
    main()
```

**新しい概念**:
- メインループによる継続的な監視
- `set()`を使った重複コメントの検出
- `file.flush()`による即時書き込み
- Timeoutベースの実行時間制御

## 10. "stale element reference"問題の対策

この段階で、「stale element reference」というエラーが発生する可能性があります。これは、DOM要素がページの更新によって古くなった場合に発生します。これを解決するためにJavaScriptを使用します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）
from selenium.common.exceptions import StaleElementReferenceException

def extract_comments(url, duration_minutes=5, output_file="comments.csv"):
    # 前のコードと同じ
    # ...
    
    # メインループ内のコメント抽出部分を修正
    while time.time() < end_time:
        try:
            # コメント領域を毎回取得し直す
            comment_area = driver.find_element(By.CSS_SELECTOR, "div.pc-comments.live-viewer")
            
            # JavaScriptを使ってコメントデータを抽出（stale element対策）
            driver.execute_script("""
            (function() {
                // メモリにコメントデータを保存
                window.commentData = [];
                var commentContainer = document.querySelector("div.pc-comments.live-viewer");
                if (!commentContainer) return;
                
                // 複数のセレクタを試す
                var commentElements = commentContainer.querySelectorAll(".comment-item");
                if (!commentElements || commentElements.length === 0) {
                    commentElements = commentContainer.querySelectorAll("[class*='comment-item']");
                }
                if (!commentElements || commentElements.length === 0) {
                    commentElements = commentContainer.querySelectorAll("[class*='comment']");
                }
                
                // 各コメント要素から情報を抽出
                for (var i = 0; i < commentElements.length; i++) {
                    var element = commentElements[i];
                    
                    // ユーザー名の抽出
                    var username = "不明";
                    var usernameSelectors = ["[class*='username']", "[class*='user-name']", "[class*='author']"];
                    for (var j = 0; j < usernameSelectors.length; j++) {
                        var usernameElem = element.querySelector(usernameSelectors[j]);
                        if (usernameElem && usernameElem.textContent.trim()) {
                            username = usernameElem.textContent.trim();
                            break;
                        }
                    }
                    
                    // コメントテキストの抽出
                    var commentText = "";
                    var commentSelectors = ["[class*='comment-text']", "[class*='message']", "[class*='content']"];
                    for (var k = 0; k < commentSelectors.length; k++) {
                        var commentElem = element.querySelector(commentSelectors[k]);
                        if (commentElem && commentElem.textContent.trim()) {
                            commentText = commentElem.textContent.trim();
                            break;
                        }
                    }
                    
                    // コメントが空の場合、要素全体のテキストを使用
                    if (!commentText) {
                        var fullText = element.textContent.trim();
                        if (username !== "不明" && fullText.includes(username)) {
                            commentText = fullText.replace(username, "").trim();
                        } else {
                            commentText = fullText;
                        }
                    }
                    
                    // 結果を保存
                    if (commentText) {
                        window.commentData.push({
                            username: username,
                            comment: commentText
                        });
                    }
                }
            })();
            """)
            
            # JavaScriptから結果を取得
            comment_data = driver.execute_script("return window.commentData;")
            
            new_comments = 0
            
            if comment_data:
                for item in comment_data:
                    username = item.get('username', '不明')
                    comment_text = item.get('comment', '')
                    
                    # 空のコメントはスキップ
                    if not comment_text:
                        continue
                    
                    # ユニークな識別子を作成
                    comment_id = f"{username}:{comment_text}"
                    
                    # 新しいコメントのみを処理
                    if comment_id not in previous_comments:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow([timestamp, username, comment_text])
                        file.flush()  # すぐにファイルに書き込む
                        previous_comments.add(comment_id)
                        new_comments += 1
                        total_comments += 1
                        print(f"{timestamp} - {username}: {comment_text}")
            
            # 残りのコードは同じ
            # ...
    
        except Exception as e:
            print(f"エラー: {e}")
        
        # 次のチェックまで待機
        time.sleep(3)
```

**新しい概念**:
- `execute_script()`: ブラウザでJavaScriptを実行する
- JavaScriptでDOMを操作して要素から情報を抽出する
- ブラウザのメモリに一時的にデータを保存する
- PytonからJavaScriptの結果を取得する

## 11. コマンドライン引数の追加

スクリプトをより柔軟に使えるように、コマンドライン引数を追加します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）
import argparse

# extract_comments関数は同じ

def main():
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='Whowatchライブストリームからコメントを抽出するツール')
    parser.add_argument('url', help='抽出対象のWhowatchライブストリームURL')
    parser.add_argument('-t', '--time', type=int, default=10, 
                        help='抽出時間（分）。デフォルトは10分')
    parser.add_argument('-o', '--output', default='whowatch_comments.csv',
                        help='出力CSVファイル名。デフォルトはwhowatch_comments.csv')
    parser.add_argument('--headless', action='store_true',
                        help='ヘッドレスモードで実行（ブラウザウィンドウを表示しない）')
    
    # 引数を解析
    args = parser.parse_args()
    
    # 引数から値を取得
    target_url = args.url
    duration_min = args.time
    output_file = args.output
    headless_mode = args.headless
    
    # コメント抽出を実行
    extract_comments(target_url, duration_min, output_file, headless_mode)

if __name__ == "__main__":
    main()
```

**新しい概念**:
- `argparse`: コマンドライン引数を処理するためのモジュール
- パラメータの型指定と説明
- デフォルト値の設定
- ブール値フラグの設定（`--headless`）

## 12. 結果の分析と統計情報の表示

最後に、抽出したコメントの基本的な分析と統計情報を表示します。

```python
# whowatch_comment_extractor.py
# （前のインポートに加えて）
import os
import pandas as pd

def extract_comments(url, duration_minutes=5, output_file="comments.csv", headless=False):
    # 前のコードと同じ
    # ...
    
    # 最後に結果の分析を追加
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        df = pd.read_csv(output_file)
        print("\n=== 抽出結果の概要 ===")
        print(f"合計コメント数: {len(df)}")
        if not df.empty:
            print(f"ユニークユーザー数: {df['ユーザー名'].nunique()}")
            print(f"最初のコメント時間: {df['タイムスタンプ'].iloc[0]}")
            print(f"最後のコメント時間: {df['タイムスタンプ'].iloc[-1]}")
            print("\n最初の5件のコメント:")
            print(df.head(5)[['タイムスタンプ', 'ユーザー名', 'コメント']])
            
            # トップユーザーの表示
            print("\n最もコメントの多いユーザー（上位5名）:")
            top_users = df['ユーザー名'].value_counts().head(5)
            for user, count in top_users.items():
                print(f"{user}: {count}件")
    
    return total_comments
```

**新しい概念**:
- `pandas`を使ったデータ分析
- データフレームの基本操作（`head()`、`nunique()`など）
- `value_counts()`を使った頻度集計

## 13. 完成版コード

以下が、すべてのステップを統合した完全なコードです：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whowatchライブストリームコメント抽出ツール
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import pandas as pd
from datetime import datetime
import os
import argparse

def extract_comments(url, duration_minutes=10, output_file="whowatch_comments.csv", headless=False):
    """
    指定したWhowatchのURLからコメントを抽出する
    
    Parameters:
        url (str): WhowatchのライブストリームURL
        duration_minutes (int): 抽出を実行する時間（分）
        output_file (str): 出力するCSVファイル名
        headless (bool): ヘッドレスモードを使用するかどうか
    
    Returns:
        int: 抽出したコメントの総数
    """
    print("コメント抽出を開始します...")
    print(f"対象URL: {url}")
    print(f"実行時間: {duration_minutes}分")
    print(f"出力ファイル: {output_file}")
    print(f"ヘッドレスモード: {'有効' if headless else '無効'}")
    
    # Chromeの設定
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    
    # ヘッドレスモードの設定
    if headless:
        print("ヘッドレスモードで実行します（ブラウザ画面は表示されません）")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    # ChromeDriverの自動インストールとサービスの設定
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # CSVファイルを準備
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'コメント'])
        
        # 前回取得したコメントを記録するセット
        previous_comments = set()
        
        try:
            # URLにアクセス
            driver.get(url)
            print("ページにアクセスしました。コメント領域を探しています...")
            
            # まずコメント領域が表示されるまで待機（最大20秒）
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.pc-comments.live-viewer"))
                )
                print("コメント領域を検出しました！")
            except Exception as e:
                print(f"コメント領域の検出に失敗しました: {str(e)}")
                print("別のセレクタで試行します...")
                
                # 代替のセレクタを試してみる
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='comment']"))
                    )
                    print("代替セレクタでコメント領域を検出しました！")
                except Exception as e2:
                    print(f"代替セレクタでも検出できませんでした: {str(e2)}")
                    print("ページのHTMLを確認してください。")
                    return 0
            
            # 指定時間（デフォルト10分）実行
            end_time = time.time() + (duration_minutes * 60)
            total_comments = 0
            
            print(f"コメントの抽出を開始します。{duration_minutes}分間実行します...")
            
            while time.time() < end_time:
                try:
                    # コメント領域を毎回取得し直す (stale element対策)
                    comment_container = driver.find_element(By.CSS_SELECTOR, "div.pc-comments.live-viewer")
                    
                    # コメント要素をリスト化する前に処理
                    comment_html = comment_container.get_attribute('innerHTML')
                    
                    # コメント要素の取得と処理を1つのトランザクションにする
                    driver.execute_script("""
                    (function() {
                        // メモリにコメントデータを保存
                        window.commentData = [];
                        var commentContainer = document.querySelector("div.pc-comments.live-viewer");
                        if (!commentContainer) return;
                        
                        // 複数のセレクタを試す
                        var commentElements = commentContainer.querySelectorAll(".comment-item");
                        if (!commentElements || commentElements.length === 0) {
                            commentElements = commentContainer.querySelectorAll("[class*='comment-item']");
                        }
                        if (!commentElements || commentElements.length === 0) {
                            commentElements = commentContainer.querySelectorAll("[class*='comment']");
                        }
                        
                        // 各コメント要素から情報を抽出
                        for (var i = 0; i < commentElements.length; i++) {
                            var element = commentElements[i];
                            
                            // ユーザー名の抽出
                            var username = "不明";
                            var usernameSelectors = ["[class*='username']", "[class*='user-name']", "[class*='author']"];
                            for (var j = 0; j < usernameSelectors.length; j++) {
                                var usernameElem = element.querySelector(usernameSelectors[j]);
                                if (usernameElem && usernameElem.textContent.trim()) {
                                    username = usernameElem.textContent.trim();
                                    break;
                                }
                            }
                            
                            // コメントテキストの抽出
                            var commentText = "";
                            var commentSelectors = ["[class*='comment-text']", "[class*='message']", "[class*='content']"];
                            for (var k = 0; k < commentSelectors.length; k++) {
                                var commentElem = element.querySelector(commentSelectors[k]);
                                if (commentElem && commentElem.textContent.trim()) {
                                    commentText = commentElem.textContent.trim();
                                    break;
                                }
                            }
                            
                            // コメントが空の場合、要素全体のテキストを使用
                            if (!commentText) {
                                var fullText = element.textContent.trim();
                                if (username !== "不明" && fullText.includes(username)) {
                                    commentText = fullText.replace(username, "").trim();
                                } else {
                                    commentText = fullText;
                                }
                            }
                            
                            // 結果を保存
                            if (commentText) {
                                window.commentData.push({
                                    username: username,
                                    comment: commentText
                                });
                            }
                        }
                    })();
                    """)
                    
                    # JavaScriptから結果を取得
                    comment_data = driver.execute_script("return window.commentData;")
                    
                    new_comments_count = 0
                    
                    if comment_data:
                        for item in comment_data:
                            username = item.get('username', '不明')
                            comment_text = item.get('comment', '')
                            
                            # 空のコメントはスキップ
                            if not comment_text:
                                continue
                            
                            # ユニークな識別子を作成
                            comment_id = f"{username}:{comment_text}"
                            
                            # 新しいコメントのみを処理
                            if comment_id not in previous_comments:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                writer.writerow([timestamp, username, comment_text])
                                file.flush()  # すぐにファイルに書き込む
                                previous_comments.add(comment_id)
                                new_comments_count += 1
                                total_comments += 1
                                print(f"{timestamp} - {username}: {comment_text}")
                    
                    if new_comments_count > 0:
                        print(f"{new_comments_count}件の新しいコメントを検出しました。合計: {total_comments}件")
                    
                except Exception as e:
                    print(f"エラーが発生しました: {str(e)}")
                
                # ページをスクロールして新しいコメントを表示
                try:
                    # コメント領域を再取得してスクロール
                    comment_container = driver.find_element(By.CSS_SELECTOR, "div.pc-comments.live-viewer")
                    driver.execute_script("arguments[0].scrollTop = 0;", comment_container)
                except Exception as e:
                    print(f"スクロールエラー: {str(e)}")
                
                # 次のチェックまで待機
                time.sleep(3)
                
            print(f"コメント抽出を終了しました。合計{total_comments}件のコメントを保存しました。")
            print(f"結果は {output_file} に保存されています。")
            
        finally:
            # ブラウザを閉じる
            driver.quit()
            
    # 結果をPandasで整形して表示
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        df = pd.read_csv(output_file)
        print("\n=== 抽出結果の概要 ===")
        print(f"合計コメント数: {len(df)}")
        if not df.empty:
            print(f"ユニークユーザー数: {df['ユーザー名'].nunique()}")
            print(f"最初のコメント時間: {df['タイムスタンプ'].iloc[0]}")
            print(f"最後のコメント時間: {df['タイムスタンプ'].iloc[-1]}")
            print("\n最初の5件のコメント:")
            print(df.head(5)[['タイムスタンプ', 'ユーザー名', 'コメント']])
            
            # トップユーザーの表示
            print("\n最もコメントの多いユーザー（上位5名）:")
            top_users = df['ユーザー名'].value_counts().head(5)
            for user, count in top_users.items():
                print(f"{user}: {count}件")
    
    return total_comments

def main():
    """メイン関数"""
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='Whowatchライブストリームからコメントを抽出するツール')
    parser.add_argument('url', help='抽出対象のWhowatchライブストリームURL')
    parser.add_argument('-t', '--time', type=int, default=10, 
                        help='抽出時間（分）。デフォルトは10分')
    parser.add_argument('-o', '--output', default='whowatch_comments.csv',
                        help='出力CSVファイル名。デフォルトはwhowatch_comments.csv')
    parser.add_argument('--headless', action='store_true',
                        help='ヘッドレスモードで実行（ブラウザウィンドウを表示しない）')
    
    # 引数を解析
    args = parser.parse_args()
    
    # 引数から値を取得
    target_url = args.url
    duration_min = args.time
    output_file = args.output
    headless_mode = args.headless
    
    # コメント抽出実行
    extract_comments(target_url, duration_min, output_file, headless_mode)

if __name__ == "__main__":
    main()
```

## 14. 使用方法

このスクリプトをPythonファイルとして保存し、以下のように実行します：

### 基本的な使用方法
```bash
python whowatch_comment_extractor.py https://whowatch.tv/viewer/61932105
```

### 抽出時間を指定する場合（例：30分）
```bash
python whowatch_comment_extractor.py https://whowatch.tv/viewer/61932105 -t 30
```

### 出力ファイル名も指定する場合
```bash
python whowatch_comment_extractor.py https://whowatch.tv/viewer/61932105 -t 30 -o my_comments.csv
```

### ヘッドレスモードで実行する場合
```bash
python whowatch_comment_extractor.py https://whowatch.tv/viewer/61932105 --headless
```

## 15. さらなる学習のためのチャレンジ

1. コメントの出現頻度をグラフで表示する機能を追加する
2. 特定のユーザーのコメントのみをフィルタリングする機能を追加する
3. GUIインターフェースを作成する
4. コメントの自動応答機能を追加する
5. 複数のライブストリームプラットフォームに対応させる

このチュートリアルを通じて、WebスクレイピングとSeleniumの基本から応用までを学ぶことができました。実際のプロジェクトに応用して、さらにスキルを磨いていきましょう！

## Seleniumと自動化における重要な概念

このプロジェクトで学んだ重要な概念は以下の通りです：

1. **ウェブドライバーの管理**: `webdriver-manager`を使って適切なバージョンのドライバーを自動的にダウンロードし管理する
2. **明示的な待機**: `WebDriverWait`を使って特定の要素が表示されるまで待機する
3. **要素の検索**: CSSセレクタを使って要素を柔軟に検索する
4. **動的コンテンツの処理**: JavaScriptを実行してDOM操作を行う
5. **エラー処理**: 例外処理を使って安定したスクレイピングを実現する
6. **ヘッドレスモード**: ブラウザを表示せずにバックグラウンドで実行する
7. **Stale Element Reference対策**: 動的に変更されるDOM要素への参照が古くなる問題への対処法

これらの概念は、他のWebスクレイピングや自動化プロジェクトにも応用できる重要なスキルです。
