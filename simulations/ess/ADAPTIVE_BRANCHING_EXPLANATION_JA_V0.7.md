# Adaptive branchingとTESS：なぜ平均候補数だけでは不十分か

作成日：2026年7月30日

## 0. この解析の目的

これまでのGaussian・t-copula解析は、固定されたK個の候補について、
候補間依存とtail levelがTESSをどう変えるかを調べた。

しかし、実際のmachine-learning developmentは固定K個の検定よりadaptiveである。

例：

- 初期モデルが有望なら追加tuningを行う
- 初期モデルが不十分なら別algorithmを追加する
- feature selection結果に応じて別pipelineを起動する
- fit failure時だけ代替modelを試す

この解析では、最大候補数と平均評価候補数が同じでも、
**追加探索を起動するrule**によってTESSが変わることを示す。

これはTESSを単なるeffective number of fixed testsではなく、
adaptive workflow全体のsearch multiplicityとして位置づけるための重要な例である。

---

## 1. 設計

最初にbase candidateを5個評価する。

必要に応じてextra candidateを15個追加する。

したがって、

- 最小候補数：5
- 最大候補数：20

である。

trigger thresholdは、base候補の最小p値がthreshold以下となる確率が50%になるように選ぶ。

\[
P(\min P_{\mathrm{base}}\le\tau)=0.5
\]

base candidateが5個なので、

\[
\tau=1-0.5^{1/5}\approx0.12945.
\]

これにより、次の3つのadaptive ruleはすべて平均12.5候補を評価する。

---

## 2. 比較する5つのworkflow

### 2.1 Fixed base

常にbase 5候補だけを評価する。

\[
\operatorname{TESS}(\alpha)=5.
\]

### 2.2 Fixed full

常に20候補すべてを評価する。

\[
\operatorname{TESS}(\alpha)=20.
\]

### 2.3 Random expansion

p値とは独立なcoin flipで50%の確率でextra候補を評価する。

平均評価候補数は12.5。

### 2.4 Promising-triggered expansion

base候補の最小p値が小さく、初期結果が有望なときだけextra候補を評価する。

\[
\min P_{\mathrm{base}}\le\tau
\]

で追加探索する。

これは「良さそうなモデルが見つかったので、さらにtuningやmodel searchを広げる」
workflowに対応する。

### 2.5 Rescue-triggered expansion

base候補の最小p値が十分小さくないときだけextra候補を評価する。

\[
\min P_{\mathrm{base}}>\tau
\]

で追加探索する。

これは「初期候補が不十分だったので、別algorithmや追加解析を試す」
workflowに対応する。

---

## 3. 重要な比較条件

random、promising、rescueはすべて、

- 最大候補数：20
- 最小候補数：5
- 追加候補数：15
- expansion probability：0.5
- 平均評価候補数：12.5

である。

違うのは、

> どのreplicationで追加15候補を評価するか

だけである。

したがって、TESSが異なれば、探索多重性は単なる最大Kや平均Kではなく、
**data-dependent activation rule**に依存することになる。

---

## 4. 厳密式

base最小p値を \(A\)、extra最小p値を \(B\) とする。

\[
S_0(a)=P(A\ge a)=(1-a)^{K_0},
\qquad
S_1(a)=P(B\ge a)=(1-a)^{K_1}.
\]

### Random expansion

expansion probabilityを \(r\) とすると、

\[
P(P_{\mathrm{winner}}\ge a)
=
S_0(a)\{(1-r)+rS_1(a)\}.
\]

### Promising-triggered expansion

\(a\le\tau\) では、

\[
P(P_{\mathrm{winner}}\ge a)
=
S_0(\tau)+\{S_0(a)-S_0(\tau)\}S_1(a).
\]

\(a>\tau\) では追加探索がa-level rejectionへ影響しないため、

\[
P(P_{\mathrm{winner}}\ge a)=S_0(a).
\]

### Rescue-triggered expansion

\(a\le\tau\) では、

\[
P(P_{\mathrm{winner}}\ge a)
=
S_0(a)-S_0(\tau)+S_0(\tau)S_1(a).
\]

\(a>\tau\) では、a未満でないbase結果はすべて追加探索を起動するので、

\[
P(P_{\mathrm{winner}}\ge a)=S_0(a)S_1(a).
\]

これらを

\[
\operatorname{TESS}(a)
=
\frac{\log P(P_{\mathrm{winner}}\ge a)}
{\log(1-a)}
\]

へ変換する。

---

## 5. 予想される結果

trigger probabilityが0.5の場合、3つのadaptive workflowの平均候補数はすべて12.5である。

しかしalpha=0.10付近では概ね、

- promising-triggered：約6.2
- random expansion：約9.8
- rescue-triggered：約15.6

となる。

つまり、平均12.5候補という同じsearch budgetでも、
TESSは約6から16まで変わり得る。

deep tailでは、3つとも平均候補数12.5へ近づく。

これは、非常に小さいalphaでは各候補がrejectionを生む一次近似が支配し、
activationされる平均候補数が効くためである。

一方、実用的な有限alphaでは、activation ruleと現在のp値の極端さの依存が重要となる。

---

## 6. この結果の新規性への意味

この例は、既存のfixed multiple-testing問題との差を明確にする。

- nominal Kだけでは不十分
- maximum Kだけでも不十分
- expected Kだけでも不十分
- pairwise correlationだけでも不十分

必要なのは、候補がどのdata stateで有効化され、winner selectionへ参加するかを含む
workflow-level search lawである。

TESSはそのworkflow全体がglobal null下で生むrejection inflationから定義されるため、
adaptive branchingを自然に含められる。

---

## 7. 解釈上の注意

このtoy exampleは、実際のML pipelineを完全に再現するものではない。

目的は、

> adaptive activationそのものがeffective search sizeを変える

という基本現象を、解析解が得られる最小例で示すことである。

次段階では、実際のfeature selection、conditional tuning、fit failure、
model-family expansionへ拡張する。
