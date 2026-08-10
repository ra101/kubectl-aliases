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


import os
import itertools


SSH_OPTS = (
    '--local-ssh-opts="-o UserKnownHostsFile=/dev/null" '
    '--local-ssh-opts="-o StrictHostKeyChecking=no" '
    '--local-ssh-opts="-o LogLevel=ERROR" '
)


def generate_aliases(shell):
    output = ''

    # (alias, full, allow_when_oneof, incompatible_with)
    cmds = [('k', 'kubebin', None, None)]

    _globals = [('sys', '--namespace=kube-system', None, None)]

    # (alias, full, require_oneof, incompatible_with)
    operations = [
        ('a', 'apply --recursive -f', None, None),
        ('ak', 'apply -k', None, ['sys']),
        ('k', 'kustomize', None, ['sys']),
        ('kb', 'kustomize build', None, ['sys']),
        ('v', 'virt', None, ['sys']),
        ('ex', 'exec -i -t', None, None),
        ('vex', f'virt ssh {SSH_OPTS}', None, ['sys']),
        ('nex', 'node-shell', None, None),
        ('lo', 'logs -f', None, None),
        ('lop', 'logs -f -p', None, None),
        ('e', 'edit', None, None),
        ('rr', 'rollout restart', None, None),
        ('vst', 'virt start', None, ['sys']),
        ('vr', 'virt reset', None, ['sys']),
        ('vrr', 'virt restart', None, ['sys']),
        ('vsr', 'virt soft-reboot', None, ['sys']),
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
        ('vp', 'virt pause', None, ['sys']),
        ('vup', 'virt unpause', None, ['sys']),
        ('vsp', 'virt stop', None, ['sys']),
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
        ('kvcp', 'virt scp', None, ['sys']),
    ]

    # (alias, full, require_oneof, incompatible_with)
    resources = [
        ('po', 'pods', ['g', 'e', 'd', 'rm'], None),
        ('vm', 'virtualmachine', ['g', 'e', 'd', 'rm'], None),
        ('vmi', 'virtualmachineinstance', ['g', 'e', 'd', 'rm'], None),
        ('vmim', 'virtualmachineinstancemigration', ['g', 'e', 'd', 'rm'], None),
        ('dep', 'deployment', ['s', 'rr', 'rs', 'g', 'e', 'd', 'rm'], None),
        ('vmp', 'virtualmachinepool', ['g', 'e', 'd', 'rm', 's'], None),
        ('st', 'statefulset', ['s', 'rr', 'rs', 'g', 'e', 'd', 'rm'], None),
        ('ds', 'daemonset', ['rr', 'rs', 'g', 'e', 'd', 'rm'], None),
        ('svc', 'service', ['g', 'e', 'd', 'rm'], None),
        ('ep', 'endpoints', ['g', 'e', 'd', 'rm'], None),
        ('eps', 'endpointslices', ['g', 'e', 'd', 'rm'], None),
        ('ing', 'ingress', ['g', 'e', 'd', 'rm'], None),
        ('cm', 'configmap', ['g', 'e', 'd', 'rm'], None),
        ('sec', 'secret', ['g', 'e', 'd', 'rm'], None),
        ('sc', 'sc', ['g', 'e', 'd', 'rm'], None),
        ('pv', 'pv', ['g', 'e', 'd', 'rm'], None),
        ('pvc', 'pvc', ['g', 'd', 'rm'], None),
        ('nad', 'net-attach-def', ['g', 'e', 'd', 'rm'], None),
        ('no', 'nodes', ['g', 'd'], ['sys']),
        ('rs', 'replicaset', ['g', 'e', 'd', 'rm'], ['sys']),
        ('ns', 'namespaces', ['g', 'd', 'rm'], ['sys']),
        ('ac', 'admissionconfiguration', ['g', 'e', 'd', 'rm'], ['sys']),
        ('sa', 'serviceaccount', ['g', 'e', 'd', 'rm'], ['sys']),
        ('r', 'role', ['g', 'e', 'd', 'rm'], ['sys']),
        ('rb', 'rolebinding', ['g', 'e', 'd', 'rm'], ['sys']),
        ('cr', 'clusterrole', ['g', 'e', 'd', 'rm'], ['sys']),
        ('crb', 'clusterrolebinding', ['g', 'e', 'd', 'rm'], ['sys']),
        ('j', 'jobs', ['g', 'e', 'd', 'rm'], ['sys']),
        ('cj', 'cronjobs', ['g', 'e', 'd', 'rm'], ['sys']),
        ('np', 'networkpolicy', ['g', 'e', 'd', 'rm'], None),
        ('gw', 'gateway', ['g', 'e', 'd', 'rm'], None),
        ('gwc', 'gatewayclass', ['g', 'e', 'd', 'rm'], None),
        ('http', 'httproute', ['g', 'e', 'd', 'rm'], None),
        ('grpc', 'grpcroute', ['g', 'e', 'd', 'rm'], None),
        ('vpa', 'verticalpodautoscaler', ['g', 'e', 'd', 'rm'], None),
        ('hpa', 'horizontalpodautoscaler', ['g', 'e', 'd', 'rm'], None),
        ('ev', 'events', ['g', 'e', 'd', 'rm'], None),
    ]
    res_types = [r[0] for r in resources]

    # (alias, full, require_oneof, incompatible_with)
    args = [
        ('oyaml', '-o=yaml', ['g'], ['owide', 'ojson', 'sl']),
        ('owide', '-o=wide', ['g'], ['oyaml', 'ojson']),
        ('ojson', '-o=json', ['g'], ['owide', 'oyaml', 'sl']),
        ('all', '--all-namespaces', ['g', 'd'], [
            'rm', 'f', 'no', 'ns', 'sys']),
        ('sl', '--show-labels', ['g'], ['oyaml', 'ojson'], None),
        ('all', '--all', ['rm'], None),  # caution: reusing the alias
        ('w', '--watch', ['g'], ['oyaml', 'ojson', 'owide']),
    ]

    # these accept a value, so they need to be at the end and
    # mutually exclusive within each other.
    # 
    positional_args = [
        ('f', '--recursive -f', ['g', 'd', 'rm'], res_types + ['all', 'l', 'sys']),
        ('n', '--namespace', ['s', 'rr', 'rs', 'g', 'e', 'd', 'rm', 'lo', 'ex', 'pf'], ['ns', 'no', 'sys', 'all'])
    ]

    # [(part, optional, take_exactly_one)]
    parts = [
        (cmds, False, True),
        (_globals, True, False),
        (operations, True, True),
        (resources, True, True),
        (args, True, False),
        (positional_args, True, True),
    ]

    shellFormatting = {
        "bash": "alias {}='{}'\n",
        "zsh": "alias {}='{}'\n",
        "fish": "abbr --add {} \"{}\"\n",
    }

    if shell not in shellFormatting:
        raise ValueError(
            "Shell \"{}\" not supported. Options are {}".format(
                shell, [key for key in shellFormatting]))

    out = generate_combinations(parts)

    output += ('\n#!/usr/bin/env {}\n\n'.format(shell))

    # prepare output
    header_path = \
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'license_header')
    with open(header_path, 'r') as f:
        output += (f.read())

    seen_aliases = set()

    # Pre Aliases
    output += (
        '\nif command -v kubecolor >/dev/null 2>&1; then'
        '\n    kubebin() { kubecolor "$@"; }'
        '\nelse'
        '\n    kubebin() { kubectl "$@"; }'
        '\nfi\n'
    )

    output += (
        '\nif command -v virtctl >/dev/null 2>&1; then'
        '\n    virtbin() { virtctl "$@"; }'
        '\nelse'
        '\n    virtbin() { kubectl virt "$@"; }'
        '\nfi\n\n'
    )

    for cmd in out:
        alias = ''.join([a[0] for a in cmd])
        command = ' '.join([a[1] for a in cmd])

        if command.startswith('kubebin get events'):
            command.replace(
                'get events',
                'get events --sort-by=.metadata.creationTimestamp'
            )

        if command.startswith('kubebin virt'):
            command = command.replace('kubebin virt', 'virtbin')

        if alias in seen_aliases:
            raise RuntimeError("Alias conflict detected: {}".format(alias))

        seen_aliases.add(alias)

        output += (shellFormatting[shell].format(alias, command))

    output += ('\n\n')

    output += (shellFormatting[shell].format('kswag', 'kubectl get --raw /openapi/v2  > /tmp/$KUBECONFIG-openapi-v2.json && docker run -v /tmp/$KUBECONFIG-openapi-v2.json:/app/swagger.json -p 8081:8080 swaggerapi/swagger-ui'))

    output += ('\n\n')

    # Post Aliases
    if shell == 'fish':
        output += ('\nkubectl completion fish | source')
    else:
        output += (f'source <(kubectl completion {shell})')

    if shell == 'zsh':
        output += ('\ncompdef k=kubectl')
        output += ('\ncompdef kubecolor=kubectl')
        output += ('\ncompdef kubebin=kubectl')

    return output


def generate_combinations(parts):
    """
    Generates all valid combinations of the given parts,
    where each part is a list of tuples of
    (alias, full, require_oneof, incompatible_with)
    and the boolean flags (optional, take_exactly_one)
    specify how to combine the tuples.
    """
    out = [()]
    for items, optional, take_exactly_one in parts:
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
    for shell in ['bash', 'zsh', 'fish']:
        with open(f'.kubectl_aliases.{shell}', 'w') as f:
            f.write(generate_aliases(shell))
