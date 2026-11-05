"""pytest is not installable in this environment (no matching distribution through the package proxy), so run each test_*.py by importing it and
calling every top-level test_* function in a fresh process per file; record pass/fail/error with the exception text.  Does not modify behaviour.
usage: python3 tools/t1_run_tests.py <test_file.py> <outjson>"""
import sys, os, json, time, traceback, importlib.util
f, out = sys.argv[1], sys.argv[2]; sys.argv = ['x']; sys.path.insert(0, os.getcwd())
t0 = time.time(); rec = dict(file=f, results=[], import_error=None)
try:
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for n in sorted(k for k in dir(m) if k.startswith('test_') and callable(getattr(m, k))):
        t = time.time()
        try: getattr(m, n)(); rec['results'].append(dict(test=n, status='pass', s=round(time.time() - t, 1)))
        except BaseException as e: rec['results'].append(dict(test=n, status='fail', s=round(time.time() - t, 1), error=(type(e).__name__ + ': ' + str(e))[:300], tb=traceback.format_exc()[-600:]))
except BaseException as e: rec['import_error'] = (type(e).__name__ + ': ' + str(e))[:300]
rec['total_s'] = round(time.time() - t0, 1); json.dump(rec, open(out, 'w'), indent=1)
print(f, sum(r['status'] == 'pass' for r in rec['results']), 'pass', sum(r['status'] == 'fail' for r in rec['results']), 'fail', rec['import_error'] or '')
