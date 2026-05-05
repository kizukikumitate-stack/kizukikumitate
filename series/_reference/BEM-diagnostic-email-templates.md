# BEM診断結果メール テンプレート集

Make.com の Gmail / Email モジュールに直接コピー&ペーストできる完全版。

## 使い方

1. Make.com の Router で 5 分岐後、それぞれの分岐に Gmail (または Email) モジュールを配置
2. 下記の Type 別テンプレを各分岐に貼り付け
3. `{{webhook.name}}`, `{{e1_score}}` などの変数は Make.com の Mapping で対応するフィールドにバインド
4. 添付ファイルは Google Drive の "Download a File" モジュールの結果をマップ

## 共通変数の対応表

| テンプレ内変数 | Make.com 内のマッピング元 |
|---|---|
| `{{name}}` | Webhook の `name` フィールド |
| `{{e1_score}}` | Set Variables で計算した `e1_score` |
| `{{e2_score}}` | Set Variables で計算した `e2_score` |
| `{{e3_score}}` | Set Variables で計算した `e3_score` |
| `{{i1_score}}` | Set Variables で計算した `i1_score` |
| `{{series_url}}` | `https://kizukikumitate.com/series/` |
| `{{consult_url}}` | `https://kizukikumitate.com/consult/` |
| `{{newsletter_url}}` | `https://kizukikumitate.com/newsletter/` |
| `{{unsubscribe_url}}` | メール配信解除のURL(ConvertKit等が自動生成) |

> 名前が空欄の場合のフォールバック: Make.com の `ifempty(name; "")` で空欄なら無記名処理

---

# Type A: 情報・フィードバック構造型

## 件名
```
【BEM診断結果】あなたの組織は Type A: 情報・フィードバック構造型 です
```

## 本文 (HTML)

```html
<p>{{name}}様</p>

<p>このたびは BEM診断シートにご回答いただき、ありがとうございます。<br>
診断の結果、あなたの組織は以下と判定されました。</p>

<p style="border-left: 4px solid #2563eb; padding-left: 16px; margin: 24px 0;">
<strong style="font-size: 16px;">Type A: 情報・フィードバック構造型</strong><br>
<span style="color: #475569;">あなたの組織は「期待水準とフィードバックの設計」にボトルネックがあります。</span>
</p>

<p>詳しい分析結果は、添付の4ページのPDFレポートをご覧ください。</p>

<p><strong>セル別スコア:</strong><br>
E1 (情報・フィードバック): {{e1_score}} / 8 ← 優位<br>
E2 (資源・時間): {{e2_score}} / 8<br>
E3 (インセンティブ・帰結): {{e3_score}} / 12<br>
I1 (個人能力): {{i1_score}} / 4</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>この型でよく起こること</strong></p>

<p>1on1が雑談化したり、評価制度が形骸化したり、目標管理が形式に流れたりする組織で頻発する型です。これは研修によるスキル付与では解決しません。期待水準とフィードバック構造の再設計が必要です。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>次の一歩</strong></p>

<p>▶ <a href="{{series_url}}#type-a">Type A に直結する記事を読む</a><br>
連載「気づきから組み立てる」の中で、本診断結果と関連性の高い記事(④1on1が雑談で終わる構造、⑧エンゲージメントサーベイ依存症、⑨評価制度の処遇配分ツール化、⑫対話がフォーマットになるとき)</p>

<p>▶ <a href="{{consult_url}}">30分相談で E1 構造を一緒に整理する</a><br>
無料・営業目的の押し売りはありません。あなたと同じ立場で組織を構造化したい方のための壁打ち時間です。</p>

<p>▶ <a href="{{newsletter_url}}">連載のメルマガに登録する</a><br>
新着記事・実務テンプレートの優先案内をお送りします。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p style="font-size: 12px; color: #64748b;">
このメールは BEM診断シートにご回答いただいた方にお送りしています。<br>
配信解除は <a href="{{unsubscribe_url}}">こちら</a> から可能です。<br><br>
<strong>きづきくみたて工房</strong> ─ 森本康仁<br>
<a href="https://kizukikumitate.com">kizukikumitate.com</a> | <a href="mailto:info@kizukikumitate.com">info@kizukikumitate.com</a>
</p>
```

---

# Type B: 資源・時間構造型

## 件名
```
【BEM診断結果】あなたの組織は Type B: 資源・時間構造型 です
```

## 本文 (HTML)

