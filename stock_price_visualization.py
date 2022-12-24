import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write(
  """
  # GAFA株価
  #
  こちらは株価可視化ツールです。
  以下のオプションから表示日時を指定できます。
  #
  """
)

st.sidebar.write(
  """
  ## 表示日数
  """
)

days = st.sidebar.slider('日数', 0, 50, 20)

st.write(
  f"""
  #
  ### 過去*{days}日間*のGAFAの株価
  """
)

# データをキャッシュしておき、表示速度を向上させる
@st.cache
#仮引数にdays, tickersを代入。 グローバル変数を使用可能に。
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
    # company = 'facebook'
        tkr = yf.Ticker(tickers[company])

        #過去２０日分の履歴をhistに格納
        hist = tkr.history(period=f'{days}d')

        #Dateのを自分好みに並び替え
        hist.index = hist.index.strftime('%d %B %Y')

        #終値のみを取得
        hist = hist[['Close']]
        hist.columns = [company]

        #col, rowを逆転させる
        hist = hist.T

        #appleの上に 'Name'を追加
        hist.index.name = 'Name'

        #dfにhistを順次、addしていく
        df = pd.concat([df, hist])
    return df
  
# 例外処理
try:
    st.sidebar.write(
      """
      ## 株価の範囲指定
      """
    )

    ymin, ymax = st.sidebar.slider(
      '範囲を指定してください(終値)', 
      0, 3500, (0, 400)
    )

    tickers = {
      'apple': 'AAPL',
      'facebook': 'META',
      'google': 'GOOGL',
      'microsoft': 'MSFT',
      'netflix': 'NFLX',
      'amazon': 'AMZN',
      'tesla': 'TSLA'
    }

    #関数に実引数を代入して、実行 
    df = get_data(days, tickers)

    """
    #
    """

    companies = st.multiselect(
      '会社名を選択してください。',
      # df.indexでtickersで指定した要素を取得し、それをlistで囲んでlist形式に変換
      list(df.index),
      # 初期で表示する内容
      ['google', 'amazon', 'facebook', 'apple']
    )

    # companiesが一つも選ばれていなければ...
    if not companies:
      st.error('少なくとも一社は選んでください。')
    else:
      data = df.loc[companies]
      """
      #
      """
      # .sort_index()でアルファベット順に変更
      st.write("### 株価 (USD)", data.sort_index())
      #天地ひっくり返し＋時間だけを取得できる形に変換
      data = data.T.reset_index()
      #日付、会社名、値に変換(形の整形されていない生データに変換した)
      data = pd.melt(data, id_vars=['Date']).rename(
        # valuenの名前をStock Prices(USD)に変更
        columns={'value': 'Stock Prices(USD)'}
      )
      
      chart = (
        alt.Chart(data)
        #clipでグラフの外にあるものは削除 
        .mark_line(opacity=.8, clip=True)
        .encode(
            x="Date:T",
            y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
            color="Name:N"
        )
      )

      # streamlitでaltairを表示
      st.altair_chart(chart, use_container_width=True)
except:
  st.error(
    "エラーが起きているようです。"
  )