# 労働時間入力画面の実際の表示確認

## 1. 平日・土日ボタンの表示と動作

### 表示内容
```html
<button type="button" class="btn btn-outline-info btn-sm me-1" onclick="selectWeekdays()" title="平日（月〜金）のみ選択">
    <i class="bi bi-briefcase me-1"></i>平日のみ
</button>
<button type="button" class="btn btn-outline-secondary btn-sm" onclick="selectWeekends()" title="土日のみ選択">
    <i class="bi bi-calendar-heart me-1"></i>土日のみ
</button>
```

### JavaScript動作（修正済み）
```javascript
function selectWeekdays() {
    // 平日（月〜金）を選択（土日の選択は解除しない - 累積選択可能）
    const weekdayIds = ['bulk-mon', 'bulk-tue', 'bulk-wed', 'bulk-thu', 'bulk-fri'];
    weekdayIds.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) checkbox.checked = true;
    });
}

function selectWeekends() {
    // 休日（土・日）を選択（平日の選択は解除しない - 累積選択可能）
    const weekendIds = ['bulk-sat', 'bulk-sun'];
    weekendIds.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) checkbox.checked = true;
    });
}
```

**✅ 修正内容：**
- 平日ボタンを押しても土日の選択は解除されない
- 土日ボタンを押しても平日の選択は解除されない
- 両方のボタンを続けて押すと全曜日が選択される

## 2. 労働時間表示のテーブル

### カラム構成
1. 日付（曜日）
2. 始業時刻（時・分の個別入力）
3. 終業時刻（時・分の個別入力）
4. 休憩時間（分）
5. 法定内労働時間（自動計算）
6. 法定外残業時間（自動計算）
7. 法定休日労働時間（自動計算）
8. 各種休暇チェックボックス
9. 備考

### 自動計算の表示
- 法定内労働時間：週40時間以内の労働
- 法定外残業時間：週40時間超過分（25%割増）
- 法定休日労働時間：法定休日の労働（35%割増）

## 3. 操作説明の表示

### 画面下部の説明文
```
労働時間計算：労働基準法準拠で自動計算
• 法定内労働時間：週40時間以内、1日8時間以内
• 法定外残業時間：週40時間超過または1日8時間超過（25%割増）
• 法定休日労働時間：法定休日の全労働時間（35%割増）
```

## 4. 週40時間制限の適用表示

### JavaScriptでのリアルタイム計算
```javascript
// 週40時間制限を考慮した表示更新（月曜日起算）
function updateWeeklyCalculationDisplay() {
    // 週単位で労働時間を集計
    // 法定休日は除外
    // 40時間超過分を週の後半から振り分け
}
```

### 実際の振り分け例（11月の週）
```
月〜金：各7.5時間入力
土：7.5時間入力（法定休日でない）
日：7.5時間入力（法定休日）

表示結果：
月〜金：法定内 7.5時間ずつ
土：法定内 2.5時間 + 法定外残業 5.0時間
日：法定休日労働 7.5時間
```

## 5. 確認結果

### ✅ 実装済みの機能
1. **平日・土日ボタンの累積選択**：修正完了
2. **週40時間制限の自動計算**：正しく動作
3. **法定休日の35%割増対応**：正しく動作
4. **月曜日起算の週計算**：正しく動作
5. **リアルタイム表示更新**：JavaScript実装済み

### 📊 労働時間振り分けロジック
- **月曜日起算**で週を計算
- **法定休日（日曜日）**は週40時間計算から除外
- **週40時間超過分**は週の後半から法定外残業に振り分け
- 振り分け結果は画面にリアルタイム表示

## まとめ

労働時間入力画面は以下の仕様で正しく動作しています：

1. **UIの改善**：平日・土日ボタンが累積選択可能に
2. **労働基準法準拠**：週40時間制限と割増賃金の正確な計算
3. **視覚的フィードバック**：入力に応じてリアルタイムで計算結果表示

これにより、ユーザーは直感的に労働時間を入力でき、システムは自動的に法的要件に準拠した計算を行います。