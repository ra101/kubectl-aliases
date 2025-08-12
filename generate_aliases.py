#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import itertools
import os.path
import sys


def main():
    # (alias, full, allow_when_oneof, incompatible_with)
    cmds = [('k', 'kubebin', None, None)]

    globs = [('sys', '--namespace=kube-system', None, None)]

    ops = [
        ('a', 'apply --recursive -f', None, None),
        ('ak', 'apply -k', None, ['sys']),
        ('k', 'kustomize', None, ['sys']),
        ('kb', 'kustomize build', None, ['sys']),
        ('ex', 'exec -i -t', None, None),
        ('lo', 'logs -f', None, None),
        ('lop', 'logs -f -p', None, None),
        ('e', 'edit', None, None),
        ('rr', 'rollout restart', None, None),
        ('rs', 'rollout status', None, None),
        ('s', 'scale', None, None),
        ('sr', 'set resources', None, None),
        ('as', 'autoscale', None, None),
        ('asdep', 'autoscale deployment', None, None),
        ('asrc', 'autoscale replicaset', None, None),
        ('p', 'proxy', None, ['sys']),
        ('pa', 'patch', None, ['sys']),
        ('pf', 'port-forward', None, ['sys']),
        ('g', 'get', None, None),
        ('d', 'describe', None, None),
        ('rm', 'delete', None, None),
        ('l', 'label', None, ['sys']),
        ('an', 'annotate', None, ['sys']),
        ('run', 'run --rm --restart=Never --image-pull-policy=IfNotPresent -i -t', None, None),
        ('conf', 'config', None, None),
        ('config', 'config view', None, None),
        ('confgc', 'config get-clusters', None, None),
        ('confdc', 'config delete-cluster', None, None),
        ('confsc', 'config set-cluster', None, None),
        ('confgctx', 'config get-contexts', None, None),
        ('confuctx', 'config use-contexts', None, None),
        ('confcctx', 'config current-context', None, None),
        ('confdctx', 'config delete-context', None, None),
        ('confsctx', 'config set-context', None, None),
        ('cp', 'cp', None, None),
    ]

    res = [
        ('po', 'pods', ['e', 'g', 'd', 'rm'], None),
        ('dep', 'deployment', ['s', 'rr', 'rs', 'e', 'g', 'd', 'rm'], None),
        ('ds', 'daemonset', ['rr', 'rs', 'e', 'g', 'd', 'rm'], None),
        ('svc', 'service', ['e', 'g', 'd', 'rm'], None),
        ('ing', 'ingress', ['e', 'g', 'd', 'rm'], None),
        ('cm', 'configmap', ['e', 'g', 'd', 'rm'], None),
        ('sec', 'secret', ['e', 'g', 'd', 'rm'], None),
        ('sc', 'sc', ['e', 'g', 'd', 'rm'], None),
        ('pv', 'pv', ['g', 'd', 'rm'], None),
        ('pvc', 'pvc', ['g', 'd', 'rm'], None),
        ('nad', 'net-attach-def', ['g', 'd', 'rm'], None),
        ('no', 'nodes', ['g', 'd'], ['sys']),
        ('rs', 'replicaset', ['g', 'd'], ['sys']),
        ('ns', 'namespaces', ['g', 'd', 'rm'], ['sys']),
        ('ac', 'admissionconfiguration', ['e', 'g', 'd', 'rm'], ['sys']),
        ('sa', 'serviceaccount', ['e', 'g', 'd', 'rm'], ['sys']),
        ('ro', 'role', ['e', 'g', 'd', 'rm'], ['sys']),
        ('rob', 'rolebinding', ['e', 'g', 'd', 'rm'], ['sys']),
        ('cro', 'clusterrole', ['e', 'g', 'd', 'rm'], ['sys']),
        ('crob', 'clusterrolebinding', ['e', 'g', 'd', 'rm'], ['sys']),
        ('jo', 'jobs', ['e', 'g', 'd', 'rm'], ['sys']),
        ('np', 'networkpolicy', ['e', 'g', 'd', 'rm'], None),
        ('gw', 'gateway', ['e', 'g', 'd', 'rm'], None),
        ('gwc', 'gatewayclass', ['e', 'g', 'd', 'rm'], None),
        ('http', 'httproute', ['e', 'g', 'd', 'rm'], None),
        ('grpc', 'grpcroute', ['e', 'g', 'd', 'rm'], None),
        ('vpa', 'verticalpodautoscaler', ['e', 'g', 'd', 'rm'], None),
        ('hpa', 'horizontalpodautoscaler', ['e', 'g', 'd', 'rm'], None),
    ]
    res_types = [r[0] for r in res]

    args = [
        ('oyaml', '-o=yaml', ['g'], ['owide', 'ojson', 'sl']),
        ('owide', '-o=wide', ['g'], ['oyaml', 'ojson']),
        ('ojson', '-o=json', ['g'], ['owide', 'oyaml', 'sl']),
        ('all', '--all-namespaces', ['g', 'd'], ['rm', 'f', 'no', 'ns', 'sys']),
        ('sl', '--show-labels', ['g'], ['oyaml', 'ojson'], None),
        ('all', '--all', ['rm'], None), # caution: reusing the alias
        ('w', '--watch', ['g'], ['oyaml', 'ojson', 'owide']),
    ]

    # these accept a value, so they need to be at the end and
    # mutually exclusive within each other.
    positional_args = [('f', '--recursive -f', ['g', 'd', 'rm'], res_types + ['all'
                       , 'l', 'sys']), ('l', '-l', ['g', 'd', 'rm'], ['f',
                       'all']), ('n', '--namespace', ['s', 'rr', 'rs', 'e', 'g', 'd', 'rm',
                       'lo', 'ex', 'pf'], ['ns', 'no', 'sys', 'all'])]

    # [(part, optional, take_exactly_one)]
    parts = [
        (cmds, False, True),
        (globs, True, False),
        (ops, True, True),
        (res, True, True),
        (args, True, False),
        (positional_args, True, True),
        ]
        

    shellFormatting = {
        "bash": "alias {}='{}'",
        "zsh": "alias {}='{}'",
        "fish": "abbr --add {} \"{}\"",
    }

    shell = sys.argv[1] if len(sys.argv) > 1 else "bash"
    if shell not in shellFormatting:
        raise ValueError("Shell \"{}\" not supported. Options are {}"
                        .format(shell, [key for key in shellFormatting]))

    out = gen(parts)

    # prepare output
    if not sys.stdout.isatty():
        header_path = \
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'license_header')
        with open(header_path, 'r') as f:
            print(f.read())

    seen_aliases = set()

    # Pre Aliases
    print('IS_KUBECOLOR=$(command -v kubecolor >/dev/null 2>&1 && echo 1 || echo 0)')
    print('kubebin() { [ "$IS_KUBECOLOR" -eq 1 ] && kubecolor "$@" || kubectl "$@"; }')

    print('\n')

    for cmd in out:
        alias = ''.join([a[0] for a in cmd])
        command = ' '.join([a[1] for a in cmd])

        if alias in seen_aliases:
            print("Alias conflict detected: {}".format(alias), file=sys.stderr)

        seen_aliases.add(alias)

        print(shellFormatting[shell].format(alias, command))

    print('\n')

    print(shellFormatting[shell].format('kswag', 'kubectl get --raw /openapi/v2  > /tmp/$KUBECONFIG-openapi-v2.json && docker run -v /tmp/$KUBECONFIG-openapi-v2.json:/app/swagger.json -p 8081:8080 swaggerapi/swagger-ui'))

    print('\n')

    # Post Aliases
    if shell == 'fish':
        print('kubectl completion fish | source')
    else:
        print(f'source <(kubectl completion {shell})')

    if shell == 'zsh':
        print('compdef k=kubectl')
        print('compdef kubecolor=kubectl')
        print('compdef kubebin=kubectl')

