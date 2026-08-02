from __future__ import annotations
import json, math, tempfile, unittest
from pathlib import Path
import numpy as np
from d2_core import exact_independent_normal_benchmark
from d2_validation_core import benchmark_derivatives_finite_difference, benchmark_dgp, sample_dgp
import d2_validate

ROOT=Path(__file__).resolve().parents[1]

class D2NumericalTests(unittest.TestCase):
    def test_independent_benchmark_matches_closed_form(self):
        observed=benchmark_dgp('independent_normal',0.05,0.5,1.0)
        expected=exact_independent_normal_benchmark(0.05,0.5,1.0)
        for key in ['pi','tess','a0','b1','d_u','sigma_e2_sqrt_n','sigma_r_d1_2_sqrt_B','sigma_trigger_2_sqrt_B','sigma_r_d2_2_sqrt_B','sigma_pi2_sqrt_n']:
            mapped='sigma_pi_d2_2_sqrt_n' if key=='sigma_pi2_sqrt_n' else key
            self.assertAlmostEqual(observed[mapped],expected[key],places=8)

    def test_dependent_benchmarks_are_finite(self):
        for name in ['gaussian_factor','nonlinear_smooth']:
            b=benchmark_dgp(name,0.05,0.5,1.0)
            for key in ['pi','tess','sigma_r_d2_2_sqrt_B','sigma_pi_d2_2_sqrt_n','sigma_trigger_delta_2_sqrt_n']:
                self.assertTrue(math.isfinite(float(b[key])))
                self.assertGreater(float(b[key]),0.0)

    def test_boundary_derivatives(self):
        for name in ['independent_normal','gaussian_factor','nonlinear_smooth']:
            result=benchmark_derivatives_finite_difference(name,0.05,0.5)
            for stem in ['dq0','dq1','dc']:
                self.assertAlmostEqual(result[f'numeric_dm_{stem}'],result[f'analytic_dm_{stem}'],delta=2e-5)

    def test_sampling_shapes(self):
        rng=np.random.default_rng(123)
        for name in ['independent_normal','gaussian_factor','nonlinear_smooth']:
            x=sample_dgp(rng,name,100)
            self.assertEqual(x.shape,(100,3))
            self.assertTrue(np.isfinite(x).all())

    def test_locked_config(self):
        cfg=json.loads((ROOT/'D2_NUMERICAL_CONFIG.json').read_text())
        d2_validate._validate_config(cfg)
        self.assertEqual(cfg['outer_repetitions'],3000)
        self.assertEqual(cfg['bootstrap_repetitions'],999)
        self.assertIn('bootstrap-normal',cfg['primary_interval'])
        nonlinear=[x for x in cfg['data_generating_laws'] if x['name']=='nonlinear_smooth'][0]
        self.assertEqual(nonlinear['peak_amplitude'],2.0)
        self.assertEqual(nonlinear['sigma1'],0.45)

    def test_smoke_config(self):
        cfg=json.loads((ROOT/'D2_NUMERICAL_CONFIG_SMOKE.json').read_text())
        d2_validate._validate_config(cfg)
        self.assertEqual(cfg['status'],'smoke_not_scientific')

    def test_one_outer_each_dgp(self):
        for idx,name in enumerate(['independent_normal','gaussian_factor','nonlinear_smooth']):
            b=benchmark_dgp(name,0.05,0.5,1.0)
            row=d2_validate._one_outer(master_seed=9,dgp_index=idx,cell_index=idx,outer_index=0,dgp_name=name,B=200,n=200,alpha=0.05,activation_rate=0.5,bootstrap_repetitions=25,benchmark=b)
            self.assertTrue(math.isfinite(row['pi_hat']))
            self.assertTrue(math.isfinite(row['trigger_delta_pi_bootstrap_sd']))

if __name__=='__main__': unittest.main()
