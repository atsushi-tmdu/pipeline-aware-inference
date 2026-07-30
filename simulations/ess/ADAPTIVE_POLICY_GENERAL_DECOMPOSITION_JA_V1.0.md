# Adaptive policyの一般分解：なぜtoyと実MLで順序が逆転したのか v1.0

作成日：2026年7月30日

## 0. 結論

v0.7の独立p値toy modelでは、

\[
\mathrm{TESS}_{\mathrm{promising}}
<
\mathrm{TESS}_{\mathrm{random}}
<
\mathrm{TESS}_{\mathrm{rescue}}
\]

となった。

しかしPhase 3Cの実モデル再解析では、α=0.05で、

### High-dependency

- fixed base：1.86
- rescue：1.86
- random：1.95
- promising：2.02
- fixed full：2.02

### Mixed-realistic

- fixed base：4.16
- rescue：4.89
- random：5.53
- promising：6.10
- fixed full：6.91

となり、

\[
\mathrm{TESS}_{\mathrm{rescue}}
<
\mathrm{TESS}_{\mathrm{random}}
<
\mathrm{TESS}_{\mathrm{promising}}
\]

という逆順序が観察された。

これはtoy theoremの誤りではない。
toy theoremは、extra候補がbase候補と独立な特別な場合の結果である。

実MLでは、base-stageの「有望さ」と、追加モデルが新しいrejectionを生む能力が
正に関連している。そのため、有望なstateへ追加探索を配分する方が
推論的多重性を大きくした。

---

## 1. 一般設定

あるreplicationについて、base searchだけを行ったときの
α-level rejection indicatorを

\[
R_0(\alpha)\in\{0,1\}
\]

とする。

full searchまで行ったときのrejection indicatorを

\[
R_1(\alpha)\in\{0,1\}
\]

とする。

追加探索を起動するindicatorを

\[
A\in\{0,1\}
\]

とする。

adaptive policyの最終rejection indicatorは、

\[
\boxed{
R_A(\alpha)
=
R_0(\alpha)
+
A\{R_1(\alpha)-R_0(\alpha)\}
}
\]

と正確に書ける。

ここで、

\[
D_\alpha
=
R_1(\alpha)-R_0(\alpha)
\in\{-1,0,1\}
\]

を**incremental rejection effect**と呼ぶ。

---

## 2. Dの意味

### \(D_\alpha=1\)

base searchでは棄却しなかったが、full searchでは棄却した。

追加探索が新しいrejectionを作るstate。

### \(D_\alpha=0\)

baseとfullでrejection statusが変わらない。

追加探索がα-level decisionを変えないstate。

### \(D_\alpha=-1\)

baseでは棄却したが、fullでは棄却しなかった。

winnerが変わり、model-specific naive p値がかえって大きくなったstate。

MLではwinnerはraw performanceで選ばれ、p値はmodel-specific nullで計算されるため、
rejection eventは必ずしもnestedではない。したがって \(D=-1\) も起こり得る。

---

## 3. Proposition：policy rejection probabilityの一般分解

adaptive policyのglobal-null rejection probabilityを

\[
\pi_A(\alpha)=E\{R_A(\alpha)\}
\]

とすると、

\[
\boxed{
\pi_A(\alpha)
=
\pi_0(\alpha)
+
E(A D_\alpha)
}
\]

である。

ここで、

\[
\pi_0(\alpha)=E\{R_0(\alpha)\}
\]

はbase searchのrejection probabilityである。

### 証明

定義から、

\[
R_A=R_0+A(R_1-R_0)=R_0+AD_\alpha.
\]

両辺の期待値を取ればよい。証明終。

---

## 4. Random expansionとの比較

base stateと独立なrandom activation \(C\) を考え、

\[
E(C)=r
\]

とする。

このとき、

\[
\pi_{\mathrm{random}}
=
\pi_0+rE(D_\alpha).
\]

同じactivation rateを持つdata-dependent policy \(A\)、
すなわち \(E(A)=r\) について、

