import json
from subprocess import Popen, PIPE

cmd = ['perl', '-MJSON', '-MYAML', '-e', 'print Dump(decode_json(<STDIN>))']


def dumps(o):
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    out, _ = proc.communicate(json.dumps(o).encode('UTF-8'))
    assert proc.returncode == 0
    return out
