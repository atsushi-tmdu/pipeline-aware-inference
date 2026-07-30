# Asymptotic independence と asymptotic dependence のTESS比較

## 目的

同じ通常域の相関を持つ候補群でも、joint tail structureが違えば
TESS curveが異なることを示す。

比較する依存構造：

1. Gaussian copula  
   相関rho<1ではasymptotic independence。deep tailでTESS→K。

2. t-copula  
   有限自由度ではasymptotic dependence。deep tailでTESSは
   K未満のextremal-t coefficientへ収束する。

3. Gumbel–Hougaard extreme-value copula  
   max-stableなのでTESSはalphaによらず一定。

この比較によって、TESSが単なるPearson相関や候補数ではなく、
copula diagonalのtail geometryを測ることを確認する。
