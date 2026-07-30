# Adaptive branching TESS：Propositionと証明 v0.8

作成日：2026年7月30日

## 0. この文書の目的

v0.7では、最大候補数と平均評価候補数が同じでも、
追加探索を起動するruleだけでTESSが大きく変わることを数値的に確認した。

この文書では、その現象を解析式に基づく正式なPropositionとして整理する。

結論は次のとおりである。

> 同じ最大候補数、同じ追加探索確率、同じ平均評価候補数を持つsearch policyでも、
> data-dependent activation ruleが異なれば、有限の有意水準におけるTESSは異なる。

balanced designでは、すべての \(\alpha\in(0,1)\) について、

\[
\mathrm{TESS}_{\mathrm{promising}}(\alpha)
<
\mathrm{TESS}_{\mathrm{random}}(\alpha)
<
\mathrm{TESS}_{\mathrm{rescue}}(\alpha)
\]

が成り立つ。

一方で、\(\alpha\downarrow0\) では3方式とも同じ平均評価候補数へ収束する。

---

## 1. 設定

base候補を \(K_0\) 個、追加候補を \(K_1\) 個とする。

global null下で、各候補のp値を独立な \(U(0,1)\) とする。

\[
P_{01},\ldots,P_{0K_0},
\qquad
P_{11},\ldots,P_{1K_1}.
\]

base候補の最小p値と追加候補の最小p値を、

\[
A=\min_{1\le j\le K_0}P_{0j},
\qquad
B=\min_{1\le j\le K_1}P_{1j}
\]

とする。

したがって、

\[
S_0(\alpha)=P(A\ge\alpha)=(1-\alpha)^{K_0},
\]

\[
S_1(\alpha)=P(B\ge\alpha)=(1-\alpha)^{K_1}.
\]

threshold \(\tau\) は、

\[
P(A\le\tau)=P(A>\tau)=\frac12
\]

となるように選ぶ。

すなわち、

\[
(1-\tau)^{K_0}=\frac12,
\qquad
\tau=1-2^{-1/K_0}.
\]

---

## 2. 3つのadaptive policy

### 2.1 Promising-triggered policy

base結果が有望なときだけ追加探索する。

\[
W_P=
\begin{cases}
\min(A,B), & A\le\tau,\\
A, & A>\tau.
\end{cases}
\]

### 2.2 Random-expansion policy

base結果と独立なcoin \(C\sim\operatorname{Bernoulli}(1/2)\) により追加探索する。

\[
W_R=
\begin{cases}
\min(A,B), & C=1,\\
A, & C=0.
\end{cases}
\]

### 2.3 Rescue-triggered policy

base結果が不十分なときだけ追加探索する。

\[
W_S=
\begin{cases}
A, & A\le\tau,\\
\min(A,B), & A>\tau.
\end{cases}
\]

各 \(W\) は、そのworkflowで最終的に得られる最小naive p値である。

---

## 3. Proposition 1：平均候補数は同じ

### Proposition

3つのpolicyはいずれも追加探索を確率 \(1/2\) で起動する。

したがって、評価される候補数の期待値はすべて、

\[
E[N_{\mathrm{eval}}]
=
K_0+\frac{K_1}{2}
\]

である。

また、3方式はいずれも、

- 最小候補数：\(K_0\)
- 最大候補数：\(K_0+K_1\)

を共有する。

### 証明

Promising policyでは、

\[
P(A\le\tau)=\frac12.
\]

Rescue policyでは、

\[
P(A>\tau)=\frac12.
\]

Random policyでは定義上、追加探索確率は \(1/2\) である。

したがって、すべてのpolicyで、

\[
E[N_{\mathrm{eval}}]
=
K_0+K_1P(\text{expansion})
=
K_0+\frac{K_1}{2}.
\]

証明終。

---

## 4. Proposition 2：non-rejection probabilityの厳密式

\[
Q_m(\alpha)=P(W_m\ge\alpha)
\]

とする。

### 4.1 \(\alpha\le\tau\) の場合

\[
Q_P(\alpha)
=
\frac12+
\left\{
S_0(\alpha)-\frac12
\right\}S_1(\alpha),
\]

\[
Q_R(\alpha)
=
S_0(\alpha)
\frac{1+S_1(\alpha)}{2},
\]

\[
Q_S(\alpha)
=
S_0(\alpha)-\frac12+
\frac12S_1(\alpha).
\]

### 4.2 \(\alpha>\tau\) の場合

\[
Q_P(\alpha)=S_0(\alpha),
\]

\[
Q_R(\alpha)
=
S_0(\alpha)\frac{1+S_1(\alpha)}{2},
\]

\[
Q_S(\alpha)=S_0(\alpha)S_1(\alpha).
\]

これらはv0.7で使用した解析式である。

---

## 5. Proposition 3：TESSの厳密な順序

### Proposition

\(K_1\ge1\) とする。このとき、すべての \(\alpha\in(0,1)\) について、

\[
Q_P(\alpha)>Q_R(\alpha)>Q_S(\alpha).
\]

したがって、

\[
\boxed{
\mathrm{TESS}_P(\alpha)
<
\mathrm{TESS}_R(\alpha)
<
\mathrm{TESS}_S(\alpha)
}
\]

が成り立つ。

さらに、