```html
<p>{{name}}様</p>

<p>このたびは BEM診断シートにご回答いただき、ありがとうございます。<br>
診断の結果、あなたの組織は以下と判定されました。</p>

<p style="border-left: 4px solid #0891b2; padding-left: 16px; margin: 24px 0;">
<strong style="font-size: 16px;">Type B: 資源・時間構造型</strong><br>
<span style="color: #475569;">あなたの組織は「業務量とプロセスの設計」にボトルネックがあります。</span>
</p>

<p>詳しい分析結果は、添付の4ページのPDFレポートをご覧ください。</p>

<p><strong>セル別スコア:</strong><br>
E1 (情報・フィードバック): {{e1_score}} / 8<br>
E2 (資源・時間): {{e2_score}} / 8 ← 優位<br>
E3 (インセンティブ・帰結): {{e3_score}} / 12<br>
I1 (個人能力): {{i1_score}} / 4</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>この型でよく起こること</strong></p>

<p>マネジャーが慢性的に時間不足で、ツールやプロセスが業務を妨げている組織で頻発する型です。これは「タイムマネジメント研修」では解決しません。業務量・工数・プロセス設計そのものの再構築が必要です。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>次の一歩</strong></p>

<p>▶ <a href="{{series_url}}#type-b">Type B に直結する記事を読む</a><br>
連載「気づきから組み立てる」の中で、本診断結果と関連性の高い記事(③マネジャーに育成の時間はあるか、⑥時間管理研修という延命装置、⑬キャリア自律の押し付け、⑮メンタル問題の個人化)</p>

<p>▶ <a href="{{consult_url}}">30分相談で「育成時間の捻出」を構造から考える</a><br>
無料・営業目的の押し売りはありません。プロセス再設計のヒントを共有します。</p>

<p>▶ <a href="{{newsletter_url}}">連載のメルマガに登録する</a><br>
新着記事・実務テンプレートの優先案内をお送りします。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p style="font-size: 12px; color: #64748b;">
このメールは BEM診断シートにご回答いただいた方にお送りしています。<br>
配信解除は <a href="{{unsubscribe_url}}">こちら</a> から可能です。<br><br>
<strong>きづきくみたて工房</strong> ─ 森本康仁<br>
<a href="https://kizukikumitate.com">kizukikumitate.com</a> | <a href="mailto:info@kizukikumitate.com">info@kizukikumitate.com</a>
</p>
```

---

# Type C: インセンティブ構造型

## 件名
```
【BEM診断結果】あなたの組織は Type C: インセンティブ構造型 です
```

## 本文 (HTML)

```html
<p>{{name}}様</p>

<p>このたびは BEM診断シートにご回答いただき、ありがとうございます。<br>
診断の結果、あなたの組織は以下と判定されました。</p>

<p style="border-left: 4px solid #d97706; padding-left: 16px; margin: 24px 0;">
<strong style="font-size: 16px;">Type C: インセンティブ構造型</strong><br>
<span style="color: #475569;">あなたの組織は「評価と望ましい行動の不整合」にボトルネックがあります。</span>
</p>

<p>詳しい分析結果は、添付の4ページのPDFレポートをご覧ください。</p>

<p><strong>セル別スコア:</strong><br>
E1 (情報・フィードバック): {{e1_score}} / 8<br>
E2 (資源・時間): {{e2_score}} / 8<br>
E3 (インセンティブ・帰結): {{e3_score}} / 12 ← 優位<br>
I1 (個人能力): {{i1_score}} / 4</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>この型でよく起こること</strong></p>

<p>リーダー研修を打ってもリーダーが育たない、バリューが掲示物で終わる、育成行動が報われない、といった現象が起こる型です。これはリーダー研修やバリュー策定では解決しません。評価制度・処遇・承認構造の再設計が必要です。BEM の中でも E3 は最も診断されにくく、しかし最も介入効果が大きい領域です。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>次の一歩</strong></p>

<p>▶ <a href="{{series_url}}#type-c">Type C に直結する記事を読む</a><br>
連載「気づきから組み立てる」の中で、本診断結果と関連性の高い記事(②リーダー研修で育たないリーダー、⑦バリューが掲示物で終わる、⑩ハラスメント研修の年次行事化、⑪心理的安全性の希釈、⑰シニアにモチベ研修を打つ前に)</p>

<p>▶ <a href="{{consult_url}}">30分相談で評価制度と望ましい行動のギャップを構造化する</a><br>
無料・営業目的の押し売りはありません。E3構造の現状診断を一緒に行います。</p>

<p>▶ <a href="{{newsletter_url}}">連載のメルマガに登録する</a><br>
新着記事・実務テンプレートの優先案内をお送りします。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p style="font-size: 12px; color: #64748b;">
このメールは BEM診断シートにご回答いただいた方にお送りしています。<br>
配信解除は <a href="{{unsubscribe_url}}">こちら</a> から可能です。<br><br>
<strong>きづきくみたて工房</strong> ─ 森本康仁<br>
<a href="https://kizukikumitate.com">kizukikumitate.com</a> | <a href="mailto:info@kizukikumitate.com">info@kizukikumitate.com</a>
</p>
```

