# Twitch Chat Scorer Bot

このPythonボットは、Twitchのライブチャットをリアルタイムで取得し、Google Gemini APIを使用して各メッセージの感情と盛り上がり度を分析し、その結果をコンソールに出力します。

## 目次

1.  [機能](https://www.google.com/search?q=%231-%E6%A9%9F%E8%83%BD)
2.  [必要なもの](https://www.google.com/search?q=%232-%E5%BF%85%E8%A6%81%E3%81%AA%E3%82%82%E3%81%AE)
3.  [セットアップ](https://www.google.com/search?q=%233-%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)
      * [3.1 Python開発環境の準備](https://www.google.com/search?q=%2331-python%E9%96%8B%E7%99%BA%E7%92%B0%E5%A2%83%E3%81%AE%E6%BA%96%E5%82%99)
      * [3.2 依存ライブラリのインストール](https://www.google.com/search?q=%2332-%E4%BE%9D%E5%AD%98%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB)
      * [3.3 Twitch OAuthトークンの取得](https://www.google.com/search?q=%2333-twitch-oauth%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%81%AE%E5%8F%96%E5%BE%97)
      * [3.4 Gemini APIキーの取得](https://www.google.com/search?q=%2334-gemini-api%E3%82%AD%E3%83%BC%E3%81%AE%E5%8F%96%E5%BE%97)
4.  [設定ファイル (`.secret`) または環境変数の準備](https://www.google.com/search?q=%234-%E8%A8%AD%E5%AE%9A%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB-secret-%E3%81%BE%E3%81%9F%E3%81%AF%E7%92%B0%E5%A2%83%E5%A4%89%E6%95%B0%E3%81%AE%E6%BA%96%E5%82%99)
      * [4.1 `.secret` ファイルを使用する場合 (推奨)](https://www.google.com/search?q=%2341-secret-%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B%E5%A0%B4%E5%90%88-%E6%8E%A8%E5%A5%A8)
      * [4.2 環境変数を使用する場合](https://www.google.com/search?q=%2342-%E7%92%B0%E5%A2%83%E5%A4%89%E6%95%B0%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B%E5%A0%B4%E5%90%88)
5.  [ボットの実行](https://www.google.com/search?q=%235-%E3%83%9C%E3%83%83%E3%83%88%E3%81%AE%E5%AE%9F%E8%A1%8C)
6.  [コマンド例](https://www.google.com/search?q=%236-%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89%E4%BE%8B)
7.  [コストについて](https://www.google.com/search?q=%237-%E3%82%B3%E3%82%B9%E3%83%88%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6)

-----

## 1\. 機能

  * 指定したTwitchチャンネルのチャットメッセージをリアルタイムで取得。
  * 取得したチャットメッセージをGoogle Gemini APIに送信し、感情（ポジティブ、ネガティブ、ニュートラル、不明）と盛り上がり度（10点満点）を分析。
  * 分析結果（感情、スコア、理由）をコンソールに表示。
  * 設定情報を環境変数または安全な `.secret` ファイルから読み込み。

-----

## 2\. 必要なもの

  * Python 3.10以降 (推奨: Python 3.13)
  * Twitchアカウント (ボット用のアカウント推奨)
  * Google Cloud Platformアカウント (Gemini APIの利用のため)

-----

## 3\. セットアップ

### 3.1 Python開発環境の準備

まず、プロジェクトディレクトリを作成し、Pythonの仮想環境を設定します。

```bash
# プロジェクトディレクトリを作成
mkdir twitch-chat-scorer
cd twitch-chat-scorer

# uv を使って仮想環境を作成
uv venv

# 仮想環境をアクティベート
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

### 3.2 依存ライブラリのインストール

仮想環境をアクティベートした状態で、必要なライブラリをインストールします。

```bash
uv pip install twitchio google-generativeai pyyaml
```

### 3.3 Twitch OAuthトークンの取得

Twitch IRCに接続するには、`oauth:` から始まるOAuthトークンが必要です。

1.  [Twitch Developer Console](https://dev.twitch.tv/console/) にログインします。
2.  「**Applications**」から「**Register Your Application**」をクリックし、新しいアプリケーションを登録します。
      * **Name:** 任意のアプリケーション名 (例: `ChatScorerBot`)
      * **OAuth Redirect URLs:** `http://localhost:8000` を追加します。
      * **Category:** `Chat Bot` を選択。
3.  登録後、「**Manage**」をクリックし、表示される「**Client ID**」を控えておきます。
4.  以下のURLの `YOUR_CLIENT_ID` と `YOUR_REDIRECT_URI` を置き換え、ブラウザでアクセスします。
    ```
    https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=chat%3Aread+chat%3Aedit
    ```
    (例: `https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=abcdef1234567890&redirect_uri=http://localhost:8000&scope=chat%3Aread+chat%3Aedit`)
5.  Twitchの認証画面で「Authorize」をクリックし、許可します。
6.  リダイレクトされたURLの `#access_token=` の後に続く文字列が、あなたのOAuthトークンです。これをコピーします。**必ず `oauth:` を頭に付けて使用します**。

### 3.4 Gemini APIキーの取得

チャット分析のためにGoogle Gemini APIキーが必要です。

1.  [Google Cloud Console](https://console.cloud.google.com/) にログインします。
2.  新しいプロジェクトを作成するか、既存のプロジェクトを選択します。
3.  左メニューで「**Vertex AI**」を検索し、移動します。
4.  Vertex AIダッシュボードで「**API の有効化**」をクリックし、「**Vertex AI API**」を有効にします。
5.  左メニューで「**認証情報**」を選択し、「**認証情報を作成**」\>「**API キー**」をクリックします。
6.  生成されたAPIキーをコピーし、安全な場所に保存します。

-----

## 4\. 設定ファイル (`.secret`) または環境変数の準備

このボットは、TwitchのOAuthトークンとチャンネル名、Gemini APIキーの3つの設定値を必要とします。これらの設定は、**環境変数**または\*\*`.secret` ファイル\*\*のいずれかから読み込まれます。

**推奨は `.secret` ファイルを使用する方法です。** これにより、Gitリポジトリに機密情報が誤ってコミットされるのを防ぎつつ、設定をファイルで管理できます。

### 4.1 `.secret` ファイルを使用する場合 (推奨)

プロジェクトのルートディレクトリ (`twitch-chat-scorer/`) に `.secret` という名前のファイルを作成し、以下の内容を記述します。`YOUR_TWITCH_OAUTH_TOKEN_HERE`、`YOUR_CHANNEL_NAME_HERE`、`YOUR_GEMINI_API_KEY_HERE` を取得した実際の値に置き換えてください。

```yaml
# .secret
twitch:
  oauth_token: "oauth:YOUR_TWITCH_OAUTH_TOKEN_HERE"
  channel_name: "YOUR_CHANNEL_NAME_HERE" # 監視したいTwitchチャンネル名（例: "shroud"）

gemini:
  api_key: "YOUR_GEMINI_API_KEY_HERE"
```

**重要:** `.secret` ファイルはGitにコミットされないよう、プロジェクトのルートディレクトリに `.gitignore` ファイルを作成し、以下の行を追加してください。

```gitignore
# .gitignore

# Python 仮想環境
.venv/
venv/
env/

# コンパイルされたPythonファイル
__pycache__/
*.pyc
*.pyo

# IDE specific files
.idea/
.vscode/

# 設定ファイルや秘密情報 (非常に重要!)
.secret
*.env
```

### 4.2 環境変数を使用する場合

`bot.py` が実行される前に、以下の環境変数を設定します。

**Windows (PowerShell)**

```powershell
$env:TWITCH_OAUTH_TOKEN="oauth:YOUR_TWITCH_OAUTH_TOKEN_HERE"
$env:TWITCH_CHANNEL_NAME="YOUR_CHANNEL_NAME_HERE"
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

**macOS / Linux (Bash/Zsh)**

```bash
export TWITCH_OAUTH_TOKEN="oauth:YOUR_TWITCH_OAUTH_TOKEN_HERE"
export TWITCH_CHANNEL_NAME="YOUR_CHANNEL_NAME_HERE"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

**注意点:**

  * 上記の設定方法は、現在のターミナルセッションでのみ有効です。永続化したい場合は、システムの環境変数として設定するか、`.bashrc` / `.zshrc` / PowerShellプロファイルなどに記述する必要があります。
  * `.secret` ファイルと環境変数が両方設定されている場合、**環境変数が優先されます**。

-----

## 5\. ボットの実行

設定が完了したら、仮想環境がアクティベートされていることを確認し、ボットを起動します。

```bash
python bot.py
```

ボットが正常にTwitchに接続されると、コンソールにメッセージが表示され、指定したチャンネルのチャットが流れ始め、各メッセージの分析結果が出力されます。

```
Twitch にログインしました | ユーザー名: your_bot_name
チャンネル: your_channel_name を監視中
[your_channel_name] user1: こんにちは！
  [Gemini分析] 感情: ポジティブ, 盛り上がり度: 7/10, 理由: 挨拶とポジティブな内容
[your_channel_name] user2: 草
  [Gemini分析] 感情: ポジティブ, 盛り上がり度: 8/10, 理由: 笑いを表すスラングで盛り上がっている
```

-----

## 6\. コマンド例

ボットはチャット内で `!` から始まる簡単なコマンドに応答するように設定されています。

  * `!hello`: ボットが「Hello {ユーザー名}\!」と応答します。

-----

## 7\. コストについて

Gemini APIの利用にはGoogle Cloudの料金が発生します。使用するモデル（`gemini-1.5-flash` または `gemini-1.5-pro`）とトークン数に応じて課金されます。

  * **料金の確認:** Google Cloud Consoleの「お支払い」セクションで、現在の利用状況と費用を確認できます。
      * [Google Cloud Billing Reports](https://console.cloud.google.com/billing/reports)
  * **無料枠:** Gemini APIには無料枠が提供されていることがありますが、それを超えると課金されます。
  * **予算とアラート:** 予期せぬ高額請求を防ぐため、Google Cloud Consoleの「お支払い」\>「予算とアラート」で予算を設定し、通知を受け取るように強く推奨します。

