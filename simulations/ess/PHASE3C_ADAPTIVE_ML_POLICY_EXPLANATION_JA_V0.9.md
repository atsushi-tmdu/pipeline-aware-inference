# Phase 3Cモデルを用いたadaptive search policy再解析 v0.9

作成日：2026年7月30日

## 0. 目的

v0.7–v0.8では、独立一様p値によるtoy modelで、

- 最大候補数が同じ
- 平均評価候補数が同じ
- 追加探索確率が同じ

であっても、追加候補をどのdata stateで起動するかによってTESSが異なることを示した。

次は、保存済みPhase 3C full runの**実際のモデル別性能**を使い、
同じ現象がmachine-learning candidate libraryでも起きるかを検証する。

この解析では新しいモデル fittingを行わない。
Phase 3Cで保存されたmodel-level null reference bankとevaluation bankを再利用する。

---

## 1. 使用するデータ

各candidate libraryについて、次のファイルを読む。

```text
null_reference_model_metrics.csv
evaluation_model_metrics.csv
candidate_library_manifest.csv
independent_inference_results.csv
```

対象library：

- high_dependency_linear_20
- mixed_realistic_20

global null条件：

- target AUROC = 0.50
- feature selection = none
- selection event count = 100
- metric = ROC AUC

---

## 2. Candidate構成

Phase 3Cと同じcandidate orderを使う。

- base candidate：先頭7モデル
- extra candidate：残り13モデル
- maximum K：20

各replicationで、base 7モデルのselection ROC AUC最大値をbase-stage statisticとする。

---

## 3. Expansion threshold

null reference bankにおけるbase-stage maximumの中央値付近を使い、
promising expansion probabilityが約50%となるthresholdを決める。

selection ROC AUCには有限標本によるtieがあるため、threshold上のtieでは
deterministic randomized tie ruleを使う。

同じthreshold ruleをevaluation bankへ適用する。

---

## 4. 比較するpolicy

### Fixed base

常にbase 7モデルだけからwinnerを選ぶ。

### Fixed full

常に20モデルすべてからwinnerを選ぶ。

### Random expansion

base結果とは独立に約50%のreplicationでextra 13モデルを追加する。

### Promising-triggered expansion

base-stage maximumがthresholdより良いときにextraモデルを追加する。

### Rescue-triggered expansion

base-stage maximumがthresholdより悪いときにextraモデルを追加する。

Promisingとrescueは同じtrigger ruleの補集合である。

---

## 5. Winnerとnaive p値

各policyで有効化されたcandidate subsetの中から、
selection ROC AUCが最大のモデルをwinnerとする。

winnerのnaive empirical p値は、Phase 3Cと同じ考え方で、

> winnerモデルが最初から事前指定されていた

かのように、そのモデル固有のnull reference distributionと比較して求める。

\[
p_{\mathrm{naive}}
=
\frac{
1+\#\{T^{(b)}_{\mathrm{winner}}\ge T_{\mathrm{obs}}\}
}{
B+1
}.
\]

このp値から各alphaにおけるglobal-null rejection probabilityとTESSを計算する。

---

## 6. 重要な内部検証

再構成したfixed-baseおよびfixed-fullのp値を、
既存の `independent_inference_results.csv` の

- pool size 7
- pool size 20
- method = naive_empirical

と比較する。

一致すれば、winner selection、candidate order、empirical p-value計算が
既存Phase 3Cと整合していることが確認できる。

---

## 7. 不確実性評価

evaluation replicationを単位とするpaired bootstrapを行う。

同じbootstrap sample内で全policy・全alphaを同時に再計算し、

- TESS curveのpointwise 95%区間
- rescue minus promising
- random minus promising
- rescue minus random

を推定する。

このbootstrapは、保存済みnull reference bankに条件づけた評価bankの不確実性を扱う。

---

## 8. 主要な問い

### 問い1

ML model libraryでも、

\[
\mathrm{TESS}_{\mathrm{promising}}
<
\mathrm{TESS}_{\mathrm{random}}
<
\mathrm{TESS}_{\mathrm{rescue}}
\]

というtoy theoremと同じ順序が現れるか。

### 問い2

このpolicy effectはhigh-dependency libraryより
mixed-realistic libraryで大きいか。

### 問い3

policy間の差はalphaによって変化するか。

### 問い4

最大Kや平均評価Kだけではpolicy-level multiplicityを説明できないか。

---

## 9. 解釈

toy theoremと同じ順序が出れば、

> Effective search size is a property of the adaptive development policy,
> not merely of the candidate library or its average computational budget.

という主張が、解析解だけでなく実際のML candidate performanceでも支持される。

順序が完全には再現されない場合も重要である。
その場合、候補間依存、モデル固有marginal、winner identity、
selection metricの離散性がadaptive activationと相互作用していることを意味する。

---

## 10. 注意点

- これは保存済みnull bankの再解析であり、新しい独立simulationではない
- trigger thresholdはnull reference bankでcalibrateする
- naive p値はmarginal empirical p値であり、pipeline-adjusted p値ではない
- TESSを補正係数として推奨する解析ではない
- finite reference-bank uncertaintyはまだ含まない
