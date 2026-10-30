#!/usr/bin/env python3
"""
Unit and Integration Test Suite for data_curator.py
===================================================
Runs using Python standard library unittest module (zero dependencies).
"""

import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from data_curator import (
    clean_column_name,
    jaro_winkler_similarity,
    levenshtein_similarity,
    calculate_quantiles,
    calculate_skewness,
    to_float,
    to_int,
    SanitizerEngine,
    DeduplicatorEngine,
    MissingValueHandler,
    OutlierHandler,
    FeatureEngineerEngine,
    DataScaler,
    DataAugmenter,
    StagingDeliverablesEngine,
    curate_pipeline,
    UCI_HEART_COLUMNS
)


class TestDataCuratorUnits(unittest.TestCase):
    """Unit tests for standalone helper functions and algorithmic engines."""

    def test_clean_column_name(self):
        self.assertEqual(clean_column_name("Patient Age (yr)"), "patient_age_yr")
        self.assertEqual(clean_column_name("  Resting BP  "), "resting_bp")
        self.assertEqual(clean_column_name("1st_measurement"), "c_1st_measurement")
        existing = {"age"}
        self.assertEqual(clean_column_name("age", existing), "age_1")

    def test_string_similarities(self):
        # Jaro-Winkler
        self.assertAlmostEqual(jaro_winkler_similarity("Martin", "Martin"), 1.0)
        self.assertGreater(jaro_winkler_similarity("Marthin", "Martin"), 0.90)

        # Levenshtein
        self.assertAlmostEqual(levenshtein_similarity("John", "John"), 1.0)
        self.assertGreater(levenshtein_similarity("John", "Jon"), 0.70)

    def test_quantiles_and_skewness(self):
        data = [10, 12, 14, 15, 16, 18, 20, 22, 24, 100]
        q1, q2, q3 = calculate_quantiles(data)
        self.assertGreater(q3, q1)
        self.assertEqual(q2, 17.0)
        skew = calculate_skewness(data)
        self.assertGreater(skew, 1.0)  # heavy right skew due to 100

    def test_to_float_and_int(self):
        self.assertEqual(to_float("42.5"), 42.5)
        self.assertEqual(to_float("?"), None)
        self.assertEqual(to_float(None), None)
        self.assertEqual(to_int("42.0"), 42)
        self.assertEqual(to_int("43.1"), 43)
        self.assertEqual(to_int("NA"), None)

    def test_pii_redaction(self):
        sanitizer = SanitizerEngine()
        text = "Patient SSN is 123-45-6789, email is test@med.org, phone 555-123-4567"
        redacted = sanitizer.redact_pii(text)
        self.assertIn("[REDACTED_SSN]", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertNotIn("123-45-6789", redacted)

    def test_deduplication(self):
        rows = [
            {"id": "1", "val": "A"},
            {"id": "1", "val": "A"},
            {"id": "2", "val": "B"}
        ]
        unique, dropped = DeduplicatorEngine.deduplicate_exact(rows, ["id", "val"])
        self.assertEqual(len(unique), 2)
        self.assertEqual(dropped, 1)

    def test_fuzzy_entity_resolution(self):
        rows = [
            {"name": "Jonathan Smith", "city": "Boston"},
            {"name": "Johnathan Smith", "city": "Boston"},
            {"name": "Eva Green", "city": "London"}
        ]
        resolved, clusters, _ = DeduplicatorEngine.resolve_entities_fuzzy(rows, ["name"], similarity_threshold=0.88)
        self.assertEqual(len(resolved), 3)
        self.assertIn("canonical_entity_id", resolved[0])
        # Jonathan and Johnathan should share the same entity id
        self.assertEqual(resolved[0]["canonical_entity_id"], resolved[1]["canonical_entity_id"])
        self.assertNotEqual(resolved[0]["canonical_entity_id"], resolved[2]["canonical_entity_id"])

    def test_missing_value_handler(self):
        schema = {"age": "float", "gender": "categorical"}
        rows = [
            {"age": 50.0, "gender": "M"},
            {"age": 60.0, "gender": "M"},
            {"age": None, "gender": "?"},
        ]
        # Allow rows with 100% missing to test imputation on completely missing row
        handler = MissingValueHandler(numeric_strategy="median", categorical_strategy="mode", max_missing_row=1.0)
        handler.fit(rows, schema)
        transformed, dropped = handler.transform(rows, schema)
        self.assertEqual(len(transformed), 3)
        # Median of 50 and 60 is 55.0
        self.assertEqual(transformed[2]["age"], 55.0)
        self.assertEqual(transformed[2]["gender"], "M")
        self.assertEqual(transformed[2]["age_is_missing"], 1)

    def test_outlier_clipping(self):
        schema = {"chol": "float"}
        rows = [{"chol": 200.0}, {"chol": 210.0}, {"chol": 220.0}, {"chol": 230.0}, {"chol": 800.0}]
        handler = OutlierHandler(method="iqr", treatment="clip", factor=1.5)
        handler.fit(rows, schema)
        curated, dropped = handler.transform(rows)
        self.assertEqual(len(curated), 5)
        # 800.0 should be clipped to the upper bound
        self.assertLess(curated[4]["chol"], 400.0)

    def test_standard_scaler(self):
        rows = [{"x": 10.0}, {"x": 20.0}, {"x": 30.0}]
        scaler = DataScaler(method="standard")
        scaler.fit(rows, ["x"])
        scaled = scaler.transform(rows)
        # Middle value (20.0) should be scaled to approximately 0.0
        self.assertAlmostEqual(scaled[1]["x"], 0.0, places=2)

    def test_data_augmentation(self):
        rows = [{"x": 10.0, "y": 20.0}, {"x": 12.0, "y": 22.0}, {"x": 14.0, "y": 24.0}]
        schema = {"x": "float", "y": "float"}
        augmenter = DataAugmenter(method="jitter", augment_ratio=0.5, random_seed=42)
        total, synth_count = augmenter.augment(rows, schema)
        self.assertGreater(synth_count, 0)
        self.assertEqual(len(total), len(rows) + synth_count)
        self.assertEqual(total[-1]["is_synthetic"], 1)


class TestCuratePipelineIntegration(unittest.TestCase):
    """End-to-End integration test simulating a full data pipeline."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="data_curator_test_"))
        self.out_dir = self.test_dir / "staged_output"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_pipeline_csv(self):
        csv_file = self.test_dir / "clinical_test.csv"
        rows = [
            ["patient_id", "full_name", "ssn", "age", "chol", "resting_bp", "diagnosis"],
            ["P01", "Alice Smith", "111-22-3333", "45", "210", "120", "0"],
            ["P01", "Alice Smith", "111-22-3333", "45", "210", "120", "0"], # Duplicate
            ["P02", "Bob Jones", "222-33-4444", "62", "280", "140", "1"],
            ["P03", "Charlie Day", "333-44-5555", "55", "?", "130", "0"],   # Missing chol
            ["P04", "Diana Ross", "444-55-6666", "70", "590", "160", "1"],  # Outlier chol
            ["P05", "Evan Wright", "555-66-7777", "38", "190", "115", "0"],
            ["P06", "Frank Castle", "666-77-8888", "50", "240", "135", "1"],
            ["P07", "Grace Kelly", "777-88-9999", "65", "260", "145", "1"],
            ["P08", "Hank Pym", "888-99-0000", "42", "200", "125", "0"],
        ]
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        audit = curate_pipeline(
            input_paths=[csv_file],
            output_dir=self.out_dir,
            target_column="diagnosis",
            dedup_keys=["patient_id"],
            entity_keys=["full_name"],
            outlier_treatment="clip",
            scale_method="standard",
            augment_method="jitter",
            augment_ratio=0.20,
            split_ratios=(0.60, 0.20, 0.20)
        )

        # Assert deliverables exist
        self.assertTrue((self.out_dir / "train.csv").is_file())
        self.assertTrue((self.out_dir / "val.csv").is_file())
        self.assertTrue((self.out_dir / "test.csv").is_file())
        self.assertTrue((self.out_dir / "curated_full.csv").is_file())
        self.assertTrue((self.out_dir / "staged_for_llm.jsonl").is_file())
        self.assertTrue((self.out_dir / "staged_tensors.json").is_file())
        self.assertTrue((self.out_dir / "scaler_parameters.json").is_file())
        self.assertTrue((self.out_dir / "staging_manifest.json").is_file())
        self.assertTrue((self.out_dir / "DATA_CARD.md").is_file())

        # Check deduplication
        self.assertEqual(audit.exact_duplicates_dropped, 1)

        # Check PII redaction in LLM output
        with open(self.out_dir / "staged_for_llm.jsonl", "r", encoding="utf-8") as f:
            first_llm_line = json.loads(f.readline())
            self.assertIn("[REDACTED_SSN]", first_llm_line["text"])
            self.assertNotIn("111-22-3333", first_llm_line["text"])

        # Check tensor structure
        with open(self.out_dir / "staged_tensors.json", "r", encoding="utf-8") as f:
            tensor_payload = json.load(f)
            self.assertIn("feature_names", tensor_payload)
            self.assertIn("X", tensor_payload)
            self.assertIn("y", tensor_payload)
            self.assertEqual(tensor_payload["target_name"], "diagnosis")


if __name__ == "__main__":
    unittest.main()