def gen(parts):
    out = [()]
    for (items, optional, take_exactly_one) in parts:
        orig = list(out)
        combos = []

        if optional and take_exactly_one:
            combos = combos.append([])

        if take_exactly_one:
            combos = combinations(items, 1, include_0=optional)
        else:
            combos = combinations(items, len(items), include_0=optional)

        # permutate the combinations if optional (args are not positional)
        if optional:
            new_combos = []
            for c in combos:
                new_combos += list(itertools.permutations(c))
            combos = new_combos

        new_out = []
        for segment in combos:
            for stuff in orig:
                if is_valid(stuff + segment):
                    new_out.append(stuff + segment)
        out = new_out
    return out


def is_valid(cmd):
    return is_valid_requirements(cmd) and is_valid_incompatibilities(cmd)


def is_valid_requirements(cmd):
    parts = {c[0] for c in cmd}

    for i in range(0, len(cmd)):
        # check at least one of requirements are in the cmd
        requirements = cmd[i][2]
        if requirements and len(parts & set(requirements)) == 0:
            return False

    return True


def is_valid_incompatibilities(cmd):
    parts = {c[0] for c in cmd}

    for i in range(0, len(cmd)):
        # check none of the incompatibilities are in the cmd
        incompatibilities = cmd[i][3]
        if incompatibilities and len(parts & set(incompatibilities)) > 0:
            return False

    return True


def combinations(a, n, include_0=True):
    _combinations = []
    for j in range(0, n + 1):
        if not include_0 and j == 0:
            continue

        cs = itertools.combinations(a, j)

        # check incompatibilities early
        cs = (c for c in cs if is_valid_incompatibilities(c))

        _combinations += list(cs)

    return _combinations


def diff(a, b):
    return list(set(a) - set(b))


if __name__ == '__main__':
    main()