\[
\begin{aligned}
\pi_A-\pi_{\mathrm{random}}
&=
E(AD_\alpha)-rE(D_\alpha)\\
&=
\operatorname{Cov}(A,D_\alpha).
\end{aligned}
\]

したがって、

\[
\boxed{
\pi_A-\pi_{\mathrm{random}}
=
\operatorname{Cov}(A,D_\alpha)
}
\]

である。

固定αではTESSはπの単調増加関数なので、

\[
\operatorname{sign}
\{
\mathrm{TESS}_A-\mathrm{TESS}_{\mathrm{random}}
\}
=
\operatorname{sign}
\{
\operatorname{Cov}(A,D_\alpha)
\}.
\]

---

## 5. 解釈

### Covarianceが負

追加探索が主に、

- full searchへ進んでも新しいrejectionが生じにくいstate
- すでにbaseでrejectionしているstate

へ割り当てられている。

この場合、data-dependent policyのTESSはrandom expansionより小さい。

独立p値toy modelのpromising policyがこの場合である。

### Covarianceが正

追加探索が主に、

- extra modelによってbase non-rejectionがrejectionへ変わりやすいstate

へ割り当てられている。

この場合、data-dependent policyのTESSはrandom expansionより大きい。

Phase 3Cのpromising policyがこの場合である。

---

## 6. Complementary policy

balanced promising trigger \(A\) と、その補集合であるrescue trigger \(1-A\) を考える。

\(E(A)=1/2\) なら、

\[
\pi_{\mathrm{promising}}
-
\pi_{\mathrm{random}}
=
\operatorname{Cov}(A,D_\alpha),
\]

\[
\pi_{\mathrm{random}}
-
\pi_{\mathrm{rescue}}
=
\operatorname{Cov}(A,D_\alpha).
\]

したがって、rejection probabilityのscaleではrandom policyは
promisingとrescueの正確な中点になる。

TESSは非線形変換なので、TESS scaleで厳密な中点になるとは限らないが、
順序は同じである。

---

## 7. Toy theoremはこの一般式の特殊例

独立p値toy modelでは、extra候補がbase stateと独立である。

promising triggerはbaseがすでに小さいp値を持つstateへ探索を配分するため、
追加探索によるincremental gain \(D_\alpha=1\) と負に関連する。

したがって、

\[
\operatorname{Cov}(A,D_\alpha)<0
\]

となり、

\[
\mathrm{TESS}_{\mathrm{promising}}
<
\mathrm{TESS}_{\mathrm{random}}
<
\mathrm{TESS}_{\mathrm{rescue}}
\]

が得られる。

---

## 8. 実MLで逆転した理由

Phase 3Cでは、同じdataset replication上で全モデルが評価される。

あるreplicationが、

- 偶然分離しやすい
- 特定のノイズ方向を複数model familyが利用しやすい
- selection setで全般に高いAUROCを生みやすい

場合、base maximumが高いだけでなく、extra modelにも極端なperformanceが出やすい。

そのため、promising triggerは、

> extra modelによる新しいrejection gainが大きいstate

を選別した。

すなわち、

\[
\operatorname{Cov}(A,D_\alpha)>0
\]

となり、toyとは逆の順序になった。

---

## 9. 研究上の重要性

この一般分解は、TESS研究の中心命題をさらに明確にする。

探索多重性は、

- candidate count
- expected candidate count
- pairwise dependence
- activation rate

だけでは決まらない。

必要なのは、

\[
\boxed{
\text{activation policy}
\times
\text{incremental rejection opportunity}
}
\]

である。

同じ50% expansionでも、どのstateへ追加探索を配分するかによって
TESSは大きく異なる。

---

## 10. 次の解析

Phase 3C replication bankを使い、各αについて、

1. \(D_\alpha=1,0,-1\) の頻度
2. promising stateとrescue state別の \(E(D_\alpha)\)
3. \(\operatorname{Cov}(A,D_\alpha)\)
4. 上の分解式によるpolicy rejection probabilityの再現
5. base-stage score decileごとのincremental rejection probability
6. paired bootstrap区間

を計算する。

これにより、順序逆転のmechanismを直接可視化する。
