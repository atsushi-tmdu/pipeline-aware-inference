# Phase 3C TESS paired bootstrap：何をしているのか

## 1. 今回の目的

前段階では、保存済みの2,000個のnaive p値からTESS curveを計算した。
次の疑問は、alphaが小さくなるほどTESSが増えたように見える現象が、2,000反復という有限なMonte Carlo sampleの偶然だけで説明されるか、である。

今回のpaired bootstrapは、その不確実性を評価する最初の解析である。

## 2. 何を再標本化するのか

1つのcandidate libraryには、global null下の評価反復が2,000個ある。
各反復にはK=7とK=20のnaive p値が対応している。

bootstrapでは、この2,000個の反復IDを復元抽出し、新しい疑似的な2,000反復bankを作る。
これをデフォルトで20,000回繰り返す。

重要なのは、K=7とK=20を別々に抽出しないことである。
同じ元反復から得られた2つのp値を一緒に再標本化するため、K間のpaired structureが保たれる。

また、すべてのalphaは同じp値に異なる閾値を当てたものなので、alpha間の依存性も自動的に保たれる。

## 3. library間もpairedなのか

スクリプトは、high-dependencyとmixed-realisticで `replication` と `seed` が完全に一致するか確認する。

- 一致する場合：同じbootstrap indexを両libraryへ使う
- 一致しない場合：libraryごとに独立に再標本化する

デフォルトの `--cross-library-pairing auto` がこの判定を行う。

## 4. 各bootstrap sampleで何を計算するのか

各bootstrap sampleについて、次のalphaでnaive rejection probabilityを再計算する。

```text
0.20, 0.10, 0.05, 0.025, 0.01, 0.005
```

その後、

```text
TESS(alpha) = log{1 - pi(alpha)} / log(1 - alpha)
```

に変換する。

したがって、20,000本のTESS curveが得られる。

## 5. 何が出力されるのか

### TESS curve本体

各library、K、alphaについて、次を出力する。

- 元データからのTESS
- bootstrap standard error
- pointwise 95% interval
- alpha全体を同時に覆う95% simultaneous band

### K=20とK=7の差

各alphaについて、

```text
TESS(K=20) - TESS(K=7)
```

を計算する。

### library間の差

各Kとalphaについて、

```text
TESS(mixed-realistic) - TESS(high-dependency)
```

を計算する。

### difference-in-differences

各alphaについて、

```text
[mixedのK20-K7差] - [high-dependencyのK20-K7差]
```

を計算する。

これは、候補を7から20へ増やした影響が、異質なlibraryでどれだけ大きいかを直接表す。

### tail change

主要なscalar contrastとして、

```text
TESS(0.01) - TESS(0.10)
```

を計算する。

95% bootstrap intervalが0より上なら、TESSがlower tailへ向かって増加するという予備的証拠になる。

## 6. simultaneous bandとは何か

各alphaのpointwise 95% intervalを別々に見るだけでは、curve全体について多数の点を同時に見ている問題が残る。

そこで、各curve内のalpha全体についてmax-|z|方式のsimultaneous bandを作る。
これは、curveのどこか1点だけが偶然外れたことを、tail dependenceの証拠として過大評価しないための帯である。

## 7. 今回のbootstrapが含まない不確実性

今回再標本化するのは、保存済みのevaluation bank 2,000反復だけである。

naive empirical p値を作るために使われたnull-reference bankは固定したままである。
したがって、今回の区間は、

> frozen reference bankに条件づけたevaluation-bank Monte Carlo uncertainty

を表す。

reference bankを作り直した場合の変動まで含めるには、reference bankとevaluation bankを両方再標本化し、p値そのものを再計算するnested two-bank bootstrapが必要である。
これは次の段階として分離する。

## 8. この解析で何が分かれば成功か

特に見るべき結果は次の3つである。

1. mixed-realistic K=20の `TESS(0.01)-TESS(0.10)` の95%区間
2. 各libraryの `K20-K7` difference curve
3. difference-in-differences curveと、そのalpha=0.01での区間

これらが0より明確に大きければ、

- lower tailほど有効探索数が増える
- 候補追加の影響は異質なlibraryで大きい

という主張が強くなる。

ただし、これはまだPhase 3Cという限られたdesign上の結果であり、一般理論の確立ではない。
