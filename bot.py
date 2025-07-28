import twitchio
from twitchio.ext import commands
import asyncio
import os
import json
import yaml
import google.generativeai as genai # 追加: Gemini SDK

# --- 設定の読み込み ---
# 優先順位: 環境変数 -> .secretファイル -> デフォルト値 (デフォルト値は基本使わないように警告を出す)

TWITCH_OAUTH_TOKEN = None
TWITCH_CHANNEL_NAME = None
GEMINI_API_KEY = None # 後でGemini用に追加

def load_config():
    global TWITCH_OAUTH_TOKEN, TWITCH_CHANNEL_NAME, GEMINI_API_KEY
    
    # 1. 環境変数からの読み込みを試みる
    TWITCH_OAUTH_TOKEN = os.environ.get('TWITCH_OAUTH_TOKEN')
    TWITCH_CHANNEL_NAME = os.environ.get('TWITCH_CHANNEL_NAME')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # 2. 環境変数にない場合、.secret ファイルからの読み込みを試みる
    # 両方に設定されていない場合のみ、.secretファイルを読む
    if (not TWITCH_OAUTH_TOKEN or not TWITCH_CHANNEL_NAME or not GEMINI_API_KEY) and os.path.exists('.secret'):
        try:
            # ここを修正: encoding='utf-8' を追加
            with open('.secret', 'r', encoding='utf-8') as f:
                secret_config = yaml.safe_load(f)
                if secret_config:
                    # 環境変数で設定されていない場合のみ、.secretから読み込む
                    if not TWITCH_OAUTH_TOKEN:
                        TWITCH_OAUTH_TOKEN = secret_config.get('twitch', {}).get('oauth_token')
                    if not TWITCH_CHANNEL_NAME:
                        TWITCH_CHANNEL_NAME = secret_config.get('twitch', {}).get('channel_name')
                    if not GEMINI_API_KEY:
                        GEMINI_API_KEY = secret_config.get('gemini', {}).get('api_key')
        except yaml.YAMLError as e:
            print(f"警告: .secret ファイルのYAML構文エラーが発生しました: {e}")
        except Exception as e:
            # より具体的なエラーメッセージのために、元の例外をログに出す
            print(f"警告: .secret ファイルの読み込み中に予期せぬエラーが発生しました: {e}")

# 設定をロード
load_config()

# --- Gemini APIキーの設定 ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("警告: Gemini APIキーが設定されていないため、チャット分析はスキップされます。")

