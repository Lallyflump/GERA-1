"""Synthetic tests only: HTTP is loopback and all provider transports are fakes."""
from dataclasses import replace
from http.client import HTTPConnection, HTTPResponse
import io
import json
import os
from pathlib import Path
import socket
from threading import Thread, BoundedSemaphore
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import local_bridge
from gera1.adapters.nebius import NebiusTextModel
from gera1.orchestrator.brownie import synthesize_brownie
from gera1.workflows.demo_brownie import run_demo

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = local_bridge.CONTEXT


class BrownieSynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_demo(ROOT)

    def answer(self, result=None, model=None):
        return synthesize_brownie(result=self.result if result is None else result,
                                  context=CONTEXT, model=model)

    def test_model_receives_full_brownie_facts_and_missing_checks(self):
        model = Mock()
        model.complete.return_value = 'Cannot confirm: eggs short; butter unknown; production unchecked.'
        answer = self.answer(model=model)
        self.assertTrue(answer.model_used)
        facts = json.loads(model.complete.call_args.args[1])
        self.assertEqual('13', facts['recipe']['requested_quantity'])
        self.assertEqual('2', facts['recipe']['batches'])
        self.assertEqual('24', facts['recipe']['output_quantity'])
        self.assertEqual(1500, facts['finance']['remaining_minor'])
        self.assertEqual('4', facts['ingredients']['items'][1]['shortage'])
        self.assertIsNone(facts['ingredients']['items'][2]['available'])
        self.assertEqual('unknown', facts['finished_stock']['items'][0]['availability'])
        self.assertEqual(list(self.result.missing), facts['missing'])
        self.assertIn('allergen_declaration', answer.missing)
        self.assertIn('saleability_release', answer.missing)
        self.assertIn('proposal_to_ingredient_cost_link', answer.missing)
        self.assertEqual(list(self.result.evidence), facts['evidence'])

    def test_blocked_or_mismatched_envelope_never_reaches_model(self):
        for changes in ({'status': 'denied'}, {'status': 'error'}, {'audit_id': None},
                        {'actor_id': 'other'}, {'request_id': 'other'}, {'business_id': 'other'},
                        {'capability': 'finance:affordability:read'}, {'data': None}):
            with self.subTest(changes=changes):
                model = Mock()
                self.assertEqual('blocked', self.answer(replace(self.result, **changes), model).recommendation)
                model.complete.assert_not_called()

    def test_bad_specialist_identity_or_receipt_never_reaches_model(self):
        review = self.result.data
        bad_reviews = [
            replace(review, specialist_audits=()),
            replace(review, finance=replace(review.finance, audit_id=None)),
            replace(review, finance=replace(review.finance, business_id='other')),
            replace(review, calendar=replace(review.calendar, request_id='other')),
            replace(review, ingredients=replace(review.ingredients, availability=replace(
                review.ingredients.availability, business_id='other'))),
            replace(review, recommendation='approved'), replace(review, order_accepted=True),
            replace(review, stages=(('finance', 'denied'),)),
        ]
        for bad in bad_reviews:
            model = Mock()
            self.assertEqual('blocked', self.answer(replace(self.result, data=bad), model).recommendation)
            model.complete.assert_not_called()

    def test_provider_failure_or_invalid_output_uses_offline_explanation(self):
        expected = self.answer()
        for value in ('', ' ', None, 123, b'bytes', 'x' * 2501, TimeoutError('sensitive-provider-error')):
            with self.subTest(value_type=type(value).__name__):
                model = Mock()
                if isinstance(value, Exception):
                    model.complete.side_effect = value
                else:
                    model.complete.return_value = value
                self.assertEqual(expected, self.answer(model=model))

    def test_untrusted_model_cannot_change_authoritative_decision_or_records(self):
        model = Mock()
        model.complete.return_value = 'Approved! Reserve stock and send an invoice.'
        before = self.result
        answer = self.answer(model=model)
        self.assertEqual('cannot_confirm', answer.recommendation)
        self.assertEqual(before.missing, answer.missing)
        self.assertFalse(self.result.data.order_accepted)
        self.assertEqual(before, self.result)

    def test_summary_excludes_raw_messages_and_evidence_details(self):
        finance = replace(self.result.data.finance, message='PRIVATE_PATH_SENTINEL')
        result = replace(self.result, data=replace(self.result.data, finance=finance))
        model = Mock()
        model.complete.return_value = 'Cannot confirm.'
        self.answer(result, model)
        self.assertNotIn('PRIVATE_PATH_SENTINEL', model.complete.call_args.args[1])
        self.assertNotIn('workbook', model.complete.call_args.args[1])

    def test_offline_bridge_remains_offline_with_key_set_and_fixtures_unchanged(self):
        before = {p: p.read_bytes() for p in (ROOT / 'data/fixtures').glob('*.json')}
        with patch.dict(os.environ, {'NEBIUS_API_KEY': 'synthetic-test-key'}), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')):
            payload = local_bridge.evaluate_brownie('brownie')
        self.assertEqual('offline', payload['toby']['status'])
        self.assertFalse(payload['toby']['model_used'])
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_model_gets_no_free_text_question_or_browser_records(self):
        model = Mock()
        model.complete.return_value = 'Cannot confirm.'
        payload = local_bridge.evaluate_brownie('brownie QUESTION_SENTINEL 999 by tomorrow', model=model)
        self.assertNotIn('QUESTION_SENTINEL', model.complete.call_args.args[1])
        self.assertEqual('13', json.loads(model.complete.call_args.args[1])['recipe']['requested_quantity'])
        self.assertEqual('live', payload['toby']['status'])  # Mocked, not live verification evidence.
        self.assertFalse(payload['result']['data']['model_used'])

    def test_missing_key_is_explicit_fallback_without_transport(self):
        transport = Mock()
        payload = local_bridge.evaluate_brownie('brownie', model=NebiusTextModel(api_key='', transport=transport))
        self.assertEqual('fallback', payload['toby']['status'])
        transport.assert_not_called()

    def test_blocked_workflow_withholds_data(self):
        model = Mock()
        with patch.object(local_bridge, 'run_demo', return_value=replace(self.result, status='error')):
            payload = local_bridge.evaluate_brownie('brownie', model=model)
        self.assertIsNone(payload['result'])
        self.assertEqual('blocked', payload['toby']['status'])
        model.complete.assert_not_called()


