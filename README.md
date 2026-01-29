## yaplotlib

Yaplot 形式の描画データを Python から手軽に生成するためのライブラリです。

- **高レベル API**: 状態付きの `Yaplot`（1 フレーム）／複数フレーム対応の `YaplotDocument`
- **低レベル API**: Yaplot の 1 行コマンド（`l`, `c`, `t`, `@`, …）をそのまま生成する関数群
- **パレット**: ランダム・虹色・グラデーションのパレットを自動生成

API リファレンス（全メソッド・引数の説明）は、リポジトリで GitHub Pages が有効な場合にブラウザで閲覧できます。

## インストール

```bash
pip install yaplotlib
```

ソースからインストールする場合（開発版を試す場合）:

```bash
git clone <このリポジトリの URL>
cd yaplotlib
python -m pip install -e .
```

## クイックスタート（1 フレーム）

1 枚の図を描く場合は `Yaplot` を使います。

```python
from yaplotlib import Yaplot

y = Yaplot()

# 点を 3 つ描く
y.Points([
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
], color=2, size=1.5)

# 線分を 1 本描く
y.Line((0.0, 0.0, 0.0), (1.0, 1.0, 0.0), color=3)

# ファイルへ保存
y.save("example.yaplot")
```

生成した `example.yaplot` を [Yaplot](https://github.com/vitroid/Yaplot) で開くと描画を確認できます。

## クイックスタート（複数フレーム）

アニメーションや時間発展を表現する場合は `YaplotDocument` を使います。

```python
from yaplotlib import YaplotDocument

doc = YaplotDocument()

# フレーム 0
doc.Points([(0.0, 0.0, 0.0)], color=2)

# 新しいフレームを追加
doc.new_frame()
doc.Points([(1.0, 0.0, 0.0)], color=3)

doc.save("movie.yaplot")
```

`movie.yaplot` には 2 フレーム分のデータが含まれ、Yaplot で連続表示できます。

## 主な API

### 高レベルクラス

- **`Yaplot`**（= `YaplotFrame`）  
  1 フレーム分の描画を蓄積します。
  - 描画: `Line`, `Circle`, `Arrow`, `Polygon`, `Points`, `LinesBatch`, `ArrowsBatch`
  - スタイル: `Layer`, `Color`, `Size`, `ArrowType`
  - パレット: `SetPalette`, `RandomPalettes`, `RainbowPalettes`, `GradationPalettes`
  - 出力: `dumps()`, `save(path)`

- **`YaplotDocument`**  
  複数フレームをまとめて扱います。
  - `new_frame()` で新しいフレームを追加
  - 描画メソッドは現在のフレームに追加されます
  - `dumps()`, `save(path)` で全フレームをまとめて出力

### 低レベル関数

Yaplot のコマンド文字列を直接組み立てる場合は、モジュールの関数を使えます。

```python
from yaplotlib import Line, Circle, Color, SetPalette
```

- ジオメトリ: `Line`, `Circle`, `Arrow`, `Polygon`, `Text`
- スタイル: `Color`, `Size`, `Layer`, `ArrowType`, `NewPage`

いずれも 1 行ぶんの Yaplot コマンド文字列を返す純粋関数です。詳細は API リファレンス（GitHub Pages または `pdoc yaplotlib`）を参照してください。

## インポート例

```python
from yaplotlib import Yaplot, YaplotDocument, Line, Circle
```

## ライセンス

本リポジトリの `LICENSE` ファイルを参照してください。
