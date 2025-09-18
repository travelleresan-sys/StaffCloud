# 日本の財務諸表Excel出力システム

## 概要
日本の会計事務所で利用される標準的な財務諸表をExcel形式で出力するWebアプリケーションです。

## 出力される財務諸表

### 1. 貸借対照表（Balance Sheet）
- **資産の部**
  - Ⅰ 流動資産（現金及び預金、受取手形、売掛金、商品等）
  - Ⅱ 固定資産（有形固定資産、無形固定資産、投資その他の資産）
- **負債及び純資産の部**
  - Ⅰ 流動負債（支払手形、買掛金、短期借入金等）
  - Ⅱ 固定負債（長期借入金、退職給付引当金等）
  - Ⅲ 純資産の部（資本金、資本剰余金、利益剰余金）

### 2. 損益計算書（Profit and Loss Statement）
- Ⅰ 売上高
- Ⅱ 売上原価
- 売上総利益
- Ⅲ 販売費及び一般管理費
- 営業利益
- Ⅳ 営業外収益
- Ⅴ 営業外費用
- 経常利益
- Ⅵ 特別利益
- Ⅶ 特別損失
- 税引前当期純利益
- 法人税等
- 当期純利益

### 3. キャッシュフロー計算書（Cash Flow Statement）
- Ⅰ 営業活動によるキャッシュ・フロー
- Ⅱ 投資活動によるキャッシュ・フロー
- Ⅲ 財務活動によるキャッシュ・フロー
- Ⅳ 現金及び現金同等物の増減額
- Ⅴ 現金及び現金同等物の期首残高
- Ⅵ 現金及び現金同等物の期末残高

### 4. 株主資本等変動計算書（Statement of Changes in Net Assets）
- 株主資本（資本金、資本剰余金、利益剰余金、自己株式）
- 当期首残高・当期変動額・当期末残高の表示
- 剰余金の配当、当期純利益等の変動要因

### 5. 附属明細書（Notes to Financial Statements）
- 主な会計方針
- 有形固定資産の明細
- 借入金の明細
- 従業員数等の情報

## 技術仕様

### システム構成
- **言語**: Python 3.8+
- **Webフレームワーク**: Flask
- **Excel生成**: openpyxl
- **フロントエンド**: Bootstrap 5, HTML5

### ファイル構成
```
japanese_financial_statements_generator.py  # コア機能
japanese_financial_webapp.py               # Flaskアプリ
templates/
  ├── japanese_financial_index.html        # トップページ
  └── japanese_financial_form.html         # 入力フォーム
```

## 使用方法

### 1. スタンドアロン実行
```bash
python japanese_financial_statements_generator.py
```
- サンプルデータでExcelファイルを生成

### 2. Webアプリ実行
```bash
python japanese_financial_webapp.py
```
- ブラウザで `http://localhost:5003` にアクセス
- 会社名・決算年度を入力してExcel生成

### 3. 他のアプリケーションから利用
```python
from japanese_financial_statements_generator import generate_japanese_financial_statements

# Excel生成
output = generate_japanese_financial_statements("株式会社テスト", 2025)

# ファイル保存
with open("sample.xlsx", "wb") as f:
    f.write(output.getvalue())
```

## 特徴

### ✅ 日本の会計基準完全準拠
- 企業会計原則に基づく区分表示
- 流動・固定分類の適切な処理
- 段階利益計算の正確な表示

### ✅ 会計事務所向けデザイン
- シンプルで見やすいレイアウト
- 余計な装飾を排除した実用的なデザイン
- 印刷に適した罫線・フォント設定

### ✅ Excel機能活用
- 適切なセル結合・罫線
- 数値の右寄せ・カンマ区切り
- 小計・合計の強調表示

### ✅ 拡張性
- モジュール化された設計
- 簡単にカスタマイズ可能
- データ連携機能追加可能

## サンプルデータ

### 貸借対照表バランス確認
- 資産合計: 83,500,000円
- 負債合計: 34,500,000円
- 純資産合計: 49,000,000円
- **バランス**: ✅ 資産 = 負債 + 純資産

### 損益計算書
- 売上高: 120,000,000円
- 売上原価: 74,500,000円
- 売上総利益: 45,500,000円
- 営業利益: 2,500,000円
- 当期純利益: 1,225,000円

## カスタマイズ

### データ変更
`JapaneseFinancialStatementsGenerator`クラス内の各メソッドで数値を変更可能

### レイアウト調整
- フォント設定: `__init__`メソッド
- 列幅: 各作成メソッド内の`column_dimensions`
- 色設定: `header_fill`, `subtotal_fill`

### 科目追加
各財務諸表の`data`配列に項目を追加

## 注意事項

1. **サンプルデータ**: 実際の会計データではありません
2. **会計処理**: 複雑な会計処理は会計士等にご相談ください
3. **Excel互換性**: Microsoft Excel 2007以降で正常に表示されます
4. **法的責任**: このシステムの使用による損害は一切負いません

## ライセンス
MIT License

## 更新履歴
- 2025-01-18: 初版リリース
  - 5つの基本財務諸表対応
  - Flask Webアプリ化
  - サンプルデータ充実

## サポート
技術的なお問い合わせやカスタマイズのご相談は、開発チームまでご連絡ください。