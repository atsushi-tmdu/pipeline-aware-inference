# TESS研究：新規性の位置づけと研究戦略 v0.6

作成日：2026年7月30日

## 結論

現時点の研究には十分な論文化可能性がある。ただし、新規性を

> TESSという数式を初めて発明した

とは置けない。

effective number of tests、Šidák-equivalent multiplicity、extremal coefficient、
threshold-dependent extremal coefficient、p値水準によって変わるeffective numberは、
それぞれ既存研究がある。

新規性は、これらを **adaptive machine-learning pipeline searchの推論問題**へ接続し、
完全なpipeline null bankから推定・比較・不確実性評価する統合的frameworkに置く。

---

## 1. すでに知られていること

### 1.1 Effective number of tests

相関した複数検定を、同じFWERを生む独立検定数へ換算する考え方は古くからある。
遺伝統計では、eigenvalue法、minimum-p permutation法、Beta近似、
correlation/coplanar methodsなどが多数提案されている。

さらに、effective numberがlocal p-value levelに依存し得ることも既に指摘されている。

### 1.2 Extremal coefficient

極値理論では、最大値の同時分布を

\[
P(\max_j X_j\le x)=F(x)^\theta
\]

と表す \(\theta\in[1,K]\) が、独立変数何個分かを表すextremal coefficientとして知られる。

非max-stable分布では、この係数がthresholdに依存することも既知である。

### 1.3 Gaussian・t・max-stable copulaのtail behavior

- Gaussian copula：相関が1未満なら漸近独立
- t-copula：有限自由度では漸近依存
- extreme-value copula：extremal coefficientがthresholdに依存しない

これらの数学的性質そのものは新規ではない。

---

## 2. 今回の研究で新規になり得る部分

### 2.1 固定された複数検定ではなく、adaptive pipeline全体を対象にする

既存effective-number研究の多くは、事前に列挙された固定M個の検定を対象にする。

今回の対象は、次を含む宣言済みworkflow全体である。

- preprocessing
- feature selection
- candidate algorithms
- hyperparameter tuning
- fit failures
- winner selection
- tie rules
- evaluation metric
- optional analysis branches

このworkflowを一つのsearch mapとして扱い、最終winnerに対するnaive inferenceの
global-null rejection probabilityからpipeline-level search multiplicityを定義する。

### 2.2 nominalな候補数を定義しにくいworkflowにも適用できる

adaptive feature selectionやconditional tuningでは、「何個の検定をしたか」を
単純に数えられないことがある。

TESSは、最終的なpipelineのglobal-null behaviorだけから定義できるため、
明示的なcandidate countが曖昧でも計算できる。

### 2.3 exact pipeline-aware inferenceの診断指標として使う

TESSを単なる近似補正係数としてではなく、

- なぜnaive inferenceが壊れたか
- 候補追加が探索負荷をどれだけ増やしたか
- library heterogeneityがどのtailで効くか
- structural dimensionとinferential multiplicityがなぜ違うか

を説明する診断指標として位置づける。

### 2.4 pipeline null bankからcurveとpaired uncertaintyを推定する

今回すでに行ったこと：

- TESSをlocal alphaのcurveとして推定
- K=7/20を同じreplicationでpaired比較
- library差とdifference-in-differencesを推定
- simultaneous confidence bandを作成
- Gaussian exact calculationでsimulation結果を検証

この一式は、単なるeffective-numberの一点推定よりかなり広い。

### 2.5 candidate heterogeneity × K × tailのinteraction

主な発見は、TESSが何でも一様にtail-dependentということではない。

mixed-realistic K=20でのみ強いtail増加が生じ、
Kを増やす影響がlibrary heterogeneityによって増幅され、
そのinteractionがdeep tailでさらに大きくなった。

この現象をadaptive ML searchとして定式化・実証する部分が重要である。

---

## 3. 現状のままでは弱い部分

次の形で論文を出すと、新規性が弱いと判断される可能性が高い。

1. TESSの式を新指標として提示するだけ
2. Gaussian copulaの既知のtail behaviorを再確認するだけ
3. participation ratioよりTESSが大きかったと報告するだけ
4. 2種類のlibrary、K=7/20だけで一般論を主張する
5. TESSをそのまま補正係数として推奨する
6. 既存effective-number文献との違いを曖昧にする

