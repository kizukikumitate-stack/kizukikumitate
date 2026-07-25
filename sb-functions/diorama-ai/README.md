# diorama-ai（ステークホルダー・ジオラマのAI下ごしらえ）

`stakeholder-diorama.html` の「🤖 AIで下ごしらえ」は、ブラウザから直接 Claude API を
呼ぶことができない（APIキーを公開ページに置けないため）。この Edge Function がキーを
預かって中継する。

キーは **この中には書かない**。Supabase の Secrets（環境変数）に置く。

## デプロイ手順（Macのターミナルで実行）

```bash
# 1. Supabase CLI を入れる（初回のみ）
brew install supabase/tap/supabase

# 2. ログイン（ブラウザが開く）
supabase login

# 3. リポジトリで Supabase を初期化（初回のみ。supabase/ フォルダができる）
cd /Users/morimotoyasuhito/kizukikumitate
supabase init

# 4. この関数を supabase/functions/ に移す
mkdir -p supabase/functions/diorama-ai
cp sb-functions/diorama-ai/index.ts supabase/functions/diorama-ai/index.ts

# 5. Supabase のプロジェクトに紐付ける
#    <project-ref> は https://supabase.com/dashboard の URL に出てくる文字列
supabase link --project-ref <project-ref>

# 6. APIキーを Secrets に登録する（コードには書かない）
supabase secrets set ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# 7. デプロイ（JWT検証は切る＝ページから誰でも叩ける。Origin制限で守る）
supabase functions deploy diorama-ai --no-verify-jwt
```

デプロイが終わると、次の形のURLが表示される。

```
https://<project-ref>.supabase.co/functions/v1/diorama-ai
```

## ページ側の設定

`stakeholder-diorama.html` の先頭付近にある

```js
const AI_ENDPOINT = "";
```

を、上のURLに書き換えて push する。空のままなら「AIで下ごしらえ」欄は表示されない
（ケースのプリセットと手動入力だけで動く）。

## 守っていること

- APIキーはブラウザに一切出ない（Secrets に置く）
- `ALLOWED_ORIGINS` にある自サイトのドメインからしか呼べない
- 入力は200字で切る（長文を投げ込まれてコストが膨らむのを防ぐ）
- 返すのは生成結果のJSONだけ。ユーザーの入力は保存しない（テーブルを持たない）

## 費用の目安

1回の生成で入力・出力あわせて約1,500トークン。体験会で30人が2回ずつ押しても
数十円の水準。心配なら Anthropic Console 側で使用上限を設定しておく。
