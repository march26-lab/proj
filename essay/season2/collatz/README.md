## コラッツ逆木のサンプルプログラム

Zenn記事「[コラッツ逆木は何分木なのか（Part 1）](https://zenn.dev/march26/articles/a01a82ab57ac8d)」に掲載したPythonコードを公開しています。

以下のコマンドは、各 `.py` ファイルを保存したフォルダをカレントディレクトリとして実行してください。

実行には `matplotlib` が必要です。

動作確認環境: `python3.10.0, matplotlib 3.10.9`。

---

### collatz_inv_tree.py: コラッツ逆木の表示

コラッツ逆木の深さ20までのノードとその数字を表示します。

#### 実行方法

```
python collatz_inv_tree.py
```

main()関数の冒頭 `MAX_DEPTH = 20` を書き換えることで、最大深さを変えられます。

大きくするにつれて指数的にメモリ消費が多くなります。ご注意ください。

---

### collatz_inv_tree_graph.py: コラッツ逆木の表示（グラフ版）

コラッツ逆木の深さ18までのノードをグラフで表示します。

#### 実行方法

```
python collatz_inv_tree_graph.py
```

main()関数の冒頭 `MAX_DEPTH = 18` を書き換えることで、最大深さを変えられます。

また `LABEL_MAX_DEPTH = 6` を書き換えることで、ノード部分に数字を表示する深さを変えられます。