---

## 4. 強い論文にするための必須要素

### 4.1 Pipeline-level definition

固定K個のp値だけでなく、一般のadaptive workflow \(\mathcal A\) が返す
naive winner p-value \(P_{\mathcal A}\) に対して、

\[
\operatorname{TESS}_{\mathcal A}(\alpha)
=
\frac{\log P_0(P_{\mathcal A}\ge\alpha)}
{\log(1-\alpha)}
\]

を定義する。

### 4.2 Marginal calibrationの整理

candidate p値が離散的またはsuper-uniformの場合、TESSは

- search multiplicity
- marginal miscalibration
- finite reference-bank error

を混在させる可能性がある。

したがって、次を区別する必要がある。

- raw pipeline TESS
- marginally calibrated TESS
- finite-bank corrected/estimated TESS

これは既存研究との差別化にもなる。

### 4.3 一般的な命題

候補例：

1. no-search baselineではTESS=1
2. independent calibrated K-candidate searchではTESS=K
3. max-stable p-value copulaではTESSがalphaに依存しない
4. asymptotic independenceでは一定条件下でTESS→K
5. asymptotic dependenceではTESS→有限のextremal coefficient
6. candidate duplicationがTESSを不変に保つ条件
7. adaptive branch追加に対するTESSの単調性条件

### 4.4 より広いdesign grid

- K
- global dependence
- tail dependence
- block structure
- duplicate candidates
- heterogeneous marginals
- data-dependent candidate activation
- preprocessing/tuning depth
- sample size
- finite reference bank size

を系統的に変える。

### 4.5 既存法との比較

少なくとも以下と比較する。

- nominal K
- participation ratio
- Li–Ji
- Galwey
- correlation-based effective number
- permutation-derived single effective number
- copula-derived effective number
- exact pipeline max-statistic reference

---

## 5. 現時点での新規性評価

### 数式そのもの

**低い。**  
同型のeffective-number、extremal-coefficientの概念は既存。

### Gaussian/tail theoryそのもの

**低～中。**  
既知理論だが、pipeline searchへの接続には価値がある。

### Adaptive ML pipelineへの再解釈

**中～高の可能性。**  
今回の検索では、完全なadaptive pipeline null bankから
threshold-specific effective search size curveを推定する同一frameworkは明確には見つかっていない。

### 現在の実証結果

**中～高。**  
candidate heterogeneity、K、tailのinteractionとpaired uncertaintyは興味深い。

### 完成した方法論論文として

**十分狙えるが、理論と一般化をもう一段追加する必要がある。**

---

## 6. 推奨する論文の主張

### 避ける

> We propose a novel formula for the effective number of tests.

### 推奨

> We develop a pipeline-level framework that reinterprets a threshold-dependent
> effective number of tests, equivalently a diagonal extremal coefficient, as the
> inferential search size induced by an adaptive machine-learning workflow.

> Unlike structural dimension measures or nominal candidate counts, the proposed
> curve quantifies the global-null rejection inflation of the entire declared
> development pipeline at each inferential threshold.

> We show that candidate-set expansion can have little effect in redundant
> libraries but a large and tail-amplified effect in heterogeneous libraries.

---

## 7. Working title案

### 方法論を前面に出す

**Inferential Search Size of Adaptive Machine-Learning Pipelines:  
A Threshold-Dependent Extremal-Coefficient Framework**

### 現象を前面に出す

**Why the Effective Size of a Machine-Learning Search Space Depends on the Inferential Tail**

### 医学MLへの接続を強める

**Quantifying Search Multiplicity After Adaptive Biomedical Machine-Learning Development**

---

## 8. 現時点での判断

新規性は「大丈夫」だが、条件付きである。

- TESSという名前や式だけでは不十分
- 既存multiple-testing・extreme-value literatureを正面から引用する
- adaptive pipelineという対象、pipeline-null estimation、tail curve、
  uncertainty、structural dimensionとの乖離を中心に置く
- 一般的なadaptive branching simulationと理論命題を追加する

この方向で進めれば、前研究の小さな続編ではなく、
独立した統計的方法論研究として成立する可能性が高い。