class AdapterContractTests(unittest.TestCase):
    def test_existing_adapter_request_is_bounded_and_server_authenticated(self):
        transport = Mock(return_value=io.BytesIO(json.dumps({'choices': [{'message': {
            'content': 'Synthetic explanation'}}]}).encode()))
        model = NebiusTextModel(api_key='synthetic-test-key', transport=transport)
        self.assertEqual('Synthetic explanation', model.complete('system', 'synthetic facts'))
        request = transport.call_args.args[0]
        self.assertEqual(NebiusTextModel.URL, request.full_url)
        self.assertEqual('Bearer synthetic-test-key', request.get_header('Authorization'))
        data = json.loads(request.data)
        self.assertEqual(NebiusTextModel.MODEL, data['model'])
        self.assertEqual(500, data['max_tokens'])
        self.assertEqual(20, transport.call_args.kwargs['timeout'])
        self.assertNotIn('synthetic-test-key', request.data.decode())
        self.assertEqual(1, transport.call_count)

    def test_malformed_and_oversized_provider_responses_fail(self):
        for raw in (b'not json', b'{}', b'x' * 256001,
                    b'{"choices":[{"message":{"content":null}}]}'):
            with self.subTest(size=len(raw)):
                model = NebiusTextModel(api_key='synthetic-test-key', transport=Mock(return_value=io.BytesIO(raw)))
                with self.assertRaises((ValueError, KeyError)):
                    model.complete('system', 'facts')


class MemoryConnection:
    """Exercise BaseHTTPRequestHandler's actual HTTP parsing without an OS socket."""
    def __init__(self, raw):
        self.raw = raw
        self.output = io.BytesIO()

    def makefile(self, *args, **kwargs):
        return io.BytesIO(self.raw)

    def sendall(self, raw):
        self.output.write(raw)

    def settimeout(self, value):
        pass


