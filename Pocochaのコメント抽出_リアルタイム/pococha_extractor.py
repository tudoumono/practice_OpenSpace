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
    """
    手動ログインの完了を待機する
    
    Parameters:
        driver: Selenium WebDriver
        debug: デバッグモード
    
    Returns:
        bool: ログイン完了確認
    """
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
    """
    Pocochaの各種ダイアログを処理する
    
    Parameters:
        driver: Selenium WebDriver
        wait: WebDriverWait オブジェクト
        debug: デバッグモード
    
    Returns:
        bool: 処理成功
    """
    try:
        print("Pocochaのダイアログを確認中...")
        
        # Web版Pocochaの説明ダイアログを処理
        try:
            # 「Web版Pocochaへようこそ」ダイアログのOKボタンを探す
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
    """
    ライブストリームの再生ボタンをクリックする
    
    Parameters:
        driver: Selenium WebDriver
        wait: WebDriverWait オブジェクト
        debug: デバッグモード
    
    Returns:
        bool: 再生ボタンクリック成功
    """
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
    """
    指定したPocochaのライブストリームURLからコメントを抽出する
    
    Parameters:
        stream_url (str): Pocochaのライブストリーム URL
        duration_minutes (int): 抽出を実行する時間（分）
        output_file (str): 出力するCSVファイル名
        headless (bool): ヘッドレスモードを使用するかどうか
        debug (bool): デバッグモードを使用するかどうか
    
    Returns:
        int: 抽出したコメントの総数
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
    # コマンドライン引数の設定
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
    
    # 引数を解析
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