---

# Type D: 構造複合型

## 件名
```
【BEM診断結果】あなたの組織は Type D: 構造複合型 です(優先対応推奨)
```

## 本文 (HTML)

```html
<p>{{name}}様</p>

<p>このたびは BEM診断シートにご回答いただき、ありがとうございます。<br>
診断の結果、あなたの組織は以下と判定されました。</p>

<p style="border-left: 4px solid #475569; padding-left: 16px; margin: 24px 0;">
<strong style="font-size: 16px;">Type D: 構造複合型</strong><br>
<span style="color: #475569;">あなたの組織は複数の構造領域に同時に課題を抱えています。</span>
</p>

<p>詳しい分析結果は、添付の4ページのPDFレポートをご覧ください。</p>

<p><strong>セル別スコア:</strong><br>
E1 (情報・フィードバック): {{e1_score}} / 8 ← 高<br>
E2 (資源・時間): {{e2_score}} / 8 ← 高<br>
E3 (インセンティブ・帰結): {{e3_score}} / 12 ← 高<br>
I1 (個人能力): {{i1_score}} / 4</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>この型でよく起こること</strong></p>

<p>改革を打っても局所最適化に終わったり、全方位的な機能不全に陥っている組織で見られる型です。複合型の場合、E3 → E1 → E2 の順での介入が効果的です。インセンティブ構造を再設計しないと、情報設計や資源配分を変えても元に戻る力が働くためです。<strong>30分相談で介入順序の優先順位を一緒に整理することを強く推奨します。</strong></p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>次の一歩</strong></p>

<p>▶ <a href="{{consult_url}}">30分相談を優先的に予約する</a><br>
複合型は単発記事だけでは構造化が難しいため、30分相談を最優先することをお勧めします。無料・営業目的の押し売りはありません。</p>

<p>▶ <a href="{{series_url}}">シリーズ全体を Phase 1 から順に読む</a><br>
連載「気づきから組み立てる」の Phase 1 から順番に読み進めることで構造化が進みます。①〜⑥の研修依存症、⑤の Kirkpatrick L3-L4、⑭の人的資本経営、⑯の早期離職、⑱の女性活躍などが特に関連します。</p>

<p>▶ <a href="{{newsletter_url}}">連載のメルマガに登録する</a><br>
新着記事・実務テンプレートの優先案内をお送りします。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p style="font-size: 12px; color: #64748b;">
このメールは BEM診断シートにご回答いただいた方にお送りしています。<br>
配信解除は <a href="{{unsubscribe_url}}">こちら</a> から可能です。<br><br>
<strong>きづきくみたて工房</strong> ─ 森本康仁<br>
<a href="https://kizukikumitate.com">kizukikumitate.com</a> | <a href="mailto:info@kizukikumitate.com">info@kizukikumitate.com</a>
</p>
```

---

# Type E: スキル特化型

## 件名
```
【BEM診断結果】あなたの組織は Type E: スキル特化型 です(まれなケース)
```

## 本文 (HTML)

