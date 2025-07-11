import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import requests
from io import BytesIO

API_KEY = ""  # TMDB APIなので消します

# 翻訳関数
def translate_to_japanese(text):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": "en",
        "target": "ja",
        "format": "text"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        return result.get("translatedText", "翻訳に失敗しました")
    except Exception as e:
        return "翻訳エラー：" + str(e)

# （映画 → アニメ の順に検索）
def search_content():
    query = entry.get()
    if not query:
        messagebox.showwarning("入力エラー", "検索キーワードを入力してください")
        return

    # 映画検索（TMDB）
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&language=ja-JP"
    response = requests.get(url)
    data = response.json()

    if data.get("results"):
        movie = data["results"][0]
        title_var.set(f"🎬 映画タイトル: {movie['title']}")
        overview = movie["overview"] or "（日本語のあらすじがありません）"
        overview_var.set(f"あらすじ:\n{overview}")

        poster_path = movie.get("poster_path")
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}"
            img_data = requests.get(poster_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 300))
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk
        else:
            image_label.config(image="", text="画像なし")
        return  # 映画が見つかったので終了

    # アニメ検索（Jikan）幅を増やすために配置したけど微妙（gitに失礼）
    url_jikan = f"https://api.jikan.moe/v4/anime?q={query}"
    response_jikan = requests.get(url_jikan)
    data_jikan = response_jikan.json()

    if data_jikan.get('data'):
        anime = data_jikan['data'][0]
        title_var.set(f"📺 アニメタイトル: {anime.get('title_japanese') or anime['title']}")
        synopsis_en = anime.get('synopsis') or "No synopsis available."
        synopsis_ja = translate_to_japanese(synopsis_en)
        overview_var.set(f"あらすじ:\n{synopsis_ja}")

        image_url = anime['images']['jpg']['large_image_url']
        if image_url:
            img_data = requests.get(image_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 300))
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk
        else:
            image_label.config(image="", text="画像なし")
        return

    # 映画もアニメも見つからなかった場合
    title_var.set("")
    overview_var.set("該当する映画・アニメが見つかりませんでした。")
    image_label.config(image="", text="画像なし")

# --- GUI 構築 ---
root = tk.Tk()
root.title("映画 & アニメ検索アプリ")
root.geometry("450x700")

entry = tk.Entry(root, width=40)
entry.pack(pady=10)

search_button = tk.Button(root, text="🔍 映画またはアニメを検索", command=search_content)
search_button.pack(pady=5)

title_var = tk.StringVar()
overview_var = tk.StringVar()

tk.Label(root, textvariable=title_var, wraplength=400, font=("Helvetica", 13, "bold")).pack(pady=10)
tk.Label(root, textvariable=overview_var, wraplength=400, justify="left").pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=10)

root.mainloop()
