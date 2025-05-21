import unittest
import os
import shutil
import tempfile
import text2term # Assuming t2t.py is imported as text2term
from text2term.term import OntologyTermType
from text2term.mapper import Mapper

# Assuming these are available in your test environment or can be mocked
# For a real test, you might use a tiny dummy OWL file URL
DUMMY_ONTOLOGY_URL = "http://purl.obolibrary.org/obo/uberon.owl"
DUMMY_ONTOLOGY_ACRONYM = "uberon"

class TestOntologyCacheLoading(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary cache directory for all tests in this class."""
        cls.test_cache_dir = tempfile.mkdtemp(prefix="t2t_cache_test_")
        # Ensure the cache folder is set for text2term operations
        # You might need to temporarily patch text2term.onto_cache.DEFAULT_CACHE_FOLDER
        # or ensure functions take cache_folder as an argument.
        text2term.onto_cache.set_cache_folder(cls.test_cache_dir)
        print(f"Using temporary cache directory: {cls.test_cache_dir}")

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary cache directory after all tests are done."""
        print(f"Cleaning up temporary cache directory: {cls.test_cache_dir}")
        shutil.rmtree(cls.test_cache_dir)

    def setUp(self):
        """Clear cache before each test to ensure a clean state."""
        text2term.onto_cache.clear_cache(cache_folder=self.test_cache_dir)

    def test_cache_and_load_ontology_success(self):
        """
        Tests if an ontology can be successfully cached and then loaded from cache.
        This test will specifically try to trigger the 'Loading cached ontology from:' log.
        """
        # 1. Cache the ontology
        print(f"\n--- Caching {DUMMY_ONTOLOGY_ACRONYM} ---")
        try:
            # We'll need a way to mock text2term.OntologyTermCollector
            # or use a very small, local OWL file for a true unit test
            # For this example, we'll assume DUMMY_ONTOLOGY_URL is accessible and small.
            # In a true unit test, you would mock the network request and the parsing
            # of the OWL file to return a predefined set of OntologyTerm objects.
            cached_ontology_obj = text2term.cache_ontology(
                ontology_url=DUMMY_ONTOLOGY_URL,
                ontology_acronym=DUMMY_ONTOLOGY_ACRONYM,
                cache_folder=self.test_cache_dir
            )
            self.assertIsNotNone(cached_ontology_obj)
            print(f"--- Caching successful for {DUMMY_ONTOLOGY_ACRONYM} ---")
        except Exception as e:
            self.fail(f"Caching failed unexpectedly: {e}")

        # Verify the cached files exist
        expected_pickle_file = os.path.join(
            self.test_cache_dir,
            DUMMY_ONTOLOGY_ACRONYM,
            f"{DUMMY_ONTOLOGY_ACRONYM}-term-details.pickle"
        )
        self.assertTrue(os.path.exists(expected_pickle_file),
                        f"Expected cache pickle file not found: {expected_pickle_file}")
        self.assertGreater(os.path.getsize(expected_pickle_file), 0,
                           f"Cached pickle file is empty: {expected_pickle_file}")


        # 2. Attempt to load from cache using map_terms
        print(f"\n--- Attempting to map terms using cached {DUMMY_ONTOLOGY_ACRONYM} ---")
        source_terms = ["heart disease", "diabetes"]
        try:
            # The important part: use_cache=True
            mappings_df = text2term.map_terms(
                source_terms=source_terms,
                target_ontology=DUMMY_ONTOLOGY_ACRONYM,
                mapper=Mapper.TFIDF,
                use_cache=True,
                cache_folder=self.test_cache_dir
            )
            print(f"--- Mapping successful using cached {DUMMY_ONTOLOGY_ACRONYM} ---")
            self.assertFalse(mappings_df.empty, "Mappings DataFrame should not be empty")
            # You can add more assertions here to check the content of mappings_df
            # For example: self.assertIn("Source Term", mappings_df.columns)

        except Exception as e:
            self.fail(f"Loading from cache and mapping failed unexpectedly: {e}")

if __name__ == '__main__':
    # Enable more verbose logging for debugging during test run
    import logging
    logging.getLogger('text2term').setLevel(logging.DEBUG)
    unittest.main()