```html
<p>{{name}}様</p>

<p>このたびは BEM診断シートにご回答いただき、ありがとうございます。<br>
診断の結果、あなたの組織は以下と判定されました。</p>

<p style="border-left: 4px solid #059669; padding-left: 16px; margin: 24px 0;">
<strong style="font-size: 16px;">Type E: スキル特化型</strong><br>
<span style="color: #475569;">あなたの組織は「環境構造は機能している、純粋なスキル課題」に直面しています。</span>
</p>

<p>詳しい分析結果は、添付の4ページのPDFレポートをご覧ください。</p>

<p><strong>セル別スコア:</strong><br>
E1 (情報・フィードバック): {{e1_score}} / 8<br>
E2 (資源・時間): {{e2_score}} / 8<br>
E3 (インセンティブ・帰結): {{e3_score}} / 12<br>
I1 (個人能力): {{i1_score}} / 4 ← 優位</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>この型でよく起こること</strong></p>

<p>構造はおおむね機能していて、純粋にスキル不足が中心の課題と判定された<strong>稀なケース</strong>です。Gilbert の研究では、組織のパフォーマンス問題の約75〜85%は環境要因に起因するとされており、I1単独優位は少数派。HPI観点で「真にスキル不足か」の再検証をしてみると、隠れた E1〜E3 課題が見つかることもあります。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p><strong>次の一歩</strong></p>

<p>▶ <a href="{{series_url}}#type-e">関連記事で BEM の他のセルを再点検</a><br>
連載①「研修で解けない問題を、研修で解こうとする」と⑤「研修やったのに変わらない」は、E1〜E3 が本当に機能しているかを再点検する切り口を提供します。</p>

<p>▶ <a href="{{consult_url}}">30分相談で HPI 観点の再診断</a><br>
無料・営業目的の押し売りはありません。「本当にスキル不足か」を一緒に検証します。</p>

<p>▶ <a href="{{newsletter_url}}">連載のメルマガに登録する</a><br>
新着記事・実務テンプレートの優先案内をお送りします。</p>

<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">

<p style="font-size: 12px; color: #64748b;">
このメールは BEM診断シートにご回答いただいた方にお送りしています。<br>
配信解除は <a href="{{unsubscribe_url}}">こちら</a> から可能です。<br><br>
<strong>きづきくみたて工房</strong> ─ 森本康仁<br>
<a href="https://kizukikumitate.com">kizukikumitate.com</a> | <a href="mailto:info@kizukikumitate.com">info@kizukikumitate.com</a>
</p>
```

---

# プレーンテキスト版 (Type A の例・他タイプも同様パターンで作成)

HTMLメールが届かないクライアントへのフォールバック用。Make.com の Email モジュールで「Plain Text alternative」フィールドにペースト。

```text
{{name}}様

このたびは BEM診断シートにご回答いただき、ありがとうございます。
診断の結果、あなたの組織は以下と判定されました。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type A: 情報・フィードバック構造型
あなたの組織は「期待水準とフィードバックの設計」にボトルネックがあります。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

詳しい分析結果は、添付の4ページのPDFレポートをご覧ください。

【セル別スコア】
E1 (情報・フィードバック): {{e1_score}} / 8 ← 優位
E2 (資源・時間): {{e2_score}} / 8
E3 (インセンティブ・帰結): {{e3_score}} / 12
I1 (個人能力): {{i1_score}} / 4

────────────────────
この型でよく起こること
────────────────────

1on1が雑談化したり、評価制度が形骸化したり、目標管理が形式に
流れたりする組織で頻発する型です。これは研修によるスキル付与では
解決しません。期待水準とフィードバック構造の再設計が必要です。

────────────────────
次の一歩
────────────────────

▶ Type A に直結する記事を読む
   {{series_url}}

▶ 30分相談で構造化を一緒にやる(無料)
   {{consult_url}}

▶ 連載のメルマガに登録する
   {{newsletter_url}}

────────────────────

このメールは BEM診断シートにご回答いただいた方にお送りしています。
配信解除はこちら: {{unsubscribe_url}}

きづきくみたて工房 ─ 森本康仁
Web : https://kizukikumitate.com
Mail: info@kizukikumitate.com
```

---

## 運用上のメモ

### 件名のA/Bテスト案

立ち上げ後、開封率を見ながら以下の件名パターンを試すと良い:

- 直接型 (現状): `【BEM診断結果】あなたの組織は Type X: ○○型 です`
- 問いかけ型: `あなたの組織のボトルネックは「○○」でした`
- 数字型: `BEM診断: E3スコア 11/12 ─ あなたの結果`

### 開封率向上のヒント

- 送信元名を `森本康仁 (きづきくみたて工房)` のように個人名+屋号にすると開封率が上がりやすい
- プレヘッダー(プレビューテキスト)に「4ページのPDFレポートを添付しました」を入れる
- HTML/プレーンテキスト両方を送信する設定にする(配信性向上)

### Type D の優先対応扱い

Type D は最も相談につながりやすいセグメントなので:
- 件名に「優先対応推奨」を入れている
- CTAの順序を「相談 → 記事」の順にしている
- 数日後に Yasuhitoさん自身が直接フォローメールを送ることを推奨

### スパムフィルタ対策

- 添付PDFのファイル名に日本語が入っていても問題なし
- ただし、件名の【】や ★★ などの記号が多すぎるとスパム判定されやすい
- リンクは短縮URLではなく直接URL推奨
