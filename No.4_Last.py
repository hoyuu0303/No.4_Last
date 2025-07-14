import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import requests
from io import BytesIO
from rapidfuzz import fuzz

API_KEY = ""  # TMDB APIキー消し

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
    try:#映画とアニメ検索のエラー処理追加
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        messagebox.showerror("通信エラー", f"映画データの取得に失敗しました:\n{e}")
        return "翻訳エラー：" + str(e)
    
#映画候補を類似検索して一番近いものを自動選出
def get_best_match(user_input, candidates):
    best_score = 0
    best_match = None
    for item in candidates:
        title = item.get("title", "")
        score = fuzz.ratio(user_input.lower(), title.lower())
        if score > best_score:
            best_score = score
            best_match = item
    return best_match if best_score > 50 else None 

# メイン検索関数（映画 → アニメ の順に検索）
def search_content():
    query = entry.get()
    if not query:
        messagebox.showwarning("入力エラー", "検索キーワードを入力してください")
        return

    # 映画検索（TMDB）
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&language=ja-JP"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception as e:
        messagebox.showerror("エラー", f"映画データの取得に失敗しました:\n{e}")
        return


    if data.get("results"):
        movie = get_best_match(query, data["results"])
        if movie:
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
            image_label.config(image=None)#画像が表示されない可能性があったので修正
            image_label.image = img_tk
        else:
            image_label.config(image="", text="画像なし")
        return  # 映画が見つかったので終了

    # アニメ検索（Jikan）
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
        print("Anime Image URL:", image_url)
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

search_button = tk.Button(root, text="🔍 映画を検索", command=search_content)
search_button.pack(pady=5)

title_var = tk.StringVar()
overview_var = tk.StringVar()

tk.Label(root, textvariable=title_var, wraplength=400, font=("Helvetica", 13, "bold")).pack(pady=10)
tk.Label(root, textvariable=overview_var, wraplength=400, justify="left").pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=10)

root.mainloop()
