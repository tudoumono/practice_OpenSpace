# BIGO LIVEコメント抽出ツール作成ガイド

## はじめに

このチュートリアルでは、Python と Selenium を使用して、BIGO LIVE ライブストリーミングプラットフォームからコメントを自動的に抽出するツールを作成する方法を段階的に学びます。初心者にもわかりやすいよう、各ステップで具体的な説明とコードを提供します。

## 目次

1. [必要な環境とライブラリのセットアップ](#1-必要な環境とライブラリのセットアップ)
2. [基本的なプロジェクト構造の作成](#2-基本的なプロジェクト構造の作成)
3. [ブラウザを起動してページにアクセスする](#3-ブラウザを起動してページにアクセスする)
4. [ヘッドレスモードの設定](#4-ヘッドレスモードの設定)
5. [BIGO LIVEのコメント領域の特定](#5-bigo-liveのコメント領域の特定)
6. [ポップアップと同意ボタンの処理](#6-ポップアップと同意ボタンの処理)
7. [コメント要素の抽出（JavaScriptを使用）](#7-コメント要素の抽出javascriptを使用)
8. [ユーザー名とコメント内容の分離](#8-ユーザー名とコメント内容の分離)
9. [コメントのクリーンアップとフォーマット](#9-コメントのクリーンアップとフォーマット)
10. [CSVファイルに保存する](#10-csvファイルに保存する)
11. [コメント欄のスクロール処理](#11-コメント欄のスクロール処理)
12. [コマンドライン引数の追加](#12-コマンドライン引数の追加)
13. [結果の分析と統計情報の表示](#13-結果の分析と統計情報の表示)
14. [完成版コード](#14-完成版コード)
15. [使用方法](#15-使用方法)
16. [よくある問題と解決方法](#16-よくある問題と解決方法)

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

まず、基本的なプロジェクト構造から始めましょう。

```python
# bigo_comment_extractor.py
# ライブラリのインポート
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime
import os
import argparse

def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    """
    指定したBIGO LIVEのURLからコメントを抽出する関数
    """
    print("BIGO LIVEコメント抽出ツール")
    print(f"対象URL: {url}")
    
    # この関数の内容は次のステップで実装していきます
    pass

def main():
    # メイン関数（後で実装）
    pass
    
if __name__ == "__main__":
    main()
```

これは基本構造で、これから徐々に機能を追加していきます。

## 3. ブラウザを起動してページにアクセスする

最初の実装ステップとして、Chromeブラウザを起動してBIGO LIVEにアクセスする部分を作成します。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    print("コメント抽出を開始します...")
    print(f"対象URL: {url}")
    print(f"実行時間: {duration_minutes}分")
    print(f"出力ファイル: {output_file}")
    
    # Chromeの設定
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")  # 通知を無効化
    chrome_options.add_argument("--mute-audio")  # 音声をミュート
    
    # ChromeDriverの自動インストールとサービスの設定
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # URLにアクセス
        driver.get(url)
        print("ページにアクセスしました")
        
        # ページが完全に読み込まれるまで待機
        time.sleep(5)
        
        # ページタイトルを取得して表示
        title = driver.title
        print(f"ページタイトル: {title}")
        
    finally:
        # ブラウザを閉じる
        driver.quit()
```

コードの説明：
- `Options()`でChromeブラウザの設定を行います
- `ChromeDriverManager().install()`で最新のChrome Driverを自動ダウンロードします
- `try-finally`構文を使って、エラーが発生しても確実にブラウザを閉じるようにします
- `--disable-notifications`と`--mute-audio`はBIGO LIVE特有の設定です（通知や音声を無効化）

## 4. ヘッドレスモードの設定

次に、ブラウザウィンドウを表示せずにバックグラウンドで実行する「ヘッドレスモード」のオプションを追加します。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    # 前のコードに追加
    print(f"ヘッドレスモード: {'有効' if headless else '無効'}")
    
    # Chromeの設定
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    
    # ヘッドレスモードの設定
    if headless:
        print("ヘッドレスモードで実行します（ブラウザウィンドウを表示しない）")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 残りのコードは同じ
```

ヘッドレスモードの利点：
- リソース使用量が少ない（CPUとメモリを節約）
- バックグラウンドで動作するので画面に表示されない
- サーバー環境など、GUI不要の環境でも実行可能

ただし、BIGO LIVEの場合は視覚的な要素（ポップアップなど）の処理が必要なため、開発中はヘッドレスモードを無効にしておくことをお勧めします。

## 5. BIGO LIVEのコメント領域の特定

BIGO LIVEでは、コメント領域は「chat__container」クラスで識別できます。この要素を検出するコードを追加します。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    # 前のコードを保持
    
    try:
        # URLにアクセス
        driver.get(url)
        print("ページにアクセスしました。コメント領域を探しています...")
        
        # コメント領域が表示されるまで待機（最大20秒）
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat__container"))
            )
            print("コメント領域を検出しました！")
            
            # コメント領域の情報を表示
            comment_area = driver.find_element(By.CLASS_NAME, "chat__container")
            print(f"コメント領域のサイズ: 幅={comment_area.size['width']}px, 高さ={comment_area.size['height']}px")
            
        except Exception as e:
            print(f"コメント領域の検出に失敗しました: {str(e)}")
            print("別のセレクタで試行します...")
            
            # 代替のセレクタを試してみる
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='chat']"))
                )
                print("代替セレクタでコメント領域を検出しました！")
            except Exception as e2:
                print(f"代替セレクタでも検出できませんでした: {str(e2)}")
                print("ページのHTMLを確認してください。")
                return 0
                
        # 残りのコードは次のステップで実装
    
    finally:
        # ブラウザを閉じる
        driver.quit()
```

新しい概念：
- `WebDriverWait`: 特定の条件が満たされるまで待機する機能
- `EC.presence_of_element_located`: 要素が存在するかをチェックする条件
- 代替セレクタの試行：BIGO LIVEのサイト更新に備えて柔軟に対応

BIGO LIVE特有の注意点：
- コメント領域のクラス名は「chat__container」
- サイトの更新によりクラス名が変更される可能性があるため、部分一致の代替セレクタも用意

## 6. ポップアップと同意ボタンの処理

BIGO LIVEでは年齢確認や利用規約同意などのポップアップが表示されることがあります。これらを自動的に処理するコードを追加します。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    # 前のコードを保持
    
    # コメント領域を検出した後に追加
    # ポップアップや同意ボタンがあれば処理
    try:
        # 年齢確認や同意ボタンの処理
        consent_buttons = driver.find_elements(By.CSS_SELECTOR, 
                                              "button[class*='confirm'], button[class*='agree'], button[class*='accept']")
        for button in consent_buttons:
            if button.is_displayed():
                button.click()
                print("同意ボタンをクリックしました")
                time.sleep(1)
    except Exception as e:
        print(f"ボタン処理中にエラーが発生しました: {str(e)}")
    
    # 残りのコードは次のステップで実装
```

BIGO LIVE特有の処理：
- 多くのライブストリーミングサイトと同様に、BIGO LIVEにもポップアップや確認ダイアログが表示されることがあります
- このコードでは、「confirm」「agree」「accept」などのクラス名を含むボタンを自動的に検出してクリックします
- これにより、年齢確認や利用規約同意などのポップアップを自動的に処理できます

## 7. コメント要素の抽出（JavaScriptを使用）

BIGO LIVEのコメントを抽出するために、JavaScriptを使用して直接DOM要素にアクセスします。これにより「stale element reference」などのエラーを回避できます。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    # 前のコードを保持
    
    # CSVファイルの準備
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'コメント'])
        
        # 前回取得したコメントを記録するセット
        previous_comments = set()
        
        try:
            # URLにアクセスとコメント領域の検出（前のコード）
            # ...
            
            # 指定時間（デフォルト10分）実行
            end_time = time.time() + (duration_minutes * 60)
            total_comments = 0
            
            print(f"コメントの抽出を開始します。{duration_minutes}分間実行します...")
            
            while time.time() < end_time:
                try:
                    # コメント領域を毎回取得し直す (stale element対策)
                    comment_container = driver.find_element(By.CLASS_NAME, "chat__container")
                    
                    # JavaScriptを使ってコメントデータを抽出
                    driver.execute_script("""
                    (function() {
                        // メモリにコメントデータを保存
                        window.commentData = [];
                        var commentContainer = document.querySelector(".chat__container");
                        if (!commentContainer) return;
                        
                        // コメント要素を探す - BIGO LIVEのコメント要素のセレクタを調整
                        var commentElements = commentContainer.querySelectorAll(".chat-message, .message-item, [class*='message'], [class*='chat-item']");
                        
                        // 各コメント要素から情報を抽出
                        for (var i = 0; i < commentElements.length; i++) {
                            var element = commentElements[i];
                            
                            // ユーザー名の抽出
                            var username = "不明";
                            var usernameSelectors = [
                                ".username", ".user-name", ".author", 
                                "[class*='username']", "[class*='user-name']", 
                                "[class*='author']", "[class*='nick']"
                            ];
                            
                            for (var j = 0; j < usernameSelectors.length; j++) {
                                var usernameElem = element.querySelector(usernameSelectors[j]);
                                if (usernameElem && usernameElem.textContent.trim()) {
                                    username = usernameElem.textContent.trim();
                                    break;
                                }
                            }
                            
                            // コメントテキストの抽出
                            var commentText = "";
                            var commentSelectors = [
                                ".message-content", ".content", ".text", 
                                "[class*='message-content']", "[class*='content']", 
                                "[class*='text']", "[class*='comment']"
                            ];
                            
                            for (var k = 0; k < commentSelectors.length; k++) {
                                var commentElem = element.querySelector(commentSelectors[k]);
                                if (commentElem && commentElem.textContent.trim()) {
                                    commentText = commentElem.textContent.trim();
                                    break;
                                }
                            }
                            
                            // 結果を保存（まだ未完成、次のステップで追加）
                        }
                    })();
                    """)
                    
                    # 次のステップで残りのコードを実装
                    
                except Exception as e:
                    print(f"エラーが発生しました: {str(e)}")
                
                # 次のチェックまで待機
                time.sleep(3)
                
        finally:
            # ブラウザを閉じる
            driver.quit()
```

新しい概念：
- `execute_script()`: ブラウザでJavaScriptを実行する
- JavaScriptでDOMを操作して要素から情報を抽出する
- 複数のセレクタを試すことで、サイト構造の変更に対応

BIGO LIVE特有の調整：
- BIGO LIVEでよく使われるコメント要素のセレクタを追加（`.chat-message`, `.message-item`など）
- ユーザー名の要素として、`.username`, `.user-name`, `.author`, `[class*='nick']`などを試行
- コメント本文の要素として、`.message-content`, `.content`, `.text`などを試行

## 8. ユーザー名とコメント内容の分離

前のステップのJavaScriptコードを拡張して、ユーザー名とコメント内容を適切に分離します。

```javascript
// JavaScriptコードの続き（前のコードの途中から）

// コメントが空の場合、要素全体のテキストを使用
if (!commentText) {
    var fullText = element.textContent.trim();
    // ユーザー名部分を除外
    if (username !== "不明" && fullText.includes(username)) {
        commentText = fullText.replace(username, "").trim();
    } else {
        commentText = fullText;
    }
}

// 空のコメントはスキップ
if (!commentText) continue;

// 結果を保存
window.commentData.push({
    username: username,
    comment: commentText
});
```

このコードは以下のような処理を行います：
1. コメント要素から直接テキストが抽出できない場合、要素全体のテキストを使用
2. その場合、ユーザー名が含まれていればそれを除去してコメント部分だけを取得
3. コメントが空の場合はスキップ
4. 抽出したユーザー名とコメントをオブジェクトとしてJavaScriptの配列に保存

## 9. コメントのクリーンアップとフォーマット

BIGO LIVEのコメントには、ユーザー名とコメントの間にコロン（:）や矢印（>）などの区切り文字がつくことがあります。これらをクリーンアップするコードを追加します。

```javascript
// JavaScriptコードの続き

// コメントの最終クリーンアップ
// コロン、矢印などの区切り文字を削除
commentText = commentText.replace(/^[：:》>]/, '').trim();

// 結果を保存
window.commentData.push({
    username: username,
    comment: commentText
});
```

BIGO LIVE特有の処理：
- BIGO LIVEでは、ユーザー名の後に「:」や「>」などの区切り文字が表示されることがある
- これらの区切り文字をコメントテキストの先頭から削除
- 正規表現`/^[：:》>]/`を使って、先頭の区切り文字を検出して削除

## 10. CSVファイルに保存する

JavaScriptから取得したコメントデータをCSVファイルに保存するコードを追加します。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    # 前のコードを保持
    
    # JavaScriptの実行後
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
```

新しい概念：
- `driver.execute_script("return window.commentData;")`: JavaScriptから結果を取得
- 重複チェック: `comment_id`を使って既に処理したコメントをスキップ
- `file.flush()`: 書き込みをディスクに即時反映（プログラムが途中で終了した場合でもデータが保存される）

## 11. コメント欄のスクロール処理

BIGO LIVEのコメント欄は、新しいコメントが下部に表示される傾向があります。これを確実に取得するためにスクロール処理を追加します。

```python
# コメントデータの処理後に追加

# コメント欄が動的に更新される場合、スクロールして新しいコメントを表示
try:
    # コメント領域をスクロール（BIGO LIVEでは下部に新しいコメントが表示される場合が多い）
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", comment_container)
except Exception as e:
    print(f"スクロールエラー: {str(e)}")
```

BIGO LIVE特有の処理：
- BIGO LIVEのコメント欄は通常、新しいコメントが下部に表示されます
- `scrollTop = scrollHeight`を設定することで、コメント領域を最下部までスクロール
- これにより、最新のコメントも取得できるようになります

## 12. コマンドライン引数の追加

スクリプトをより柔軟に使えるように、コマンドライン引数を追加します。

```python
def main():
    """メイン関数"""
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='BIGO LIVEストリームからコメントを抽出するツール')
    parser.add_argument('url', help='抽出対象のBIGO LIVEストリームURL')
    parser.add_argument('-t', '--time', type=int, default=10, 
                        help='抽出時間（分）。デフォルトは10分')
    parser.add_argument('-o', '--output', default='bigo_comments.csv',
                        help='出力CSVファイル名。デフォルトはbigo_comments.csv')
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
```

新しい概念：
- `argparse`: コマンドライン引数を処理するためのモジュール
- パラメータの型指定と説明
- デフォルト値の設定
- ブール値フラグの設定（`--headless`）

## 13. 結果の分析と統計情報の表示

最後に、抽出したコメントの基本的な分析と統計情報を表示するコードを追加します。

```python
def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    # 前のコードを保持
    
    # ブラウザを閉じた後に実行
    
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
```

新しい概念：
- `pandas`を使ったデータ分析
- データフレームの基本操作（`head()`、`nunique()`など）
- `value_counts()`を使った頻度集計

これにより、抽出したコメントの概要を簡単に把握できます。

## 14. 完成版コード

以下が、すべてのステップを統合した完全なコードです：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIGO LIVEストリームコメント抽出ツール
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

def extract_comments(url, duration_minutes=10, output_file="bigo_comments.csv", headless=False):
    """
    指定したBIGO LIVEのURLからコメントを抽出する
    
    Parameters:
        url (str): BIGO LIVEのライブストリームURL
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
        print("ヘッドレスモードで実行します（ブラウザウィンドウを表示されません）")
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
                    EC.presence_of_element_located((By.CLASS_NAME, "chat__container"))
                )
                print("コメント領域を検出しました！")
            except Exception as e:
                print(f"コメント領域の検出に失敗しました: {str(e)}")
                print("別のセレクタで試行します...")
                
                # 代替のセレクタを試してみる
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='chat']"))
                    )
                    print("代替セレクタでコメント領域を検出しました！")
                except Exception as e2:
                    print(f"代替セレクタでも検出できませんでした: {str(e2)}")
                    print("ページのHTMLを確認してください。")
                    return 0
            
            # ポップアップや同意ボタンがあれば処理
            try:
                # 年齢確認や同意ボタンの処理
                consent_buttons = driver.find_elements(By.CSS_SELECTOR, 
                                                      "button[class*='confirm'], button[class*='agree'], button[class*='accept']")
                for button in consent_buttons:
                    if button.is_displayed():
                        button.click()
                        print("同意ボタンをクリックしました")
                        time.sleep(1)
            except Exception as e:
                print(f"ボタン処理中にエラーが発生しました: {str(e)}")
            
            # 指定時間（デフォルト10分）実行
            end_time = time.time() + (duration_minutes * 60)
            total_comments = 0
            
            print(f"コメントの抽出を開始します。{duration_minutes}分間実行します...")
            
            while time.time() < end_time:
                try:
                    # コメント領域を毎回取得し直す (stale element対策)
                    comment_container = driver.find_element(By.CLASS_NAME, "chat__container")
                    
                    # JavaScriptを使ってコメントデータを抽出
                    driver.execute_script("""
                    (function() {
                        // メモリにコメントデータを保存
                        window.commentData = [];
                        var commentContainer = document.querySelector(".chat__container");
                        if (!commentContainer) return;
                        
                        // コメント要素を探す - BIGO LIVEのコメント要素のセレクタを調整
                        var commentElements = commentContainer.querySelectorAll(".chat-message, .message-item, [class*='message'], [class*='chat-item']");
                        
                        // 各コメント要素から情報を抽出
                        for (var i = 0; i < commentElements.length; i++) {
                            var element = commentElements[i];
                            
                            // ユーザー名の抽出
                            var username = "不明";
                            var usernameSelectors = [
                                ".username", ".user-name", ".author", 
                                "[class*='username']", "[class*='user-name']", 
                                "[class*='author']", "[class*='nick']"
                            ];
                            
                            for (var j = 0; j < usernameSelectors.length; j++) {
                                var usernameElem = element.querySelector(usernameSelectors[j]);
                                if (usernameElem && usernameElem.textContent.trim()) {
                                    username = usernameElem.textContent.trim();
                                    break;
                                }
                            }
                            
                            // コメントテキストの抽出
                            var commentText = "";
                            var commentSelectors = [
                                ".message-content", ".content", ".text", 
                                "[class*='message-content']", "[class*='content']", 
                                "[class*='text']", "[class*='comment']"
                            ];
                            
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
                                // ユーザー名部分を除外
                                if (username !== "不明" && fullText.includes(username)) {
                                    commentText = fullText.replace(username, "").trim();
                                } else {
                                    commentText = fullText;
                                }
                            }
                            
                            // 空のコメントはスキップ
                            if (!commentText) continue;
                            
                            // コメントの最終クリーンアップ
                            // コロン、矢印などの区切り文字を削除
                            commentText = commentText.replace(/^[：:》>]/, '').trim();
                            
                            // 結果を保存
                            window.commentData.push({
                                username: username,
                                comment: commentText
                            });
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
                    
                    # コメント欄が動的に更新される場合、スクロールして新しいコメントを表示
                    try:
                        # コメント領域をスクロール（BIGO LIVEでは下部に新しいコメントが表示される場合が多い）
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", comment_container)
                    except Exception as e:
                        print(f"スクロールエラー: {str(e)}")
                    
                except Exception as e:
                    print(f"エラーが発生しました: {str(e)}")
                
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
    parser = argparse.ArgumentParser(description='BIGO LIVEストリームからコメントを抽出するツール')
    parser.add_argument('url', help='抽出対象のBIGO LIVEストリームURL')
    parser.add_argument('-t', '--time', type=int, default=10, 
                        help='抽出時間（分）。デフォルトは10分')
    parser.add_argument('-o', '--output', default='bigo_comments.csv',
                        help='出力CSVファイル名。デフォルトはbigo_comments.csv')
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

## 15. 使用方法

このスクリプトをPythonファイルとして保存し、以下のように実行します：

### 基本的な使用方法
```bash
python bigo_comment_extractor.py https://www.bigo.tv/ja/975053474
```

### 抽出時間を指定する場合（例：30分）
```bash
python bigo_comment_extractor.py https://www.bigo.tv/ja/975053474 -t 30
```

### 出力ファイル名も指定する場合
```bash
python bigo_comment_extractor.py https://www.bigo.tv/ja/975053474 -t 30 -o my_bigo_comments.csv
```

### ヘッドレスモードで実行する場合
```bash
python bigo_comment_extractor.py https://www.bigo.tv/ja/975053474 --headless
```

## 16. よくある問題と解決方法

### コメント領域が見つからない
- ページの読み込みが完了していない可能性があります。`WebDriverWait`の時間を長くしてみてください。
- クラス名が変更された可能性があります。ブラウザの開発者ツールでHTMLを確認して、正しいクラス名に更新してください。

### "stale element reference"エラーが発生する
- DOM要素が更新されて古い参照が無効になりました。このスクリプトではJavaScriptを使って対策していますが、問題が続く場合は、`try-except`ブロックをさらに追加して対応してください。

### ポップアップが処理されない
- ポップアップのCSSセレクタが変更された可能性があります。`consent_buttons`のセレクタを更新してみてください。
- ポップアップが非表示になっている場合、`is_displayed()`チェックをスキップするか、JavaScriptを使って直接クリックしてみてください。

### コメントが抽出されない
- ページの構造が変わった可能性があります。JavaScriptコード内のセレクタを更新してください。
- 特殊な文字や絵文字がある場合、CSV保存時に問題が発生することがあります。`csv.writer`のエスケープ設定を調整してみてください。

### ヘッドレスモードで動作しない
- BIGO LIVEがヘッドレスブラウザを検出して、別の表示をしている可能性があります。通常モードで実行するか、追加のヘッドレスモード対策を施してください。
