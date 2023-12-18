import json
import sys
from typing import Any


def main() -> None:
    new_tests: list[dict[str, Any]] = []

    for old_test in json.load(sys.stdin):
        name = old_test['name']
        new_test = {'name': name}

        assert frozenset(old_test.keys()).issubset(['name', 'check']), (
            'cannot handle top-level keys other than \'name\' and \'check\''
        )

        if 'check' in old_test:
            check_block = old_test['check']

            assert frozenset(check_block.keys()).issubset([
                'select', 'result', 'status', 'desc'
            ]), (
                'cannot handle check block keys other than \'select\', '
                '\'result\', \'status\', and \'desc\''
            )
            assert not ('result' in check_block and 'status' in check_block), (
                'cannot handle check block containing both \'result\' and '
                '\'status\' simultaneously'
            )

            if 'result' in check_block:
                new_test['do'] = [
                    {
                        '@do': 'merge',
                        'action': 'select',
                        'select': check_block['select'],
                        'use_strings': True,
                    },
                    {'@do': 'flattenSelect'},
                    {'@do': 'mergeSelect', '@rows': check_block['result']},
                ]
            elif 'status' in check_block:
                new_test['do'] = {
                    '@do': 'update',
                    '@status': check_block['status'],
                    'action': 'select',
                    'select': check_block['select'],
                }
            else:
                assert False, (
                    'neither \'result\' nor \'status\' in check block in '
                    f'test {name!r}'
                )

            if 'desc' in check_block:
                new_test['#'] = check_block['desc']

        else:
            assert False, f'\'check\' not in test {name!r}'

        new_tests.append(new_test)

    json.dump(new_tests, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
