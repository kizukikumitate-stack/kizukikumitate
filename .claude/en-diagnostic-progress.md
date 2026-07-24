# 英語版 現在地診断（海外展開ショーケース）進捗台帳

夜間クラウドroutineが、この台帳を見て「次の未完了チャンク」を1つだけ実装し、PRを出す。
各チャンク完了時に、そのPR内でこの行の [ ] を [x] に更新すること。
全チャンク完了（chunk6が [x]）になったら、routineは何もせず「完了」とだけ報告して終了する。

対象ファイル: genzaichi-shindan.html（同一ページのバイリンガル化・別ファイルは作らない）
方式: 妖怪診断と同じ ?lang=en ＋ localStorage ＋ 右下トグル（第3方式を作らない）

- [ ] chunk1: i18n土台（LANG判定＝?lang→localStorage→'ja'、切替トグル、localStorage保存、hreflang en、英語のtitle/description/og/twitter を alternate で用意する下地）。この段階では表示文字列はまだ日本語のままでよい。トグルで LANG が切り替わり保存される所まで
- [ ] chunk2: 静的UI（導入文・各見出し sec-label・ボタン・冒険の書のラベル・注記 caveat）の英日辞書化と切替反映
- [ ] chunk3: 診断の質問（QUESTIONS 8問の text/lo/hi）と耐性カード（TAISEI 15枚の name/desc）の英日化
- [ ] chunk4: 結果まわり（TYPES 5タイプの name/desc/jobsNote/indsNote、REWARDS ラベル、差分の言葉 GAP_WORD、tagNames、ホバーtip、toast）の英日化
- [ ] chunk5: 「この診断のしくみ」howto 長文セクションの英日化
- [ ] chunk6: 推薦チップの英語ラベル（JOBP の職業名・INDP の大陸名に英名を持たせ、EN時は英名表示。リンク先は日本語図鑑のまま＝英文で "The atlas pages are currently in Japanese." と注記）＋ connect導線（フッター付近に "Want a career atlas like this for your country, school, or company? Let's talk." → mailto:y.morimoto@kizukikumitate.com、GA4 connect_click）＋ 両言語の最終QA
