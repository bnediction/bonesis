import contextlib
import io
import unittest

import bonesis


class ProgressRecorder:
    def __init__(self):
        self.bars = []

    def __call__(self, **kwargs):
        bar = ProgressBarRecorder(kwargs)
        self.bars.append(bar)
        return bar


class ProgressBarRecorder:
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.descriptions = [kwargs["desc"]]
        self.closed = False
        self.updates = 0

    def set_description_str(self, desc, refresh=True):
        self.descriptions.append(desc)

    def update(self):
        self.updates += 1

    def refresh(self):
        return None

    def close(self):
        self.closed = True


class TestDiverseProgress(unittest.TestCase):
    def test_progress_can_be_overridden(self):
        domain = bonesis.InfluenceGraph.complete(
            "abcde",
            sign=1,
            loops=False,
            exact=True,
        )
        bo = bonesis.BoNesis(domain)
        bo.settings["quiet"] = True

        progress = ProgressRecorder()
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            solutions = list(bo.diverse_boolean_networks(limit=2, progress=progress))

        self.assertEqual(len(solutions), 2)
        self.assertEqual(stdout.getvalue(), "")

        self.assertEqual(len(progress.bars), 1)
        bar = progress.bars[0]
        self.assertEqual(bar.kwargs["bar_format"], "{desc}")
        self.assertIn("Found 0/2 solutions", bar.descriptions)
        self.assertTrue(any("Found 1/2 solution" in desc for desc in bar.descriptions))
        self.assertTrue(any("Found 2/2 solutions" in desc for desc in bar.descriptions))
        self.assertEqual(bar.updates, 2)
        self.assertTrue(bar.closed)
