# TESS理論ノート v0.5：極値係数との接続とGaussian copulaの厳密計算

作成日：2026-07-30

## 0. このノートの結論

今回定義した

\[
\operatorname{TESS}(\alpha)
=
\frac{\log\{1-\pi(\alpha)\}}{\log(1-\alpha)}
\]

は、各候補の帰無p値が一様分布であるとき、p値copulaの対角断面を使って

\[
\operatorname{TESS}(\alpha)
=
\frac{\log C(1-\alpha,\ldots,1-\alpha)}
{\log(1-\alpha)}
\]

と書ける。

この形は、極値理論で使われてきた **threshold-dependent extremal coefficient**
（閾値依存の極値係数）と数学的に一致する。

したがって、現時点での正しい位置づけは次のとおりである。

- TESSの数式そのものを完全に新しい依存指標として主張しない
- 既存のextremal coefficientを、adaptive model search後の偽陽性膨張に対応する
  **effective search size**として再解釈する
- pipeline null bankからこれを推定し、候補数・候補異質性・有意水準の関係を
  推論的に評価する点を研究の中心にする
- participation ratioなどのglobal dependence measureと、
  tail-specific inferential multiplicityの違いを明らかにする

これは研究を弱める発見ではない。むしろ、観測された現象に既存の極値理論という
数学的な背骨が見つかったことを意味する。

---

## 1. p値copulaによる表現

帰無仮説下で、候補 \(j=1,\ldots,K\) のmarginal p値を \(P_j\) とする。
各 \(P_j\) が連続一様分布 \(U(0,1)\) に従うと仮定する。

探索後のnaive rejectionは、

\[
\min_{1\le j\le K}P_j < \alpha
\]

に対応する。したがって、

\[
\pi(\alpha)
=
P\left(\min_j P_j<\alpha\right).
\]

ここで \(U_j=1-P_j\) とおくと、各 \(U_j\) も一様分布であり、

\[
1-\pi(\alpha)
=
P(P_1\ge\alpha,\ldots,P_K\ge\alpha)
=
P(U_1\le1-\alpha,\ldots,U_K\le1-\alpha).
\]

\(U=(U_1,\ldots,U_K)\) のcopulaを \(C\) とすれば、

\[
1-\pi(\alpha)=C(1-\alpha,\ldots,1-\alpha).
\]

よって、

\[
\boxed{
\operatorname{TESS}(\alpha)
=
\frac{\log C(1-\alpha,\ldots,1-\alpha)}
{\log(1-\alpha)}
}
\]

となる。

つまり、TESSはcopulaの**対角断面**だけで決まる。

---

## 2. 極値係数との関係

max-stable copulaでは、対角断面が

\[
C(u,\ldots,u)=u^\theta
\]

と書ける。このとき、

\[
\frac{\log C(u,\ldots,u)}{\log u}=\theta
\]

であり、\(\theta\in[1,K]\) はextremal coefficientと呼ばれる。

- \(\theta=1\)：完全依存
- \(\theta=K\)：独立
- 中間値：独立変数何個分に相当するか

max-stableでない一般copulaでは、この量はthreshold \(u\) に依存する。
今回 \(u=1-\alpha\) としたものがTESSである。

したがってTESSは、

> adaptive searchのglobal-null rejection probabilityから読み替えた、
> threshold-dependent extremal coefficient

と理解できる。

---

## 3. 境界条件

### 3.1 完全依存

すべてのp値が同一なら、

\[
C(u,\ldots,u)=u
\]

なので、

\[
\operatorname{TESS}(\alpha)=1.
\]

### 3.2 独立

p値が独立なら、

\[
C(u,\ldots,u)=u^K
\]

なので、

\[
\operatorname{TESS}(\alpha)=K.
\]

v0.4の100万反復simulationでは、この2境界を最大絶対誤差0.0794以内で回復した。

---

## 4. Gaussian copulaでの厳密な1次元積分

\(Z_1,\ldots,Z_K\) が標準正規で、すべての非対角相関が
\(\rho\in[0,1]\) のequicorrelated Gaussian vectorとする。

\[
P_j=1-\Phi(Z_j)
\]

とすれば、各 \(P_j\) は一様分布となる。

\(\rho<1\) のとき、common-factor representation

\[
Z_j=\sqrt{\rho}\,V+\sqrt{1-\rho}\,\varepsilon_j
\]

を使える。ここで \(V,\varepsilon_1,\ldots,\varepsilon_K\) は独立標準正規である。

\(z_\alpha=\Phi^{-1}(1-\alpha)\) とすると、

\[
1-\pi(\alpha)
=
P(Z_1\le z_\alpha,\ldots,Z_K\le z_\alpha)
\]

であり、\(V=v\) に条件づけると、

\[
P(Z_1\le z_\alpha,\ldots,Z_K\le z_\alpha\mid V=v)
=
\Phi\left(
\frac{z_\alpha-\sqrt{\rho}v}{\sqrt{1-\rho}}
\right)^K.
\]

よって、

\[
\boxed{
1-\pi(\alpha)
=
\int_{-\infty}^{\infty}
\phi(v)
\Phi\left(
\frac{z_\alpha-\sqrt{\rho}v}{\sqrt{1-\rho}}
\right)^K\,dv
}
\]