\[
Q_R(\alpha)
=
\frac{Q_P(\alpha)+Q_S(\alpha)}{2}
\]

である。

### 証明：\(\alpha\le\tau\)

上の厳密式から、

\[
Q_P-Q_R
=
\frac12
\{1-S_0(\alpha)\}
\{1-S_1(\alpha)\}.
\]

同様に、

\[
Q_R-Q_S
=
\frac12
\{1-S_0(\alpha)\}
\{1-S_1(\alpha)\}.
\]

\(\alpha\in(0,1)\)、\(K_0,K_1\ge1\) では、

\[
0<S_0(\alpha)<1,
\qquad
0<S_1(\alpha)<1
\]

なので、両差は正である。

したがって、

\[
Q_P>Q_R>Q_S.
\]

### 証明：\(\alpha>\tau\)

この場合、

\[
Q_P-Q_R
=
\frac12S_0(\alpha)\{1-S_1(\alpha)\}>0,
\]

\[
Q_R-Q_S
=
\frac12S_0(\alpha)\{1-S_1(\alpha)\}>0.
\]

したがって同じ順序が成り立つ。

TESSは、

\[
\mathrm{TESS}(\alpha)
=
\frac{\log Q(\alpha)}{\log(1-\alpha)}
\]

であり、分母は負である。

したがって、\(Q\)の順序はTESSでは反転し、

\[
\mathrm{TESS}_P
<
\mathrm{TESS}_R
<
\mathrm{TESS}_S.
\]

証明終。

---

## 6. Proposition 4：trigger thresholdより上での極端な差

### Proposition

\(\alpha>\tau\) では、

\[
\mathrm{TESS}_P(\alpha)=K_0,
\]

\[
\mathrm{TESS}_S(\alpha)=K_0+K_1.
\]

### 解釈

Promising policyでは、追加探索が起動する時点でbase p値がすでに
\(\tau<\alpha\) 以下である。

したがって、追加探索は\(\alpha\)-level rejectionを新しく作らない。
そのためTESSはbase候補数 \(K_0\) と同じである。

Rescue policyでは、\(\alpha>\tau\) のとき、
baseが\(\alpha\)以上であるすべてのnon-rejection stateで追加探索が起動する。

したがって、\(\alpha\)-levelのnon-rejectionにはbaseとextraの両方が
\(\alpha\)以上である必要があり、固定full searchと同じになる。

---

## 7. Proposition 5：deep-tail limit

### Proposition

3つのpolicyすべてについて、

\[
\boxed{
\lim_{\alpha\downarrow0}
\mathrm{TESS}(\alpha)
=
K_0+\frac{K_1}{2}
}
\]

が成り立つ。

### 証明

\(\alpha\downarrow0\) で、

\[
S_0(\alpha)
=
1-K_0\alpha+o(\alpha),
\]

\[
S_1(\alpha)
=
1-K_1\alpha+o(\alpha).
\]

各policyの厳密式へ代入すると、いずれも、

\[
Q(\alpha)
=
1-
\left(
K_0+\frac{K_1}{2}
\right)\alpha
+
o(\alpha)
\]

となる。

したがって、

\[
\log Q(\alpha)
=
-
\left(
K_0+\frac{K_1}{2}
\right)\alpha
+
o(\alpha),
\]

\[
\log(1-\alpha)
=
-\alpha+o(\alpha).
\]

よって、

\[
\frac{\log Q(\alpha)}{\log(1-\alpha)}
\longrightarrow
K_0+\frac{K_1}{2}.
\]

証明終。

---

## 8. Corollary：maximum Kとexpected KではTESSを決められない

3つのpolicyは、

- 同じ最小K
- 同じ最大K
- 同じexpansion probability
- 同じexpected K
- 同じbase候補分布
- 同じextra候補分布

を持つ。

それにもかかわらず、任意の有限 \(\alpha\in(0,1)\) でTESSは異なる。

したがって、

> adaptive workflowの有限threshold search multiplicityは、
> maximum candidate countにもexpected candidate countにも還元できない。

TESSはcandidate exposureの量だけでなく、

\[
\text{activation event}
\quad\text{と}\quad
\text{current extremeness}
\]

の依存関係を反映する。

---

## 9. 数値例

\(K_0=5\)、\(K_1=15\) とすると、

\[
\tau=1-2^{-1/5}\approx0.12945.
\]

すべてのadaptive policyで、

\[
E[N_{\mathrm{eval}}]=12.5.
\]

しかし \(\alpha=0.10\) では、

| Policy | TESS |
|---|---:|
| Promising-triggered | 6.2316 |
| Random expansion | 9.8019 |
| Rescue-triggered | 15.5923 |

となる。

同じ平均12.5候補でも、activation ruleだけで約9.36の差が生じる。

---

## 10. 論文での位置づけ

このPropositionは、TESS研究の中心的な理論例になり得る。

既存のfixed multiple-testing settingとの違いを、次のように表せる。

> Effective search size is a property of the entire adaptive policy—not merely
> of the candidate set, its maximum size, or its expected computational budget.

ただし、これは独立一様p値による最小toy modelである。

次に必要なのは、実際のML workflowで、

- promising-triggered hyperparameter tuning
- rescue-triggered model-family expansion
- random-budget-matched expansion

を比較し、同じ順序関係が生じるか確認することである。
