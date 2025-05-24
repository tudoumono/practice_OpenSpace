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