async def process_gemini_analysis(message_content: str):
    """
    Gemini APIを使用してチャットメッセージの感情と盛り上がり度を分析します。
    """
    if not GEMINI_API_KEY:
        # APIキーがない場合は処理しない
        return None

    # 使用するモデルを指定 (コストと性能のバランスを考慮して選択)
    # ライブチャットのリアルタイム分析には 'gemini-1.5-flash' が推奨されます。
    # より高度な分析が必要なら 'gemini-1.5-pro' も検討。
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    以下のTwitchチャットメッセージについて、感情と盛り上がり度を採点してください。
    - 感情は「ポジティブ」「ネガティブ」「ニュートラル」「不明」の中から最も適切なものを選んでください。
    - 盛り上がり度は10点満点（1が最低、10が最高）で評価してください。
    - 出力はJSON形式でお願いします。
    - Twitch特有の表現（例: 草、ｗ、GG、POG、スタンプなど）も考慮して判断してください。

    メッセージ: "{message_content}"

    JSON形式の例:
    {{
        "sentiment": "ポジティブ",
        "excitement_score": 8,
        "reason": "楽しい雰囲気の絵文字とポジティブなコメントが多い"
    }}
    """
    try:
        # generate_content_async を使って非同期でAPIを呼び出す
        response = await model.generate_content_async(prompt)
        
        # レスポンスからテキスト部分を取得し、JSONとしてパース
        # GeminiがたまにJSONの前に余計なテキストを付加することがあるので、strip()で空白除去
        response_text = response.text.strip()

        # コードブロックで囲まれている場合（例: ```json...```）はそれを取り除く
        if response_text.startswith('```json') and response_text.endswith('```'):
            response_text = response_text[len('```json'):-len('```')].strip()
        elif response_text.startswith('```') and response_text.endswith('```'):
            response_text = response_text[len('```'):-len('```')].strip()

        # json.loads()でJSON文字列をPython辞書に変換
        analysis_result = json.loads(response_text)
        return analysis_result
    except Exception as e:
        print(f"Gemini分析エラー（メッセージ: '{message_content[:50]}...'）: {e}")
        # デバッグのためにGeminiの生レスポンスも表示すると良い場合がある
        # print(f"Gemini生レスポンス: {response.text}")
        return None

class TwitchChatBot(commands.Bot):
    def __init__(self):
        # OAuthトークンは 'oauth:' から始まる必要があります
        if TWITCH_OAUTH_TOKEN and not TWITCH_OAUTH_TOKEN.startswith('oauth:'):
            print("警告: TWITCH_OAUTH_TOKENは 'oauth:' で始まる必要があります。")
            print("正しく設定されていない場合、ボットは接続できません。")

        super().__init__(
            token=TWITCH_OAUTH_TOKEN,
            prefix='!', # コマンドのプレフィックス (例: !hello)
            initial_channels=[TWITCH_CHANNEL_NAME]
        )

    async def event_ready(self):
        """ボットがTwitchに正常に接続したときに呼び出されます。"""
        print(f'Twitch にログインしました | ユーザー名: {self.nick}')
        print(f'チャンネル: {TWITCH_CHANNEL_NAME} を監視中')
        if not GEMINI_API_KEY:
            print("警告: Gemini APIキーが設定されていません。チャット分析機能は動作しません。")

    async def event_message(self, message: twitchio.Message):
        """新しいチャットメッセージが受信されるたびに呼び出されます。"""
        if message.echo:
            return
        if message.author.name.lower() == self.nick.lower():
            return  # ボット自身のメッセージは無視
        if message.author.name.lower() == 'xiphelier_bot':
            return
        print(f'[{message.channel.name}] {message.author.name}: {message.content}')

        # Gemini APIキーが設定されている場合のみ分析を実行
        if GEMINI_API_KEY:
            analysis_result = await process_gemini_analysis(message.content)
            if analysis_result:
                sentiment = analysis_result.get('sentiment', '不明')
                score = analysis_result.get('excitement_score', 'N/A')
                reason = analysis_result.get('reason', '')
                print(f"  [Gemini分析] 感情: {sentiment}, 盛り上がり度: {score}/10, 理由: {reason}")
            else:
                print("  [Gemini分析] 分析に失敗しました。")
        else:
            print("  [Gemini分析] Gemini APIキーが設定されていないためスキップ。")

        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        """テスト用のコマンド例: !hello と入力すると応答します。"""
        await ctx.send(f'Hello {ctx.author.name}!')

async def main():
    # 必須設定のチェック
    if not TWITCH_OAUTH_TOKEN:
        print("\n--- 設定が必要です！ ---")
        print("'TWITCH_OAUTH_TOKEN' が環境変数または .secret ファイルで設定されていません。")
        print("OAuthトークンは https://twitchapps.com/tmi/ などで取得できます。")
        print("ボットの実行を中止します。\n")
        return
    
    if not TWITCH_CHANNEL_NAME:
        print("\n--- 設定が必要です！ ---")
        print("'TWITCH_CHANNEL_NAME' が環境変数または .secret ファイルで設定されていません。")
        print("監視したいTwitchチャンネルのユーザー名を設定してください。")
        print("ボットの実行を中止します。\n")
        return

    bot = TwitchChatBot()
    await bot.start()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nボットを停止します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
