import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'template_profiler_panel.tests.dummy_settings')

import django
from django.template import Context, Template

django.setup()

from template_profiler_panel.panels.template import TemplateProfilerPanel, template_rendered


class TemplateProfilerPanelTestCase(unittest.TestCase):
    def setUp(self):
        super(TemplateProfilerPanelTestCase, self).setUp()
        toolbar = MagicMock()
        toolbar.config = {"SKIP_TEMPLATE_PREFIXES": ()}
        self.panel = TemplateProfilerPanel(toolbar)
        self.panel.record_stats = MagicMock()
        self.template_rendered_receiver = MagicMock()
        template_rendered.connect(self.template_rendered_receiver)

    def tearDown(self):
        template_rendered.disconnect(self.template_rendered_receiver)
        self.panel.disable_instrumentation()
        self.panel.templates = []

    def test_render_wrapped(self):
        self.panel.enable_instrumentation()
        t = Template('')
        t.render(Context({}))

        self.assertGreater(self.template_rendered_receiver.call_count, 0)

    def test_generate_stats_disabled_instrumentation(self):
        t = Template('')
        t.render(Context({}))

        self.panel.generate_stats(MagicMock(), MagicMock())

        args = self.panel.record_stats.call_args[0][0]
        self.assertEqual(len(args['templates']), 0)
        self.assertEqual(len(args['summary']), 0)

    def test_generate_stats_enabled_instrumentation(self):
        self.panel.enable_instrumentation()

        t = Template('')
        t.render(Context({}))

        self.panel.generate_stats(MagicMock(), MagicMock())
        self.panel.disable_instrumentation()

        args = self.panel.record_stats.call_args[0][0]
        self.assertEqual(len(args['templates']), 1)
        self.assertEqual(len(args['summary']), 1)

    def test_title(self):
        self.assertTrue(self.panel.title)

    def test_template(self):
        self.assertTrue(self.panel.template)
