## yaplotlib

Yaplot 形式の描画データを Python から作るライブラリです。

描画コマンドは種類（`line` や `circle` など）と座標の列で表します。種類ごとの違いはライブラリ内部の表にまとめてあり、呼び出し側は同じ `add` を使います。複数フレームと、ファイル先頭の `global` ブロック、画面に固定する SVG は `YaplotDocument` が持ちます。

## インストール

```bash
pip install yaplotlib
```

numpy が必要です。

## クイックスタート

```python
import numpy as np
from yaplotlib import YaplotDocument

doc = YaplotDocument()
doc.globals.fov = 30
doc.globals.radius = 0.3

xyz = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
path = np.array([[0.0, 0.0, 0.0], [0.5, 0.2, 0.0], [1.0, 0.0, 0.0]])

for t in range(len(path)):
    frame = doc.new_frame()
    frame.add_many("circle", xyz, color=3)
    frame.add("stick", (0, 0, 0), (1, 0, 0), arrow=1, color=4)
    if t >= 1:
        # polyline は、Yaplot が受け付けるようになるまで線分に分解して出力する
        frame.add("polyline", *path[: t + 1], color=5)
    frame.add("text", (0, 0, 0), text=f"t = {t}")

doc.save("movie.yap")
```

`color`、`layer`、`radius`、`arrow` を省略すると、その項目は出力されません。直前の値を引き継ぐので、色を指定した要素の後ろに置いた色なしの要素は、その色で描かれます。

## global ブロック

`doc.globals` に置いた値は、すべてのフレームの初期状態になります。何も設定しなければ `global` ブロックは出力しません。

- 見た目: `layer`, `color`, `radius`, `arrow`, `palettes`
- 表示の初期状態: `reality`（0..4）, `splat`（0..3）, `fov`, `verbose`（0..3）, `thickness`, `rotation`（1〜3 個の数値）, `fps`, `hide`, `show`, `messages`
- 全フレーム共通の SVG: `add_svg`

```python
doc.globals.reality = 3
doc.globals.palettes[3] = (255, 100, 100)
doc.globals.messages.append("loaded")
```

## SVG

画面に固定する 2D の情報（見出し、凡例、グラフ）は SVG のまま渡します。`global` に置くと全フレーム、フレームに置くとそのフレームだけに出ます。matplotlib の Figure も渡せます（背景は透明になります）。

```python
frame.add_svg('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
              '<text x="16" y="32" fill="white">t = 0</text></svg>')
frame.add_svg(figure)          # matplotlib の Figure
doc.globals.add_svg("hud.svg")  # ファイル
```

## まとめて追加する

`add_many` は座標を ndarray のまま保持します。形は「個数 N × 1 個あたりの座標数 × 3」です。

| 種類 | 形 |
|---|---|
| `circle`, `ring`, `triangle`, `square`, `pentagon`, `hexagon`, `text` | `(N, 3)` |
| `line`, `stick` | `(N, 2, 3)` |
| `polygon`, `polyline`（頂点数がそろうとき） | `(N, m, 3)` |

`line` の始点と終点が別の配列なら `np.stack([starts, ends], axis=1)` で重ねます。`text` には長さ N の `texts` も渡します。

```python
starts = np.zeros((10, 3))
ends = np.ones((10, 3))
frame.add_many("line", np.stack([starts, ends], axis=1), color=3)
```

## パレット

```python
from yaplotlib.palettes import rainbow_colors

doc.globals.palettes.update(enumerate(rainbow_colors(8), start=10))
frame.palette(3, (255, 96, 96))
frame.palettes(rainbow_colors(8), offset=10)
```

`random_colors` と `gradation_colors` も同じように RGB のリストを返します。

## 以前の API

モジュールの関数（`Line`, `Circle`, `Color`, `SetPalette` など）と、`Line` や `Color` のような大文字のメソッドは、`DeprecationWarning` を出して残してあります。`Yaplot` は 1 フレームだけの `YaplotFrame` の別名です。

```python
from yaplotlib import Yaplot

drawing = Yaplot()
drawing.Points([(0, 0, 0), (1, 0, 0)], color=2, size=0.3)
drawing.save("example.yaplot")
```

## ライセンス

本リポジトリの `LICENSE` ファイルを参照してください。