となる。

この積分は1次元なので、Monte Carloを使わず高精度に計算できる。

---

## 5. Gaussian copulaでtailへ行くとTESSがKへ近づく理由

固定した \(\rho<1\) のGaussian copulaは、極端なupper tailで漸近独立になる。

p値で書けば、任意の \(i\ne j\) について、

\[
P(P_i\le\alpha,\ P_j\le\alpha)=o(\alpha),
\qquad \alpha\downarrow0.
\]

有限個Kの候補について包除原理を使うと、

\[
\pi(\alpha)
=
P\left(\bigcup_{j=1}^K\{P_j\le\alpha\}\right)
=
K\alpha+o(\alpha).
\]

さらに、

\[
\log\{1-\pi(\alpha)\}=-K\alpha+o(\alpha),
\qquad
\log(1-\alpha)=-\alpha+o(\alpha),
\]

なので、

\[
\boxed{
\operatorname{TESS}(\alpha)\to K
\quad(\alpha\downarrow0,\ \rho<1)
}
\]

となる。

ただし、\(\rho\) が1に非常に近い場合、この収束は極めて遅い。
したがって、実用的なα範囲ではTESSが1に近いままでも、
数学的な極限ではKへ向かうことがあり得る。

---

## 6. 今回のGaussian simulationの意味

v0.4で観察した、

- 同じαならρが大きいほどTESSが小さい
- 同じρ<1ならαが小さいほどTESSが大きい
- 完全依存ρ=1だけは常にTESS=1
- 独立ρ=0では常にTESS=K

という挙動は、上のcopula対角とGaussian asymptotic independenceで説明できる。

したがって、mixed-realistic K=20でTESSがtailへ向かって増えた現象も、

> 通常域の相関だけでは捉えられない、候補性能のjoint-tail structure

を反映している可能性が高い。

---

## 7. 研究の新規性をどこに置くか

### 新規性として弱い主張

- \(\log C(u,\ldots,u)/\log u\) という式を初めて提案した
- 「独立変数何個分か」という解釈自体が完全に新しい

これらは既存のextremal coefficient文献と重なるため避ける。

### 新規性として有望な主張

1. adaptive biomedical ML pipelineの探索後偽陽性率と
   threshold-dependent extremal coefficientを明示的に接続した
2. local significance levelごとのeffective search sizeとして再解釈した
3. pipeline null bankからTESS curveを推定し、paired uncertaintyを評価した
4. nominal K、participation ratio、candidate heterogeneity、
   tail-specific multiplicityの違いを実証した
5. exact pipeline-aware inferenceの診断・説明指標として位置づけた
6. finite reference bankを含む推定問題を定式化した
7. ML candidate searchにおけるtail geometryという新しい問題設定を提示した

---

## 8. 用語について

TESSは直感的である一方、既存理論との接続を隠さない名称が望ましい。

暫定的な候補：

- Tail-Equivalent Search Size (TESS)
- Search Extremal Coefficient
- Pipeline Search Extremal Coefficient
- Threshold-Dependent Effective Search Size

論文では初出時に、

> We define the tail-equivalent search size, mathematically identical to a
> threshold-dependent extremal coefficient of the null p-value copula, and
> reinterpret it as the number of independent searches producing the same
> post-search global-null rejection probability.

のように明示するのが安全である。

---

## 9. 次に検討すべき理論

1. p値marginalが厳密な一様分布でない場合  
   empirical p値の離散性やsuper-uniformityをどう扱うか
2. winner selectionと \(\min_j P_j\) の対応条件  
   候補固有p値によるwinner検定と一般pipelineの違い
3. max-stable copulaならTESSがαに依存しないこと
4. asymptotic dependenceならTESSが有限のextremal coefficientへ収束すること
5. asymptotic independenceならTESSがKへ向かう条件
6. finite reference bankとevaluation bankの二重不確実性
7. TESSを補正係数として利用できる条件と、利用できない場合

---

## 10. 参考文献メモ

- Sibuya M. Bivariate extreme statistics, I. Ann Inst Stat Math. 1960;11:195–210.
  doi:10.1007/BF01682329.
- Buishand TA. Bivariate extreme-value data and the station-year method.
  J Hydrol. 1984;69:77–95. doi:10.1016/0022-1694(84)90157-4.
- Schlather M, Tawn JA. A dependence measure for multivariate and spatial
  extreme values: Properties and inference. Biometrika. 2003;90:139–156.
  doi:10.1093/biomet/90.1.139.
- Genest C, Sabbagh M. Comportement extrémal des copules diagonales et de
  Bertino. C R Math. 2020;358:1157–1167. doi:10.5802/crmath.135.

---

## 11. 現時点で理解しておけばよいこと

1. TESSはp値copulaの対角断面を測っている
2. 数学的にはthreshold-dependent extremal coefficientと接続する
3. Gaussian copulaでは1次元積分で厳密計算できる
4. \(\rho<1\) なら極端なtailでTESSはKへ向かう
5. 新規性は式そのものより、adaptive pipeline searchへの推論的再解釈と実証にある