class BridgeHTTPTests(unittest.TestCase):
    def setUp(self):
        self.server = SimpleNamespace(server_port=8765, model=None, review_slot=BoundedSemaphore(1))

    def request(self, *, method='POST', path='/api/brownie-demo', body=None, headers=None):
        raw_body = (json.dumps({'question': 'brownie'}) if body is None else body).encode()
        defaults = {'Host': '127.0.0.1:8765', 'Origin': 'http://127.0.0.1:8765',
                    'Content-Type': 'application/json', 'Content-Length': str(len(raw_body))}
        defaults.update(headers or {})
        raw = (f'{method} {path} HTTP/1.1\r\n' + ''.join(
            f'{k}: {v}\r\n' for k, v in defaults.items()) + '\r\n').encode() + raw_body
        conn = MemoryConnection(raw)
        local_bridge.Handler(conn, ('127.0.0.1', 12345), self.server)
        response = HTTPResponse(MemoryConnection(conn.output.getvalue()))
        response.begin()
        return response.status, dict(response.getheaders()), response.read()

    def test_http_handler_offline_workflow_returns_toby_and_decision(self):
        status, headers, raw = self.request()
        body = json.loads(raw)
        self.assertEqual(200, status)
        self.assertEqual('no-store', headers['Cache-Control'])
        self.assertEqual('offline', body['toby']['status'])
        self.assertEqual('cannot_confirm', body['result']['data']['recommendation'])
        self.assertFalse(body['result']['data']['order_accepted'])

    def test_http_through_mocked_adapter_returns_explanation_without_key(self):
        transport = Mock(return_value=io.BytesIO(b'{"choices":[{"message":{"content":"Cannot confirm synthetic order."}}]}'))
        with patch.object(self.server, 'model', NebiusTextModel(api_key='synthetic-test-key', transport=transport)):
            status, _, raw = self.request()
        self.assertEqual(200, status)
        self.assertEqual('live', json.loads(raw)['toby']['status'])
        self.assertEqual('Cannot confirm synthetic order.', json.loads(raw)['toby']['explanation'])
        self.assertNotIn(b'synthetic-test-key', raw)
        self.assertEqual(1, transport.call_count)

    def test_http_provider_failure_falls_back_without_disclosing_error(self):
        model = Mock()
        model.complete.side_effect = RuntimeError('PRIVATE_EXCEPTION_SENTINEL')
        with patch.object(self.server, 'model', model):
            status, _, raw = self.request()
        self.assertEqual(200, status)
        self.assertEqual('fallback', json.loads(raw)['toby']['status'])
        self.assertNotIn(b'PRIVATE_EXCEPTION_SENTINEL', raw)

    def test_rejects_cross_origin_and_wrong_host_before_workflow(self):
        with patch.object(local_bridge, 'run_demo') as run:
            for headers in ({'Origin': 'https://example.com'}, {'Origin': 'null'},
                            {'Origin': ''}, {'Host': 'evil.example'}, {'Sec-Fetch-Site': 'cross-site'}):
                self.assertEqual(403, self.request(headers=headers)[0])
            run.assert_not_called()

    def test_rejects_invalid_or_extra_input_before_workflow(self):
        with patch.object(local_bridge, 'run_demo') as run:
            for body in ('{}', '[]', '{', '{"question": 1}', '{"question":"bread"}',
                         '{"question":"brownie","actor_id":"owner"}',
                         '{"question":"brownie","question":"brownie"}',
                         '{"question":NaN}', '[' * 1500 + ']' * 1500,
                         json.dumps({'question': 'brownie' + 'x' * 1000})):
                self.assertEqual(400, self.request(body=body)[0])
            self.assertEqual(415, self.request(headers={'Content-Type': 'text/plain'})[0])
            self.assertEqual(413, self.request(body='x' * 4097)[0])
            self.assertEqual(400, self.request(headers={'Content-Length': 'invalid'})[0])
            run.assert_not_called()

    def test_busy_request_does_not_start_another_workflow(self):
        self.server.review_slot.acquire()
        try:
            with patch.object(local_bridge, 'run_demo') as run:
                self.assertEqual(429, self.request()[0])
                run.assert_not_called()
        finally:
            self.server.review_slot.release()

    def test_internal_error_is_sanitized_and_slot_released(self):
        with patch.object(local_bridge, 'run_demo', side_effect=RuntimeError('PRIVATE_PATH_SENTINEL')):
            status, _, raw = self.request()
        self.assertEqual(503, status)
        self.assertNotIn(b'PRIVATE_PATH_SENTINEL', raw)
        self.assertTrue(self.server.review_slot.acquire(blocking=False))
        self.server.review_slot.release()

    def test_only_interface_assets_are_served(self):
        for path in ('/', '/script.js', '/styles.css', '/assets/toby.webp'):
            self.assertEqual(200, self.request(method='GET', path=path)[0])
        for path in ('/../README.md', '/.env', '/assets/', '/README.txt', '/api/brownie-demo'):
            self.assertEqual(404, self.request(method='GET', path=path)[0])

    def test_non_loopback_binding_rejected(self):
        with self.assertRaises(ValueError):
            local_bridge.BridgeServer(('0.0.0.0', 0))


class LoopbackIntegrationTests(unittest.TestCase):
    def test_socket_roundtrip_when_environment_permits(self):
        try:
            server = local_bridge.BridgeServer(('127.0.0.1', 0))
        except PermissionError:
            self.skipTest('Environment prohibits local server sockets; handler tested in memory')
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        conn = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        try:
            conn.request('POST', '/api/brownie-demo', body='{"question":"brownie"}', headers={
                'Content-Type': 'application/json', 'Origin': f'http://127.0.0.1:{server.server_port}'})
            response = conn.getresponse()
            self.assertEqual(200, response.status)
            self.assertEqual('offline', json.loads(response.read())['toby']['status'])
        finally:
            conn.close()
            server.shutdown()
            server.server_close()
            thread.join()
