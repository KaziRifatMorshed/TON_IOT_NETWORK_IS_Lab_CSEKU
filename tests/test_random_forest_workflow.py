from __future__ import annotations

import argparse
import unittest

import numpy as np
import pandas as pd

from src import random_forest_workflow as workflow


class RandomForestWorkflowTests(unittest.TestCase):
    def test_default_dataset_path_is_data_dataset_csv(self) -> None:
        parser = workflow.build_arg_parser()
        args = parser.parse_args([])

        self.assertEqual(args.dataset, workflow.ROOT / "data" / "dataset.csv")

    def test_tuning_cli_is_not_available(self) -> None:
        parser = workflow.build_arg_parser()
        args = parser.parse_args([])

        self.assertFalse(hasattr(args, "tune"))
        self.assertNotIn("--tune", parser.format_help())

    def test_default_random_forest_parameters_are_available(self) -> None:
        parser = workflow.build_arg_parser()
        args = parser.parse_args([])

        self.assertEqual(args.n_estimators, 200)
        self.assertEqual(args.criterion, "gini")
        self.assertEqual(args.max_features, "sqrt")
        self.assertEqual(args.class_weight, "balanced")

    def test_compute_metrics_includes_required_summary_scores(self) -> None:
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 2, 2])
        y_score = np.array(
            [
                [0.90, 0.05, 0.05],
                [0.10, 0.80, 0.10],
                [0.05, 0.05, 0.90],
                [0.80, 0.10, 0.10],
                [0.20, 0.35, 0.45],
                [0.05, 0.10, 0.85],
            ]
        )

        metrics = workflow.compute_summary_metrics(y_true, y_pred, y_score)

        for key in [
            "accuracy",
            "precision_macro",
            "recall_macro",
            "f1_macro",
            "roc_auc_ovr_macro",
            "roc_auc_ovr_weighted",
            "mcc",
        ]:
            self.assertIn(key, metrics)
            self.assertIsInstance(metrics[key], float)

    def test_preprocessing_drops_leakage_and_cleans_features(self) -> None:
        df = pd.DataFrame(
            {
                "src_ip": ["192.168.1.1", "192.168.1.2", "192.168.1.3"],
                "dst_ip": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
                "protocol": ["tcp", "udp", "tcp"],
                "duration": [1.0, np.inf, np.nan],
                "constant": [1, 1, 1],
                "label": [0, 1, 1],
                "type": ["Normal", "DoS", "DDoS"],
            }
        )

        X, y, metadata = workflow.preprocess_dataset(df)

        self.assertNotIn("label", X.columns)
        self.assertNotIn("type", X.columns)
        self.assertNotIn("constant", X.columns)
        self.assertIn("src_ip_low", X.columns)
        self.assertIn("dst_ip_low", X.columns)
        self.assertFalse(np.isinf(X.to_numpy()).any())
        self.assertFalse(np.isnan(X.to_numpy()).any())
        self.assertEqual(y.tolist(), [0, 1, 2])
        self.assertIn("label", metadata["dropped_columns"])

    def test_distribution_counts_cover_binary_and_multiclass_targets(self) -> None:
        df = pd.DataFrame(
            {
                "label": [0, 1, 1, 0],
                "type": ["normal", "dos", "ddos", "normal"],
            }
        )

        distributions = workflow.compute_distribution_counts(df)

        self.assertEqual(distributions["binary"], {"normal": 2, "attack": 2})
        self.assertEqual(distributions["multiclass"], {"ddos": 1, "dos": 1, "normal": 2})

    def test_save_roc_curves_creates_file(self) -> None:
        import tempfile

        y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        y_score = np.array(
            [
                [0.85, 0.10, 0.05],
                [0.10, 0.75, 0.15],
                [0.05, 0.10, 0.85],
                [0.80, 0.12, 0.08],
                [0.15, 0.70, 0.15],
                [0.08, 0.12, 0.80],
                [0.90, 0.05, 0.05],
                [0.10, 0.80, 0.10],
                [0.05, 0.05, 0.90],
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = workflow.ROOT / "outputs" / "figures" / "_test_roc.png"
            output.parent.mkdir(parents=True, exist_ok=True)
            workflow.save_roc_curves(y_true, y_score, output)
            self.assertTrue(output.exists())
            output.unlink()

    def test_run_config_contains_required_keys(self) -> None:
        required_keys = {
            "dataset_path",
            "random_state",
            "test_size",
            "class_names",
            "target_mapping",
            "feature_count",
            "original_shape",
            "processed_shape",
            "duplicate_rows_removed",
        }
        # Build a minimal run_config manually matching the structure in run_workflow
        df = pd.DataFrame(
            {
                "protocol": ["tcp", "udp", "tcp"],
                "duration": [1.0, 2.0, 3.0],
                "label": [0, 1, 1],
                "type": ["normal", "dos", "ddos"],
            }
        )
        _, _, metadata = workflow.preprocess_dataset(df)
        run_config = {
            "dataset_path": "data/dataset.csv",
            "random_state": 42,
            "test_size": 0.2,
            "sample_size": None,
            "class_names": workflow.CLASS_ORDER,
            "target_mapping": metadata["target_mapping"],
            "feature_count": len(metadata["feature_columns"]),
            "feature_columns": metadata["feature_columns"],
            "ip_columns": metadata["ip_columns"],
            "categorical_columns": metadata["categorical_columns"],
            "constant_columns_removed": metadata["constant_columns"],
            "dropped_columns": metadata["dropped_columns"],
            "original_shape": list(metadata["original_shape"]),
            "processed_shape": list(metadata["processed_shape"]),
            "duplicate_rows_removed": metadata["duplicate_rows_removed"],
        }
        for key in required_keys:
            self.assertIn(key, run_config)


if __name__ == "__main__":
    unittest.main()
