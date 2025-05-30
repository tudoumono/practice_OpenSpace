# Pocochaライブストリームコメント抽出ツール作成ガイド

## はじめに

このチュートリアルでは、Python と Selenium を使用して、Pococha からライブストリーミング中のコメントを自動的に抽出するツールを作成する方法を段階的に学びます。初心者にもわかりやすいよう、各ステップで具体的な説明とコードを提供します。

**注意**: Pocochaはログインが必要なプラットフォームのため、手動ログイン方式を採用し、利用規約を遵守した設計となっています。

## 目次

1. [必要な環境とライブラリのセットアップ](#1-必要な環境とライブラリのセットアップ)
2. [基本的なプロジェクト構造の作成](#2-基本的なプロジェクト構造の作成)
3. [ブラウザを起動してPocochaにアクセス](#3-ブラウザを起動してpocochaにアクセス)
4. [手動ログイン機能の実装](#4-手動ログイン機能の実装)
5. [Pocochaダイアログの自動処理](#5-pocochaダイアログの自動処理)
6. [ライブ再生ボタンのクリック](#6-ライブ再生ボタンのクリック)
7. [コメント領域の特定](#7-コメント領域の特定)
8. [Pocochaコメントの構造分析](#8-pocochaコメントの構造分析)
9. [ユーザー情報とコメント内容の抽出](#9-ユーザー情報とコメント内容の抽出)
10. [CSVファイルに保存する](#10-csvファイルに保存する)
11. [継続的にコメントを監視する](#11-継続的にコメントを監視する)
12. [JavaScript を使った堅牢な抽出](#12-javascript-を使った堅牢な抽出)
13. [コマンドライン引数とデバッグ機能](#13-コマンドライン引数とデバッグ機能)
14. [完成版コード](#14-完成版コード)
15. [使用方法とトラブルシューティング](#15-使用方法とトラブルシューティング)
16. [さらなる学習のためのチャレンジ](#16-さらなる学習のためのチャレンジ)

## 1. 必要な環境とライブラリのセットアップ

Pocochaのコメント抽出に必要なライブラリをインストールしましょう。

```bash
pip install selenium webdriver-manager pandas
```

これらのライブラリの役割は：
- `selenium`: Webブラウザを自動操作するためのライブラリ
- `webdriver-manager`: ChromeDriverを自動で管理
- `pandas`: データ分析と処理のためのライブラリ

**Pocochaとwhowatchの主な違い**:
- Pocochaはログインが必須
- ダイアログ処理が必要
- 再生ボタンをクリックしないとコメントが流れない
- HTMLの構造が独特

## 2. 基本的なプロジェクト構造の作成

```python
# pococha_comment_extractor.py
# ライブラリのインポート
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    print("Pocochaライブストリームコメント抽出ツール")
    print("注意：このツールはPocochaの利用規約を遵守して使用してください")
    
if __name__ == "__main__":
    main()
```

このシンプルな構造から始めて、段階的に機能を追加していきます。

## 3. ブラウザを起動してPocochaにアクセス

まず、Seleniumを使ってブラウザを操作し、Pocochaのログインページにアクセスする基本部分を実装します。

```python
# pococha_comment_extractor.py
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
    chrome_options.add_argument("--disable-notifications")  # 通知を無効化
    chrome_options.add_argument("--mute-audio")  # 音声をミュート
    
    # 自動化検出を回避するための設定
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # ChromeDriverの設定
    service = Service(ChromeDriverManager().install())
    
    # ブラウザを起動
    print("ブラウザを起動中...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # WebDriverプロパティを隠す
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Pocochaログインページにアクセス
    login_url = "https://www.pococha.com/ja-jp/login"
    print(f"{login_url} にアクセス中...")
    driver.get(login_url)
    
    # ページが完全に読み込まれるまで待機
    time.sleep(5)
    
    # ページタイトルを取得して表示
    title = driver.title
    print(f"ページタイトル: {title}")
    
    # ページのURLを確認
    current_url = driver.current_url
    print(f"現在のURL: {current_url}")
    
    # 一旦停止してブラウザの状態を確認
    input("ブラウザでPocochaの状態を確認してからEnterキーを押してください...")
    
    # ブラウザを閉じる
    print("ブラウザを閉じています...")
    driver.quit()
    
if __name__ == "__main__":
    main()
```

**Pococha特有の設定**:
- 自動化検出を回避する設定（Pocochaはbot検出が厳しいため）
- 通知とオーディオを無効化（ライブ配信のため）
- WebDriverプロパティを隠す

## 4. 手動ログイン機能の実装

Pocochaは認証が必要なプラットフォームのため、手動ログイン機能を実装します。これにより利用規約を遵守しつつ、安全にアクセスできます。

```python
# pococha_comment_extractor.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def wait_for_manual_login(driver):
    """
    手動ログインの完了を待機する
    """
    print("=" * 60)
    print("手動ログインが必要です")
    print("=" * 60)
    print("以下の手順でログインしてください：")
    print("1. ブラウザでPocochaログインページが表示されています")
    print("2. お好みの方法でログイン（Google、LINE、Apple ID、メール等）")
    print("3. 2段階認証がある場合は認証コードを入力")
    print("4. ログイン完了後、このターミナルに戻ってEnterキーを押してください")
    print("=" * 60)
    
    input("ログイン完了後、Enterキーを押してください...")
    
    # ログイン状態を確認
    current_url = driver.current_url
    print(f"現在のURL: {current_url}")
    
    if "login" in current_url.lower():
        print("⚠️ まだログインページにいるようです。")
        retry = input("ログインを完了してからもう一度試しますか？ (y/N): ")
        if retry.lower() == 'y':
            return wait_for_manual_login(driver)
        else:
            return False
    
    print("✅ ログインが完了しました！")
    return True

def main():
    # ブラウザの設定（前のコードと同じ）
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Pocochaログインページにアクセス
        print("Pocochaのログインページにアクセスしています...")
        driver.get("https://www.pococha.com/ja-jp/login")
        
        # ページの読み込み完了を待機
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        
        # 手動ログイン待機
        if not wait_for_manual_login(driver):
            print("ログインに失敗しました。")
            return
        
        # ログイン後の処理をここに追加
        print("ログインが成功しました。次のステップに進みます...")
        
    finally:
        input("処理を終了するにはEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**手動ログインの利点**:
- 利用規約に準拠
- 2段階認証に対応
- セキュリティが高い
- 認証情報をファイルに保存する必要がない

## 5. Pocochaダイアログの自動処理

Pocochaにログイン後、「Web版Pocochaへようこそ」などのダイアログが表示されることがあります。これを自動で処理する機能を追加します。

```python
# pococha_comment_extractor.py
# 前のインポートに加えて
from selenium.common.exceptions import TimeoutException

def handle_pococha_dialogs(driver):
    """
    Pocochaの各種ダイアログを処理する
    """
    print("Pocochaのダイアログを確認中...")
    
    try:
        # 「Web版Pocochaへようこそ」ダイアログのOKボタンを探す
        ok_selectors = [
            (By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'ok')]"),
            (By.CSS_SELECTOR, "button[class*='ok']"),
            (By.XPATH, "//button[text()='OK']"),
        ]
        
        ok_button = None
        for selector_type, selector_value in ok_selectors:
            try:
                ok_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                # ボタンのテキストを確認
                button_text = ok_button.text.strip().lower()
                if 'ok' in button_text:
                    print(f"ダイアログのOKボタンを発見: {button_text}")
                    break
                else:
                    ok_button = None
                    continue
                    
            except TimeoutException:
                continue
        
        if ok_button:
            ok_button.click()
            print("✅ ダイアログのOKボタンをクリックしました。")
            time.sleep(2)
        else:
            print("ダイアログは表示されていないか、既に閉じられています。")
            
    except Exception as e:
        print(f"ダイアログ処理でエラー: {str(e)}")
    
    return True

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # ログイン処理
        driver.get("https://www.pococha.com/ja-jp/login")
        # ...
        
        if not wait_for_manual_login(driver):
            print("ログインに失敗しました。")
            return
        
        # ダイアログ処理
        handle_pococha_dialogs(driver)
        
        print("ダイアログ処理が完了しました。")
        
    finally:
        input("処理を終了するにはEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**ダイアログ処理のポイント**:
- 複数のセレクタで堅牢に検索
- タイムアウトエラーをキャッチ
- ボタンのテキストを確認して適切なボタンをクリック

## 6. ライブ再生ボタンのクリック

Pocochaではライブストリームの再生ボタンをクリックしないとコメントが流れません。この機能を追加します。

```python
# pococha_comment_extractor.py

def click_play_button(driver):
    """
    ライブストリームの再生ボタンをクリックする
    """
    print("ライブストリームの再生ボタンを探しています...")
    
    # 再生ボタンのセレクタ（実際のPocochaの要素に基づく）
    play_selectors = [
        (By.CSS_SELECTOR, "div.video_playButton__Q_Ecm"),
        (By.CSS_SELECTOR, ".video_playButton__Q_Ecm"),
        (By.XPATH, "//div[contains(@class, 'video_playButton')]"),
        (By.XPATH, "//div[contains(@class, 'playButton')]"),
        (By.CSS_SELECTOR, "div[class*='playButton']"),
        (By.XPATH, "//img[@class='video_icon__OO57P']//parent::div"),
    ]
    
    play_button = None
    for selector_type, selector_value in play_selectors:
        try:
            play_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            print(f"再生ボタンを発見: {selector_type} = {selector_value}")
            break
        except TimeoutException:
            continue
    
    if play_button:
        play_button.click()
        print("✅ ライブストリームの再生ボタンをクリックしました。")
        time.sleep(3)
        return True
    else:
        print("⚠️ 再生ボタンが見つかりませんでした。")
        print("手動で再生ボタンをクリックしてください。")
        input("再生開始後、Enterキーを押してください...")
        return True

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # ログイン処理とダイアログ処理
        # ...
        
        # ライブストリームページにアクセス
        live_url = "https://www.pococha.com/ja-jp/app/lives/67761158"  # 例
        print(f"ライブストリームページにアクセス: {live_url}")
        driver.get(live_url)
        
        # ページの読み込み完了を待機
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        
        # ダイアログ処理
        handle_pococha_dialogs(driver)
        
        # 再生ボタンをクリック
        click_play_button(driver)
        
        print("ライブストリームの再生が開始されました。")
        
    finally:
        input("処理を終了するにはEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**再生ボタンの重要性**:
- Pocochaではライブを再生しないとコメントが更新されない
- 複数のセレクタで確実に検出
- 手動フォールバックを用意

## 7. コメント領域の特定

次に、ページ内のコメント領域を特定します。PocochaのHTML構造を分析して適切なセレクタを使用します。

```python
# pococha_comment_extractor.py

def find_comment_area(driver):
    """
    Pocochaのコメント領域を特定する
    """
    print("コメント領域を探しています...")
    
    # Pocochaのコメント領域セレクタ
    comment_selectors = [
        (By.CSS_SELECTOR, "div.messages_wrapper___xQBv"),
        (By.CSS_SELECTOR, "div.messages_messagesWrapper__l2Aus"),
        (By.CSS_SELECTOR, "[class*='messages_wrapper']"),
        (By.CSS_SELECTOR, "[class*='messagesWrapper']"),
    ]
    
    comment_area = None
    for selector_type, selector_value in comment_selectors:
        try:
            comment_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            print(f"コメント領域を発見: {selector_type} = {selector_value}")
            break
        except TimeoutException:
            continue
    
    if comment_area:
        print("✅ コメント領域を検出しました！")
        
        # コメント領域の情報を表示
        print(f"コメント領域のサイズ: 幅={comment_area.size['width']}px, 高さ={comment_area.size['height']}px")
        
        # コメント領域内のコメント数を確認
        comment_items = comment_area.find_elements(By.CSS_SELECTOR, "div.messages_messagesItem__PpIZU")
        print(f"現在表示されているコメント数: {len(comment_items)}件")
        
        return comment_area
    else:
        print("❌ コメント領域の検出に失敗しました。")
        print("ページが正しく読み込まれているか確認してください。")
        return None

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # ログイン、ダイアログ処理、再生ボタンクリック
        # ...
        
        # コメント領域を探す
        comment_area = find_comment_area(driver)
        
        if comment_area:
            print("コメント抽出の準備が完了しました！")
        else:
            print("コメント領域が見つからないため、処理を終了します。")
            return
        
    finally:
        input("処理を終了するにはEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**Pocochaのコメント構造**:
- `div.messages_wrapper___xQBv`: メインのコメントラッパー
- `div.messages_messagesWrapper__l2Aus`: コメントコンテナ
- `div.messages_messagesItem__PpIZU`: 個別のコメントアイテム

## 8. Pocochaコメントの構造分析

PocochaのHTMLからコメントの詳細構造を分析し、ユーザー名、レベル、コメント内容を適切に抽出できるようにします。

```python
# pococha_comment_extractor.py

def analyze_comment_structure(driver):
    """
    Pocochaのコメント構造を分析する
    """
    print("コメント構造を分析中...")
    
    try:
        # コメント領域を取得
        comment_area = driver.find_element(By.CSS_SELECTOR, "div.messages_messagesWrapper__l2Aus")
        
        # コメントアイテムを取得
        comment_items = comment_area.find_elements(By.CSS_SELECTOR, "div.messages_messagesItem__PpIZU")
        
        print(f"分析対象のコメント数: {len(comment_items)}件")
        
        for i, item in enumerate(comment_items[:3]):  # 最初の3件を分析
            print(f"\n--- コメント #{i+1} の構造分析 ---")
            
            # メッセージラッパーを取得
            message_wrapper = item.find_element(By.CSS_SELECTOR, "div.messages_messageWrapper__cF93S")
            message_body = message_wrapper.find_element(By.CSS_SELECTOR, "div.common-message-styles_messageBody__89Pbc")
            
            # 運営メッセージかどうかをチェック
            is_system_message = "live-news-message_info__L_ooM" in message_body.get_attribute("class")
            
            if is_system_message:
                print("タイプ: 運営からのお知らせ")
                message_text = message_body.find_element(By.TAG_NAME, "span").text
                print(f"メッセージ: {message_text}")
            else:
                print("タイプ: ユーザーコメント")
                
                # ユーザー名とレベルを取得
                try:
                    name_wrapper = message_body.find_element(By.CSS_SELECTOR, "span.name_wrapper__jpk5P")
                    
                    # ユーザー名
                    name_element = name_wrapper.find_element(By.CSS_SELECTOR, "span.name_name__1stkJ")
                    username = name_element.text.strip()
                    print(f"ユーザー名: {username}")
                    
                    # レベル
                    try:
                        level_element = name_wrapper.find_element(By.CSS_SELECTOR, "span.name_level__dHiJG")
                        level = level_element.text.strip()
                        print(f"レベル: {level}")
                    except:
                        print("レベル: 取得できませんでした")
                    
                    # コメント内容（ユーザー名ラッパーの外にあるspan要素）
                    comment_spans = message_body.find_elements(By.TAG_NAME, "span")
                    for span in comment_spans:
                        if not span.find_elements(By.XPATH, "./ancestor-or-self::*[contains(@class, 'name_wrapper__jpk5P')]"):
                            comment_text = span.text.strip()
                            if comment_text:
                                print(f"コメント: {comment_text}")
                                break
                    
                except Exception as e:
                    print(f"ユーザー情報の抽出でエラー: {e}")
            
            print(f"HTML: {item.get_attribute('outerHTML')[:150]}...")
    
    except Exception as e:
        print(f"コメント構造分析でエラー: {e}")

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # 全ての前処理（ログイン、ダイアログ、再生ボタン等）
        # ...
        
        # コメント領域を確認
        comment_area = find_comment_area(driver)
        if comment_area:
            # コメント構造を分析
            analyze_comment_structure(driver)
        
    finally:
        input("分析結果を確認してからEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**Pocochaコメントの特徴**:
- ユーザーコメントと運営メッセージが混在
- ユーザー名、レベル、コメント内容が分離されている
- CSS クラス名が特徴的（ハッシュ付き）

## 9. ユーザー情報とコメント内容の抽出

コメント構造の分析結果を元に、実際にユーザー情報とコメント内容を抽出する機能を実装します。

```python
# pococha_comment_extractor.py
import csv
from datetime import datetime

def extract_single_comment(comment_item):
    """
    単一のコメントアイテムから情報を抽出する
    """
    try:
        message_wrapper = comment_item.find_element(By.CSS_SELECTOR, "div.messages_messageWrapper__cF93S")
        message_body = message_wrapper.find_element(By.CSS_SELECTOR, "div.common-message-styles_messageBody__89Pbc")
        
        # 運営メッセージかどうかをチェック
        is_system_message = "live-news-message_info__L_ooM" in message_body.get_attribute("class")
        
        if is_system_message:
            # 運営からのお知らせの場合
            message_text = message_body.find_element(By.TAG_NAME, "span").text.strip()
            return {
                'username': '運営',
                'level': '',
                'comment': message_text,
                'type': 'system'
            }
        else:
            # 一般ユーザーのコメントの場合
            username = "不明"
            level = ""
            comment_text = ""
            
            # ユーザー名とレベルを取得
            try:
                name_wrapper = message_body.find_element(By.CSS_SELECTOR, "span.name_wrapper__jpk5P")
                
                # ユーザー名
                name_element = name_wrapper.find_element(By.CSS_SELECTOR, "span.name_name__1stkJ")
                username = name_element.text.strip()
                
                # レベル
                try:
                    level_element = name_wrapper.find_element(By.CSS_SELECTOR, "span.name_level__dHiJG")
                    level = level_element.text.strip()
                except:
                    pass
            except:
                pass
            
            # コメント内容を取得
            try:
                comment_spans = message_body.find_elements(By.TAG_NAME, "span")
                for span in comment_spans:
                    # name_wrapper の外にあるspan要素を探す
                    if not span.find_elements(By.XPATH, "./ancestor-or-self::*[contains(@class, 'name_wrapper__jpk5P')]"):
                        comment_text = span.text.strip()
                        if comment_text:
                            break
            except:
                pass
            
            return {
                'username': username,
                'level': level,
                'comment': comment_text,
                'type': 'user'
            }
    
    except Exception as e:
        print(f"コメント抽出エラー: {e}")
        return None

def extract_all_comments(driver, output_file="pococha_comments.csv"):
    """
    現在表示されているすべてのコメントを抽出する
    """
    print("コメントを抽出中...")
    
    # CSVファイルの準備
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'レベル', 'コメント', 'コメントタイプ'])
        
        try:
            # コメント領域を取得
            comment_area = driver.find_element(By.CSS_SELECTOR, "div.messages_messagesWrapper__l2Aus")
            
            # コメントアイテムを取得
            comment_items = comment_area.find_elements(By.CSS_SELECTOR, "div.messages_messagesItem__PpIZU")
            
            print(f"抽出対象のコメント数: {len(comment_items)}件")
            
            successful_extracts = 0
            
            for i, item in enumerate(comment_items):
                comment_data = extract_single_comment(item)
                
                if comment_data and comment_data['comment']:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # CSVに書き込み
                    writer.writerow([
                        timestamp,
                        comment_data['username'],
                        comment_data['level'],
                        comment_data['comment'],
                        comment_data['type']
                    ])
                    
                    successful_extracts += 1
                    
                    # コンソールに表示
                    if comment_data['type'] == 'system':
                        print(f"{timestamp} - [運営] {comment_data['comment']}")
                    else:
                        print(f"{timestamp} - {comment_data['username']}(Lv.{comment_data['level']}): {comment_data['comment']}")
                
                # 少し待機してブラウザの負荷を減らす
                time.sleep(0.1)
            
            print(f"\n抽出完了！{successful_extracts}件のコメントを {output_file} に保存しました")
            
        except Exception as e:
            print(f"コメント抽出でエラー: {e}")

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # 全ての前処理
        # ...
        
        # コメント領域を確認
        comment_area = find_comment_area(driver)
        if comment_area:
            # コメントを抽出
            extract_all_comments(driver)
        
    finally:
        input("抽出結果を確認してからEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**抽出のポイント**:
- 運営メッセージとユーザーコメントを区別
- ユーザー名、レベル、コメント内容を正確に分離
- エラーハンドリングで堅牢性を確保

## 10. CSVファイルに保存する

抽出したコメントをCSVファイルに構造化して保存し、後で分析できるようにします。

```python
# pococha_comment_extractor.py
import os
import pandas as pd

def save_comments_to_csv(comments_data, output_file="pococha_comments.csv"):
    """
    コメントデータをCSVファイルに保存する
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # ヘッダーを書き込み
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'レベル', 'コメント', 'コメントタイプ'])
        
        # データを書き込み
        for comment in comments_data:
            writer.writerow([
                comment['timestamp'],
                comment['username'],
                comment['level'],
                comment['comment'],
                comment['type']
            ])
    
    print(f"✅ {len(comments_data)}件のコメントを {output_file} に保存しました")

def analyze_csv_results(output_file):
    """
    保存されたCSVファイルの内容を分析する
    """
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        df = pd.read_csv(output_file)
        
        print("\n=== 抽出結果の概要 ===")
        print(f"合計コメント数: {len(df)}")
        
        if not df.empty:
            user_comments = df[df['コメントタイプ'] == 'user']
            system_comments = df[df['コメントタイプ'] == 'system']
            
            print(f"ユーザーコメント数: {len(user_comments)}")
            print(f"運営メッセージ数: {len(system_comments)}")
            
            if len(user_comments) > 0:
                print(f"ユニークユーザー数: {user_comments['ユーザー名'].nunique()}")
                
                # レベル分布
                if 'レベル' in user_comments.columns:
                    level_stats = user_comments['レベル'].value_counts().head(5)
                    print("\nレベル分布（上位5位）:")
                    for level, count in level_stats.items():
                        print(f"  Lv.{level}: {count}件")
                
                # 最もコメントの多いユーザー
                print("\n最もコメントの多いユーザー（上位5名）:")
                top_users = user_comments['ユーザー名'].value_counts().head(5)
                for user, count in top_users.items():
                    print(f"  {user}: {count}件")
            
            print(f"\n最初のコメント時間: {df['タイムスタンプ'].iloc[0]}")
            print(f"最後のコメント時間: {df['タイムスタンプ'].iloc[-1]}")
            
            print("\n最新の5件のコメント:")
            recent_comments = df.tail(5)
            for _, row in recent_comments.iterrows():
                if row['コメントタイプ'] == 'system':
                    print(f"  {row['タイムスタンプ']} - [運営] {row['コメント']}")
                else:
                    print(f"  {row['タイムスタンプ']} - {row['ユーザー名']}(Lv.{row['レベル']}): {row['コメント']}")

def extract_and_save_comments(driver, output_file="pococha_comments.csv"):
    """
    コメントを抽出してCSVに保存し、結果を分析する
    """
    comments_data = []
    
    try:
        # コメント領域を取得
        comment_area = driver.find_element(By.CSS_SELECTOR, "div.messages_messagesWrapper__l2Aus")
        comment_items = comment_area.find_elements(By.CSS_SELECTOR, "div.messages_messagesItem__PpIZU")
        
        print(f"抽出対象のコメント数: {len(comment_items)}件")
        
        for item in comment_items:
            comment_data = extract_single_comment(item)
            
            if comment_data and comment_data['comment']:
                # タイムスタンプを追加
                comment_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                comments_data.append(comment_data)
                
                # リアルタイム表示
                if comment_data['type'] == 'system':
                    print(f"{comment_data['timestamp']} - [運営] {comment_data['comment']}")
                else:
                    print(f"{comment_data['timestamp']} - {comment_data['username']}(Lv.{comment_data['level']}): {comment_data['comment']}")
        
        # CSVに保存
        save_comments_to_csv(comments_data, output_file)
        
        # 結果を分析
        analyze_csv_results(output_file)
        
        return len(comments_data)
        
    except Exception as e:
        print(f"コメント抽出・保存でエラー: {e}")
        return 0

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # 全ての前処理
        # ...
        
        # コメント領域を確認
        comment_area = find_comment_area(driver)
        if comment_area:
            # コメントを抽出してCSVに保存
            total_comments = extract_and_save_comments(driver)
            print(f"\n処理完了：合計 {total_comments} 件のコメントを抽出しました")
        
    finally:
        input("結果を確認してからEnterキーを押してください...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**CSV保存の利点**:
- 後で詳細分析が可能
- Excelなどで開いて確認できる
- データの永続化
- 統計情報の自動生成

## 11. 継続的にコメントを監視する

一定時間、継続的にコメントを監視し、新しいコメントのみを抽出する機能を追加します。

```python
# pococha_comment_extractor.py

def monitor_comments_continuously(driver, duration_minutes=10, output_file="pococha_comments.csv"):
    """
    指定時間の間、継続的にコメントを監視する
    """
    print(f"コメントの継続監視を開始します（{duration_minutes}分間）")
    
    # CSVファイルの準備
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'レベル', 'コメント', 'コメントタイプ'])
        
        # 前回取得したコメントを記録するセット
        previous_comments = set()
        total_comments = 0
        
        # 終了時間を計算
        end_time = time.time() + (duration_minutes * 60)
        
        print("監視を開始しました...")
        
        while time.time() < end_time:
            try:
                # コメント領域を毎回取得し直す
                comment_area = driver.find_element(By.CSS_SELECTOR, "div.messages_messagesWrapper__l2Aus")
                comment_items = comment_area.find_elements(By.CSS_SELECTOR, "div.messages_messagesItem__PpIZU")
                
                new_comments_count = 0
                
                for item in comment_items:
                    comment_data = extract_single_comment(item)
                    
                    if comment_data and comment_data['comment']:
                        # ユニークな識別子を作成
                        comment_id = f"{comment_data['username']}:{comment_data['comment']}:{comment_data['level']}"
                        
                        # 新しいコメントのみを処理
                        if comment_id not in previous_comments:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # CSVに書き込み
                            writer.writerow([
                                timestamp,
                                comment_data['username'],
                                comment_data['level'],
                                comment_data['comment'],
                                comment_data['type']
                            ])
                            file.flush()  # すぐにファイルに書き込む
                            
                            previous_comments.add(comment_id)
                            new_comments_count += 1
                            total_comments += 1
                            
                            # コンソールに表示
                            if comment_data['type'] == 'system':
                                print(f"{timestamp} - [運営] {comment_data['comment']}")
                            else:
                                print(f"{timestamp} - {comment_data['username']}(Lv.{comment_data['level']}): {comment_data['comment']}")
                
                if new_comments_count > 0:
                    print(f"🔄 {new_comments_count}件の新しいコメントを検出。合計: {total_comments}件")
                
                # 残り時間を表示
                remaining_time = int((end_time - time.time()) / 60)
                if remaining_time >= 0:
                    print(f"⏰ 残り時間: {remaining_time}分")
                
            except Exception as e:
                print(f"監視中にエラー: {e}")
            
            # 次のチェックまで待機
            time.sleep(3)
        
        print(f"\n✅ 監視完了！合計 {total_comments} 件のコメントを {output_file} に保存しました")
        return total_comments

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # 全ての前処理（ログイン、ダイアログ、再生ボタン等）
        # ...
        
        # コメント領域を確認
        comment_area = find_comment_area(driver)
        if comment_area:
            # 継続的な監視を開始（例：5分間）
            total_comments = monitor_comments_continuously(driver, duration_minutes=5)
            print(f"最終結果：{total_comments} 件のコメントを抽出しました")
            
            # 結果を分析
            analyze_csv_results("pococha_comments.csv")
        
    finally:
        input("全ての処理が完了しました。Enterキーで終了...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**継続監視の特徴**:
- 新しいコメントのみを検出（重複排除）
- リアルタイムでCSVに保存
- 進行状況の表示
- 指定時間での自動終了

## 12. JavaScript を使った堅牢な抽出

Selenium でよく発生する "stale element reference" エラーを回避し、より安定したコメント抽出を行うため、JavaScript を使用します。

```python
# pococha_comment_extractor.py

def extract_comments_with_javascript(driver):
    """
    JavaScriptを使ってコメントデータを抽出する（stale element対策）
    """
    driver.execute_script("""
    (function() {
        window.commentData = [];
        var messageItems = document.querySelectorAll("div.messages_messagesItem__PpIZU");
        
        for (var i = 0; i < messageItems.length; i++) {
            var item = messageItems[i];
            var messageWrapper = item.querySelector("div.messages_messageWrapper__cF93S");
            if (!messageWrapper) continue;
            
            var messageBody = messageWrapper.querySelector("div.common-message-styles_messageBody__89Pbc");
            if (!messageBody) continue;
            
            // 運営からのお知らせかチェック
            var isSystemMessage = messageBody.classList.contains("live-news-message_info__L_ooM");
            
            if (isSystemMessage) {
                // 運営からのお知らせの場合
                var messageText = messageBody.querySelector("span");
                if (messageText) {
                    window.commentData.push({
                        username: "運営",
                        level: "",
                        comment: messageText.textContent.trim(),
                        type: "system"
                    });
                }
            } else {
                // 一般ユーザーのコメントの場合
                var nameWrapper = messageBody.querySelector("span.name_wrapper__jpk5P");
                var username = "不明";
                var level = "";
                
                if (nameWrapper) {
                    var nameElement = nameWrapper.querySelector("span.name_name__1stkJ");
                    if (nameElement) {
                        username = nameElement.textContent.trim();
                    }
                    
                    var levelElement = nameWrapper.querySelector("span.name_level__dHiJG");
                    if (levelElement) {
                        level = levelElement.textContent.trim();
                    }
                }
                
                // コメントテキストを取得（ユーザー名の後のspan要素）
                var commentSpans = messageBody.querySelectorAll("span");
                var commentText = "";
                for (var j = 0; j < commentSpans.length; j++) {
                    var span = commentSpans[j];
                    if (!span.classList.contains("name_wrapper__jpk5P") && 
                        !span.closest(".name_wrapper__jpk5P")) {
                        commentText = span.textContent.trim();
                        break;
                    }
                }
                
                if (commentText) {
                    window.commentData.push({
                        username: username,
                        level: level,
                        comment: commentText,
                        type: "user"
                    });
                }
            }
        }
    })();
    """)
    
    # JavaScriptから結果を取得
    comment_data = driver.execute_script("return window.commentData;")
    return comment_data if comment_data else []

def monitor_comments_with_javascript(driver, duration_minutes=10, output_file="pococha_comments.csv"):
    """
    JavaScriptを使った堅牢なコメント監視
    """
    print(f"JavaScript を使った継続監視を開始します（{duration_minutes}分間）")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'レベル', 'コメント', 'コメントタイプ'])
        
        previous_comments = set()
        total_comments = 0
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                # JavaScriptでコメントデータを抽出
                comment_data_list = extract_comments_with_javascript(driver)
                
                new_comments_count = 0
                
                for comment_data in comment_data_list:
                    if comment_data and comment_data.get('comment'):
                        # ユニークな識別子を作成
                        comment_id = f"{comment_data['username']}:{comment_data['comment']}:{comment_data['level']}"
                        
                        # 新しいコメントのみを処理
                        if comment_id not in previous_comments:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            writer.writerow([
                                timestamp,
                                comment_data['username'],
                                comment_data['level'],
                                comment_data['comment'],
                                comment_data['type']
                            ])
                            file.flush()
                            
                            previous_comments.add(comment_id)
                            new_comments_count += 1
                            total_comments += 1
                            
                            # 表示
                            if comment_data['type'] == 'system':
                                print(f"{timestamp} - [運営] {comment_data['comment']}")
                            else:
                                print(f"{timestamp} - {comment_data['username']}(Lv.{comment_data['level']}): {comment_data['comment']}")
                
                if new_comments_count > 0:
                    print(f"🔄 {new_comments_count}件の新しいコメントを検出。合計: {total_comments}件")
                
            except Exception as e:
                print(f"監視中にエラー: {e}")
            
            # 次のチェックまで待機
            time.sleep(2)
        
        print(f"\n✅ 監視完了！合計 {total_comments} 件のコメントを {output_file} に保存しました")
        return total_comments

def main():
    # 前のコードと同じ部分
    # ...
    
    try:
        # 全ての前処理
        # ...
        
        # コメント領域を確認
        comment_area = find_comment_area(driver)
        if comment_area:
            # JavaScript を使った継続監視
            total_comments = monitor_comments_with_javascript(driver, duration_minutes=5)
            
            # 結果分析
            analyze_csv_results("pococha_comments.csv")
        
    finally:
        input("全ての処理が完了しました。Enterキーで終了...")
        driver.quit()

if __name__ == "__main__":
    main()
```

**JavaScript 使用の利点**:
- stale element reference エラーを回避
- より高速な処理
- DOM操作の安定性向上
- ブラウザネイティブの処理

## 13. コマンドライン引数とデバッグ機能

スクリプトをより実用的にするため、コマンドライン引数とデバッグ機能を追加します。

```python
# pococha_comment_extractor.py
import argparse

def add_debug_functionality(driver, debug=False):
    """
    デバッグ機能を追加
    """
    if debug:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"debug_screenshot_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 デバッグ用スクリーンショット保存: {screenshot_path}")
        
        # 現在のページ情報を表示
        print(f"🌐 現在のURL: {driver.current_url}")
        print(f"📄 ページタイトル: {driver.title}")

def extract_pococha_comments(stream_url, duration_minutes=10, output_file="pococha_comments.csv", headless=False, debug=False):
    """
    Pocochaコメント抽出のメイン関数
    """
    print("Pocochaコメント抽出を開始します...")
    print(f"対象URL: {stream_url}")
    print(f"実行時間: {duration_minutes}分")
    print(f"出力ファイル: {output_file}")
    print(f"ヘッドレスモード: {'有効' if headless else '無効'}")
    print(f"デバッグモード: {'有効' if debug else '無効'}")
    
    # Chromeの設定
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    if headless:
        print("ヘッドレスモードで実行します")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # ログインページにアクセス
        print("Pocochaのログインページにアクセスしています...")
        driver.get("https://www.pococha.com/ja-jp/login")
        
        if debug:
            add_debug_functionality(driver, debug)
        
        # 手動ログイン
        if not wait_for_manual_login(driver):
            print("ログインに失敗しました。")
            return 0
        
        # ライブストリームページにアクセス
        print(f"ライブストリームページにアクセス: {stream_url}")
        driver.get(stream_url)
        
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        
        if debug:
            add_debug_functionality(driver, debug)
        
        # ダイアログ処理
        handle_pococha_dialogs(driver)
        
        # 再生ボタンクリック
        click_play_button(driver)
        
        # コメント領域確認
        comment_area = find_comment_area(driver)
        if not comment_area:
            print("コメント領域が見つかりません。")
            return 0
        
        # コメント監視開始
        total_comments = monitor_comments_with_javascript(driver, duration_minutes, output_file)
        
        # 結果分析
        analyze_csv_results(output_file)
        
        return total_comments
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        if debug:
            add_debug_functionality(driver, debug)
        return 0
    
    finally:
        driver.quit()

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Pocochaライブストリームからコメントを抽出するツール（手動ログイン版）')
    parser.add_argument('url', help='抽出対象のPocochaライブストリームURL')
    parser.add_argument('-t', '--time', type=int, default=10, 
                        help='抽出時間（分）。デフォルトは10分')
    parser.add_argument('-o', '--output', default='pococha_comments.csv',
                        help='出力CSVファイル名。デフォルトはpococha_comments.csv')
    parser.add_argument('--headless', action='store_true',
                        help='ヘッドレスモードで実行（ブラウザウィンドウを表示しない）')
    parser.add_argument('--debug', action='store_true',
                        help='デバッグモードで実行（詳細なログとスクリーンショットを出力）')
    
    args = parser.parse_args()
    
    # 利用規約の確認
    print("=" * 60)
    print("Pocochaコメント抽出ツール（手動ログイン版）")
    print("=" * 60)
    print("注意事項:")
    print("1. このツールを使用する前に、Pocochaの利用規約を確認してください")
    print("2. 過度なアクセスやスクレイピングは利用規約違反となる可能性があります")
    print("3. 個人的な用途での使用に留めてください")
    print("4. 抽出したデータの取り扱いには十分注意してください")
    print("5. ログインは手動で行ってください（認証情報の保存は不要です）")
    print("=" * 60)
    
    consent = input("上記を理解し、適切に利用することに同意しますか？ (y/N): ")
    if consent.lower() != 'y':
        print("利用を中止します。")
        return
    
    # コメント抽出実行
    total_comments = extract_pococha_comments(
        args.url, 
        args.time, 
        args.output, 
        args.headless, 
        args.debug
    )
    
    print(f"\n🎉 処理完了！合計 {total_comments} 件のコメントを抽出しました")

if __name__ == "__main__":
    main()
```

**コマンドライン機能**:
- 柔軟なパラメータ指定
- デバッグモードでのスクリーンショット保存
- 利用規約の確認
- ヘッドレスモード対応

## 14. 完成版コード

以下が、すべてのステップを統合した完全なコードです：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pocochaライブストリームコメント抽出ツール（手動ログイン版）
注意：このツールを使用する前に、Pocochaの利用規約を確認し、適切な利用を心がけてください。
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import pandas as pd
from datetime import datetime
import os
import argparse

def wait_for_manual_login(driver, debug=False):
    """手動ログインの完了を待機する"""
    try:
        print("=" * 60)
        print("手動ログインが必要です")
        print("=" * 60)
        print("以下の手順でログインしてください：")
        print("1. ブラウザでPocochaにアクセス")
        print("2. お好みの方法でログイン（Google、LINE、Apple ID、メール等）")
        print("3. 2段階認証がある場合は認証コードを入力")
        print("4. ログイン完了後、このターミナルに戻ってEnterキーを押してください")
        print("=" * 60)
        
        if debug:
            screenshot_path = f"debug_before_login_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"ログイン前のスクリーンショット: {screenshot_path}")
        
        input("ログイン完了後、Enterキーを押してください...")
        
        # ログイン状態を確認
        current_url = driver.current_url
        print(f"現在のURL: {current_url}")
        
        if "login" in current_url.lower():
            print("⚠️ まだログインページにいるようです。")
            retry = input("ログインを完了してからもう一度試しますか？ (y/N): ")
            if retry.lower() == 'y':
                return wait_for_manual_login(driver, debug)
            else:
                return False
        
        print("✅ ログインが完了しました！")
        return True
        
    except Exception as e:
        print(f"ログイン確認でエラーが発生しました: {str(e)}")
        return True

def handle_pococha_dialogs(driver, wait, debug=False):
    """Pocochaの各種ダイアログを処理する"""
    try:
        print("Pocochaのダイアログを確認中...")
        
        # Web版Pocochaの説明ダイアログを処理
        try:
            ok_selectors = [
                (By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'ok')]"),
                (By.CSS_SELECTOR, "button[class*='ok']"),
                (By.XPATH, "//button[text()='OK']"),
                (By.CSS_SELECTOR, "button"),  # 最後の手段として全てのボタンを確認
            ]
            
            ok_button = None
            for selector_type, selector_value in ok_selectors:
                try:
                    ok_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    
                    # ボタンのテキストを確認
                    button_text = ok_button.text.strip().lower()
                    if 'ok' in button_text or ok_button.text.strip() == "OK":
                        print(f"Web版Pococha説明ダイアログのOKボタンを発見: {button_text}")
                        break
                    else:
                        ok_button = None
                        continue
                        
                except TimeoutException:
                    continue
            
            if ok_button:
                ok_button.click()
                print("✅ Web版Pococha説明ダイアログのOKボタンをクリックしました。")
                time.sleep(2)
                
                if debug:
                    screenshot_path = f"debug_after_dialog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"ダイアログ処理後のスクリーンショット: {screenshot_path}")
            else:
                print("Web版Pococha説明ダイアログは表示されていないか、既に閉じられています。")
                
        except Exception as e:
            print(f"ダイアログ処理でエラー: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"ダイアログ処理で予期しないエラー: {str(e)}")
        return True

def click_play_button(driver, wait, debug=False):
    """ライブストリームの再生ボタンをクリックする"""
    try:
        print("ライブストリームの再生ボタンを探しています...")
        
        # 再生ボタンのセレクタ
        play_selectors = [
            (By.CSS_SELECTOR, "div.video_playButton__Q_Ecm"),
            (By.CSS_SELECTOR, ".video_playButton__Q_Ecm"),
            (By.XPATH, "//div[contains(@class, 'video_playButton')]"),
            (By.XPATH, "//div[contains(@class, 'playButton')]"),
            (By.CSS_SELECTOR, "div[class*='playButton']"),
            (By.XPATH, "//img[@class='video_icon__OO57P']//parent::div"),
        ]
        
        play_button = None
        for selector_type, selector_value in play_selectors:
            try:
                play_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                print(f"再生ボタンを発見: {selector_type} = {selector_value}")
                break
            except TimeoutException:
                continue
        
        if play_button:
            play_button.click()
            print("✅ ライブストリームの再生ボタンをクリックしました。")
            time.sleep(3)
            
            if debug:
                screenshot_path = f"debug_after_play_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                print(f"再生ボタンクリック後のスクリーンショット: {screenshot_path}")
            
            return True
        else:
            print("⚠️ 再生ボタンが見つかりませんでした。")
            print("利用可能な要素を確認しています...")
            
            # デバッグ: ページ上のクリック可能な要素を確認
            clickable_elements = driver.find_elements(By.XPATH, "//*[@onclick or @click or contains(@class, 'button') or contains(@class, 'btn')]")
            print(f"クリック可能な要素数: {len(clickable_elements)}")
            
            print("手動で再生ボタンをクリックしてください。")
            input("再生開始後、Enterキーを押してください...")
            return True
            
    except Exception as e:
        print(f"再生ボタン処理でエラー: {str(e)}")
        print("手動で再生ボタンをクリックしてください。")
        input("再生開始後、Enterキーを押してください...")
        return True

def extract_pococha_comments(stream_url, duration_minutes=10, output_file="pococha_comments.csv", headless=False, debug=False):
    """指定したPocochaのライブストリームURLからコメントを抽出する"""
    print("Pocochaコメント抽出を開始します...")
    print(f"対象URL: {stream_url}")
    print(f"実行時間: {duration_minutes}分")
    print(f"出力ファイル: {output_file}")
    print(f"ヘッドレスモード: {'有効' if headless else '無効'}")
    print(f"デバッグモード: {'有効' if debug else '無効'}")
    
    # Chromeの設定
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
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
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 20)
    
    # CSVファイルを準備
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['タイムスタンプ', 'ユーザー名', 'レベル', 'コメント', 'コメントタイプ'])
        
        # 前回取得したコメントを記録するセット
        previous_comments = set()
        
        try:
            # Pocochaのログインページにアクセス
            print("Pocochaのログインページにアクセスしています...")
            driver.get("https://www.pococha.com/ja-jp/login")
            
            # 手動ログイン待機
            if not wait_for_manual_login(driver, debug):
                print("ログインに失敗しました。終了します。")
                if debug:
                    screenshot_path = f"debug_login_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"デバッグ用スクリーンショットを保存しました: {screenshot_path}")
                return 0
            
            # ライブストリームページにアクセス
            print(f"ライブストリームページにアクセスしています: {stream_url}")
            driver.get(stream_url)
            
            # ページの読み込み完了を待機
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)
            
            if debug:
                screenshot_path = f"debug_live_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                print(f"ライブページアクセス後のスクリーンショット: {screenshot_path}")
            
            # Pocochaのダイアログ処理
            handle_pococha_dialogs(driver, wait, debug)
            
            # 再生ボタンをクリック
            click_play_button(driver, wait, debug)
            
            # コメント領域が表示されるまで待機
            try:
                print("コメント領域を探しています...")
                comment_wrapper = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.messages_wrapper___xQBv"))
                )
                print("コメント領域を検出しました！")
            except TimeoutException:
                print("コメント領域の検出に失敗しました。")
                print("ページが正しく読み込まれているか確認してください。")
                if debug:
                    screenshot_path = f"debug_no_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"コメント領域未検出時のスクリーンショット: {screenshot_path}")
                return 0
            
            # 指定時間実行
            end_time = time.time() + (duration_minutes * 60)
            total_comments = 0
            
            print(f"コメントの抽出を開始します。{duration_minutes}分間実行します...")
            
            while time.time() < end_time:
                try:
                    # コメント領域を毎回取得し直す (stale element対策)
                    comment_container = driver.find_element(By.CSS_SELECTOR, "div.messages_messagesWrapper__l2Aus")
                    
                    # JavaScriptでコメントデータを抽出
                    driver.execute_script("""
                    (function() {
                        window.commentData = [];
                        var messageItems = document.querySelectorAll("div.messages_messagesItem__PpIZU");
                        
                        for (var i = 0; i < messageItems.length; i++) {
                            var item = messageItems[i];
                            var messageWrapper = item.querySelector("div.messages_messageWrapper__cF93S");
                            if (!messageWrapper) continue;
                            
                            var messageBody = messageWrapper.querySelector("div.common-message-styles_messageBody__89Pbc");
                            if (!messageBody) continue;
                            
                            // 運営からのお知らせかチェック
                            var isSystemMessage = messageBody.classList.contains("live-news-message_info__L_ooM");
                            
                            if (isSystemMessage) {
                                // 運営からのお知らせの場合
                                var messageText = messageBody.querySelector("span");
                                if (messageText) {
                                    window.commentData.push({
                                        username: "運営",
                                        level: "",
                                        comment: messageText.textContent.trim(),
                                        type: "system"
                                    });
                                }
                            } else {
                                // 一般ユーザーのコメントの場合
                                var nameWrapper = messageBody.querySelector("span.name_wrapper__jpk5P");
                                var username = "不明";
                                var level = "";
                                
                                if (nameWrapper) {
                                    var nameElement = nameWrapper.querySelector("span.name_name__1stkJ");
                                    if (nameElement) {
                                        username = nameElement.textContent.trim();
                                    }
                                    
                                    var levelElement = nameWrapper.querySelector("span.name_level__dHiJG");
                                    if (levelElement) {
                                        level = levelElement.textContent.trim();
                                    }
                                }
                                
                                // コメントテキストを取得（ユーザー名の後のspan要素）
                                var commentSpans = messageBody.querySelectorAll("span");
                                var commentText = "";
                                for (var j = 0; j < commentSpans.length; j++) {
                                    var span = commentSpans[j];
                                    if (!span.classList.contains("name_wrapper__jpk5P") && 
                                        !span.closest(".name_wrapper__jpk5P")) {
                                        commentText = span.textContent.trim();
                                        break;
                                    }
                                }
                                
                                if (commentText) {
                                    window.commentData.push({
                                        username: username,
                                        level: level,
                                        comment: commentText,
                                        type: "user"
                                    });
                                }
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
                            level = item.get('level', '')
                            comment_text = item.get('comment', '')
                            comment_type = item.get('type', 'user')
                            
                            # 空のコメントはスキップ
                            if not comment_text:
                                continue
                            
                            # ユニークな識別子を作成
                            comment_id = f"{username}:{comment_text}:{level}"
                            
                            # 新しいコメントのみを処理
                            if comment_id not in previous_comments:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                writer.writerow([timestamp, username, level, comment_text, comment_type])
                                file.flush()  # すぐにファイルに書き込む
                                previous_comments.add(comment_id)
                                new_comments_count += 1
                                total_comments += 1
                                
                                # コンソールに表示
                                if comment_type == "system":
                                    print(f"{timestamp} - [運営] {comment_text}")
                                else:
                                    print(f"{timestamp} - {username}(Lv.{level}): {comment_text}")
                    
                    if new_comments_count > 0:
                        print(f"{new_comments_count}件の新しいコメントを検出しました。合計: {total_comments}件")
                    
                except Exception as e:
                    print(f"エラーが発生しました: {str(e)}")
                    if debug:
                        screenshot_path = f"debug_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        driver.save_screenshot(screenshot_path)
                        print(f"エラー時のスクリーンショット: {screenshot_path}")
                
                # 次のチェックまで待機
                time.sleep(2)
                
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
            user_comments = df[df['コメントタイプ'] == 'user']
            system_comments = df[df['コメントタイプ'] == 'system']
            
            print(f"ユーザーコメント数: {len(user_comments)}")
            print(f"運営メッセージ数: {len(system_comments)}")
            
            if len(user_comments) > 0:
                print(f"ユニークユーザー数: {user_comments['ユーザー名'].nunique()}")
                
                # トップユーザーの表示
                print("\n最もコメントの多いユーザー（上位5名）:")
                top_users = user_comments['ユーザー名'].value_counts().head(5)
                for user, count in top_users.items():
                    print(f"{user}: {count}件")
            
            print(f"\n最初のコメント時間: {df['タイムスタンプ'].iloc[0]}")
            print(f"最後のコメント時間: {df['タイムスタンプ'].iloc[-1]}")
            print("\n最新の5件のコメント:")
            print(df.tail(5)[['タイムスタンプ', 'ユーザー名', 'レベル', 'コメント']])
    
    return total_comments

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Pocochaライブストリームからコメントを抽出するツール（手動ログイン版）')
    parser.add_argument('url', help='抽出対象のPocochaライブストリームURL')
    parser.add_argument('-t', '--time', type=int, default=10, 
                        help='抽出時間（分）。デフォルトは10分')
    parser.add_argument('-o', '--output', default='pococha_comments.csv',
                        help='出力CSVファイル名。デフォルトはpococha_comments.csv')
    parser.add_argument('--headless', action='store_true',
                        help='ヘッドレスモードで実行（ブラウザウィンドウを表示しない）')
    parser.add_argument('--debug', action='store_true',
                        help='デバッグモードで実行（詳細なログとスクリーンショットを出力）')
    
    args = parser.parse_args()
    
    # 利用規約の確認
    print("=" * 60)
    print("Pocochaコメント抽出ツール（手動ログイン版）")
    print("=" * 60)
    print("注意事項:")
    print("1. このツールを使用する前に、Pocochaの利用規約を確認してください")
    print("2. 過度なアクセスやスクレイピングは利用規約違反となる可能性があります")
    print("3. 個人的な用途での使用に留めてください")
    print("4. 抽出したデータの取り扱いには十分注意してください")
    print("5. ログインは手動で行ってください（認証情報の保存は不要です）")
    print("=" * 60)
    
    consent = input("上記を理解し、適切に利用することに同意しますか？ (y/N): ")
    if consent.lower() != 'y':
        print("利用を中止します。")
        return
    
    # 引数から値を取得
    target_url = args.url
    duration_min = args.time
    output_file = args.output
    headless_mode = args.headless
    debug_mode = args.debug
    
    # コメント抽出実行
    extract_pococha_comments(target_url, duration_min, output_file, headless_mode, debug_mode)

if __name__ == "__main__":
    main()
```

## 15. 使用方法とトラブルシューティング

### 基本的な使用方法

```bash
# 基本的な実行（10分間）
python pococha_comment_extractor.py "https://www.pococha.com/ja-jp/app/lives/67761158"

# 抽出時間を指定（30分間）
python pococha_comment_extractor.py -t 30 "https://www.pococha.com/ja-jp/app/lives/67761158"

# デバッグモードで実行（推奨）
python pococha_comment_extractor.py --debug "https://www.pococha.com/ja-jp/app/lives/67761158"

# ヘッドレスモードで実行
python pococha_comment_extractor.py --headless "https://www.pococha.com/ja-jp/app/lives/67761158"

# カスタムファイル名で保存
python pococha_comment_extractor.py -o "my_comments.csv" "https://www.pococha.com/ja-jp/app/lives/67761158"
```

### 実行フロー

1. **ツール起動** → 利用規約確認
2. **ブラウザ起動** → Chromeが自動で開く
3. **手動ログイン** → お好みの方法でログイン
4. **自動処理**:
   - ライブページアクセス
   - ダイアログ処理
   - 再生ボタンクリック
   - コメント抽出開始
5. **結果保存** → CSVファイルに保存
6. **分析表示** → 統計情報を表示

### よくあるトラブルと解決方法

#### 1. ログインできない
**症状**: ログインページでエラーが発生
**解決方法**:
- 正しいアカウント情報を使用
- 2段階認証を正しく入力
- ブラウザのキャッシュをクリア

#### 2. 再生ボタンが見つからない
**症状**: 再生ボタンの自動クリックに失敗
**解決方法**:
- 手動で再生ボタンをクリック
- ライブが実際に配信中か確認
- デバッグモードで要素を確認

#### 3. コメントが取得できない
**症状**: コメント領域は見つかるがコメントが0件
**解決方法**:
- ライブが実際にアクティブか確認
- 再生が正常に開始されているか確認
- しばらく待ってからコメントが流れるか確認

#### 4. ブラウザエラー
**症状**: ChromeDriverに関するエラー
**解決方法**:
```bash
# Chromeを最新版に更新
# パッケージを再インストール
pip uninstall selenium webdriver-manager
pip install selenium webdriver-manager
```

### デバッグのコツ

```bash
# デバッグモードで詳細情報を取得
python pococha_comment_extractor.py --debug "URL"

# 生成されるファイル：
# - debug_before_login_20241201_123456.png
# - debug_live_page_20241201_123457.png
# - debug_after_dialog_20241201_123458.png
# - debug_after_play_20241201_123459.png
```

## 16. さらなる学習のためのチャレンジ

### 初級チャレンジ
1. **コメント頻度の可視化**: matplotlib を使ってコメント頻度をグラフ化
2. **感情分析**: コメントの感情（ポジティブ/ネガティブ）を分析
3. **ユーザーレベル分析**: ユーザーレベルとコメント数の関係を調査

### 中級チャレンジ
4. **リアルタイム通知**: 特定のキーワードを含むコメントが投稿されたらアラート
5. **コメント予測**: 過去のデータを使って将来のコメント数を予測
6. **多言語対応**: 英語や他の言語のコメントに対応

### 上級チャレンジ
7. **機械学習**: コメント内容からライブの人気度を予測
8. **データベース連携**: PostgreSQLやMongoDBにデータを保存
9. **Web API化**: FlaskやFastAPIでコメント抽出をAPI化
10. **複数ライブ対応**: 複数のライブストリームを同時に監視

### プロジェクト例

```python
# 感情分析の例
from textblob import TextBlob

def analyze_sentiment(comment):
    blob = TextBlob(comment)
    return blob.sentiment.polarity

# 使用例
df['感情スコア'] = df['コメント'].apply(analyze_sentiment)
```

このチュートリアルを通じて、Pocochaのコメント抽出だけでなく、Webスクレイピングとデータ分析の実践的なスキルを身につけることができました。これらの技術は他のプラットフォームやプロジェクトにも応用できる貴重な経験となるでしょう。

## Pocochaとwhowatchの技術的な違い

| 項目 | Pococha | whowatch |
|------|---------|----------|
| 認証 | 必須（手動ログイン） | 不要 |
| ダイアログ | Web版説明あり | なし |
| 再生操作 | 再生ボタンクリック必須 | 自動再生 |
| HTML構造 | ハッシュ付きクラス名 | シンプルなクラス名 |
| コメント形式 | ユーザー名+レベル+コメント | ユーザー名+コメント |
| セキュリティ | 高（bot検出あり） | 標準 |

この違いを理解することで、他のライブストリーミングプラットフォームにも応用できる柔軟性を身につけることができます。