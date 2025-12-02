# coding: utf-8

from __future__ import absolute_import
import unittest
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'template_profiler_panel.tests.dummy_settings'

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

from django.core.wsgi import get_wsgi_application
from django.template import Context, Template

from template_profiler_panel.panels.template import TemplateProfilerPanel, template_rendered


class TemplateProfilerPanelTestCase(unittest.TestCase):
    def setUp(self):
        super(TemplateProfilerPanelTestCase, self).setUp()
        self.panel = TemplateProfilerPanel(MagicMock())
        self.panel.record_stats = MagicMock()
        self.template_rendered_receiver = MagicMock()
        self.request = MagicMock()
        self.response = MagicMock()
        template_rendered.connect(self.template_rendered_receiver)

    def tearDown(self):
        template_rendered.disconnect(self.template_rendered_receiver)

    def test_render_wrapped(self):
        t = Template('')
        t.render(Context({}))

        self.assertGreater(self.template_rendered_receiver.call_count, 0)

    def test_process_response_disabled_instrumentation(self):
        t = Template('')
        t.render(Context({}))

        self.panel.process_response(self.request, self.response)

        args = self.panel.record_stats.call_args[0][0]
        self.assertEqual(len(args['templates']), 0)
        self.assertEqual(len(args['summary']), 0)

    def test_process_response_enabled_instrumentation(self):
        self.panel.enable_instrumentation()

        t = Template('')
        t.render(Context({}))

        self.panel.process_response(self.request, self.response)
        self.panel.disable_instrumentation()

        args = self.panel.record_stats.call_args[0][0]
        self.assertEqual(len(args['templates']), 1)
        self.assertEqual(len(args['summary']), 1)

    def test_title(self):
        self.assertTrue(self.panel.title)

    def test_template(self):
        self.assertTrue(self.panel.template)

    def test_get_export_data(self):
        class DummyNode(object):
            def __str__(self):
                return "dummy_node"

        self.panel.get_stats = MagicMock(return_value={
            'request_id': 'req-1',
            'templates': [{
                'name': 'base.html',
                'time': 12.5,
                'level': 2,
                'relative_start': 0.0,
                'relative_end': 12.5,
                'offset_p': 0.0,
                'duration_p': 100.0,
                'rel_duration_p': 100.0,
                'processing_timeline': [{
                    'name': DummyNode(),
                    'relative_start': 0.0,
                    'relative_end': 6.25,
                    'duration': 6.25,
                    'offset_p': 0.0,
                    'rel_duration_p': 50.0,
                    'position': (1, 5),
                    'level': 0,
                }],
            }],
            'summary': [('base.html', 12.5)],
        })

        payload = self.panel.get_export_data()

        self.assertEqual(payload['schema'], self.panel.export_schema)
        self.assertEqual(payload['meta']['request_id'], 'req-1')
        self.assertEqual(payload['meta']['render_window_ms'], 12.5)
        self.assertEqual(payload['summary']['render_calls'], 1)
        self.assertEqual(payload['summary']['total_render_time_ms'], 12.5)
        self.assertEqual(payload['by_template'][0]['name'], 'base.html')
        template = payload['templates'][0]
        self.assertEqual(template['name'], 'base.html')
        self.assertEqual(template['timeline']['duration_pct'], 100.0)
        self.assertEqual(template['nodes'][0]['name'], 'dummy_node')
        self.assertEqual(template['nodes'][0]['template_position'], [1, 5])


if __name__ == '__main__':
    application = get_wsgi_application()
    unittest.main()
