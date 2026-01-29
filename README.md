## yaplotlib

Yaplot 形式の描画データを Python から手軽に生成するための小さなライブラリです。

**API ドキュメント（オンライン）**: このリポジトリを GitHub にプッシュし、[GitHub Pages を有効化](#github-pages-でドキュメントを公開する)すると、pdoc で生成した API リファレンスを `https://<user>.github.io/yaplotlib/` で公開できます。

- **低レベル API**: Yaplot の 1 行コマンド (`l`, `c`, `t`, `@`, …) をそのまま生成
- **高レベル API**: 状態付きの `Yaplot` / 複数フレーム対応の `YaplotDocument`
- **パレットユーティリティ**: ランダム・虹色・グラデーションパレットの自動生成

## インストール

PyPI に公開している場合は次のようにインストールできます:

```bash
pip install yaplotlib
```

ローカルのこのリポジトリを直接使う場合は、カレントディレクトリを通したうえで:

```bash
python -m pip install -e .
```

## クイックスタート（1フレーム）

最も簡単な使い方は、`Yaplot`（= 1 フレームぶんのバッファ）を使う方法です。

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

生成された `example.yaplot` を Yaplot で読み込むと描画を確認できます。

## クイックスタート（複数フレーム）

アニメーションや時間発展を表現したい場合は、`YaplotDocument` を使います。

```python
from yaplotlib import YaplotDocument

doc = YaplotDocument()

# フレーム 0
doc.Points([(0.0, 0.0, 0.0)], color=2)

# 新しいフレームを作成
doc.new_frame()
doc.Points([(1.0, 0.0, 0.0)], color=3)

doc.save("movie.yaplot")
```

`movie.yaplot` には 2 フレーム分のデータが含まれます。

## 主な API

### 高レベルクラス

- **`Yaplot` / `YaplotFrame`**
  - 1 フレーム分のコマンドを蓄積するクラスです。
  - 主なメソッド:
    - `Layer(layer: int)` / `Color(color: int)` / `Size(size: float)` / `ArrowType(arrowtype: int)`
    - `Line(a, b, layer=-1, color=-1)`
    - `Circle(c, layer=-1, color=-1, size=-1)`
    - `Arrow(a, b, layer=-1, color=-1, size=-1, arrowtype=-1)`
    - `Polygon(vertices, layer=-1, color=-1)`
    - `RandomPalettes`, `RainbowPalettes`, `GradationPalettes`
    - 高レベル:
      - `Points(points, layer=-1, color=-1, size=-1)`
      - `LinesBatch(segments, layer=-1, color=-1)`
      - `ArrowsBatch(segments, layer=-1, color=-1, size=-1, arrowtype=-1)`
    - `dumps() -> str`: 内部バッファを文字列として取り出す
    - `save(path: str)`: ファイルへ保存する

- **`YaplotDocument`**
  - 複数の `YaplotFrame` を持つドキュメントクラスです。
  - `frames: list[YaplotFrame]`
  - `current`: 現在アクティブなフレーム（プロパティ）
  - `new_frame() -> YaplotFrame`: 新しいフレームを追加してアクティブにする
  - 描画関連メソッド（`Line`, `Circle`, `Arrow`, `Points`, …）はすべて `current` フレームに委譲されます。
  - `dumps() -> str`: 全フレームを連結した文字列を返す
  - `save(path: str)`: 全フレームを含むファイルを保存する

### 低レベル関数 (`yaplotlib.core`)

Yaplot フォーマットを直接扱いたい場合は、低レベル関数をそのまま使うこともできます。

- ジオメトリ:
  - `Line(v0, v1) -> str`
  - `Circle(v0) -> str`
  - `Arrow(v0, v1) -> str`
  - `Polygon(vertices) -> str`
  - `Text(v, txt) -> str`
- スタイル:
  - `Color(x) -> str`
  - `Size(x) -> str`
  - `Layer(x) -> str`
  - `ArrowType(x) -> str`
  - `NewPage() -> str`

これらはすべて **1 行ぶんの Yaplot コマンド文字列を返す**だけの純粋関数です。

### パレットユーティリティ (`yaplotlib.palettes`)

- `RandomPalettes(N: int, offset: int = 10) -> str`
- `RainbowPalettes(N: int, offset: int = 10) -> str`
- `GradationPalettes(N: int, color, color1, offset: int = 10, maxval: float = 255.0) -> str`

いずれも、複数行の `@` コマンドを返します。`Yaplot` / `YaplotFrame` のメソッドとしても同名のものがあります。

## API ドキュメント (pdoc)

docstring と型ヒントから API リファレンスを生成するには [pdoc](https://pdoc.dev/) を使います。

```bash
# 開発用依存をインストール
poetry install

# HTML を docs/ に出力
make docs
```

ブラウザで `docs/index.html` を開くとモジュール一覧と各 API の説明を確認できます。

### GitHub Pages でドキュメントを公開する

1. リポジトリの **Settings** → **Pages** を開く。
2. **Build and deployment** の **Source** で **GitHub Actions** を選ぶ。
3. `main` または `master` にプッシュすると、ワークフローが pdoc を実行し、生成した HTML を GitHub Pages にデプロイする。
4. 数分後、`https://<ユーザ名>.github.io/yaplotlib/` で API ドキュメントが表示される。

（初回は **Settings** → **Pages** で **GitHub Actions** を選んだあと、一度 `main`/`master` にプッシュする必要があります。）

## 互換性について

- `import yaplotlib` はパッケージ（`yaplotlib/`）を読み込みます。`yaplotlib.Yaplot(...)` や `yaplotlib.Line(...)` など、従来どおり利用できます。
- 推奨するインポート例:

```python
from yaplotlib import Yaplot, YaplotDocument, Line, Circle
```

## ライセンス

ライセンス形態はこのリポジトリの `LICENSE` ファイルを参照してください。
