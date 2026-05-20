#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: environment
short_description: Manage repos
version_added: "1.0.0"
description:
  - Create, update, and delete environment resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the environment resource.
    type: str
    choices: ['present', 'absent']
    default: present

  deployment_branch_policy:
    description:
      - >-
        The type of deployment branch policy for this environment. To allow all branches to deploy, set to null.
    type: dict

  prevent_self_review:
    description:
      - >-
        Whether or not a user who created the job is prevented from approving their own job.
    type: bool

  reviewers:
    description:
      - >-
        The people or teams that may review jobs that reference the environment. You can list up to six...
    type: list
    elements: str

  wait_timer:
    description:
      - >-
        The amount of time to delay a job after the job is initially triggered. The time (in minutes)...
    type: int

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Update a environment
  stevefulme1.github.environment:
    id: "existing_id"

    deployment_branch_policy: "updated_deployment_branch_policy"

    prevent_self_review: "updated_prevent_self_review"

    reviewers: "updated_reviewers"

    wait_timer: "updated_wait_timer"

    state: present
  # API:

- name: Delete a environment
  stevefulme1.github.environment:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/environments/{environment_name}
"""

RETURN = r"""
id:
  description: >-
    The id of the environment.
  returned: success
  type: int

node_id:
  description: >-

  returned: success
  type: str

name:
  description: >-
    The name of the environment.
  returned: success
  type: str

url:
  description: >-

  returned: success
  type: str

html_url:
  description: >-

  returned: success
  type: str

created_at:
  description: >-
    The time that the environment was created, in ISO 8601 format.
  returned: success
  type: str

updated_at:
  description: >-
    The time that the environment was last updated, in ISO 8601 format.
  returned: success
  type: str

protection_rules:
  description: >-
    Built-in deployment protection rules for the environment.
  returned: success
  type: list

deployment_branch_policy:
  description: >-
    The type of deployment branch policy for this environment. To allow all branches to deploy, set to null.
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the environment via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/environments")
        if isinstance(items, dict):
            items = items.get("results", items.get("data", items.get("items", [])))
        for item in items:
            if str(item.get(search_key)) == str(search_value):
                return item
            if str(item.get("id")) == str(search_value):
                return item
        return None
    except ClientError:
        return None


def needs_update(current, desired):
    """Compare current state against desired params and return True if an update is needed."""
    if current is None:
        return True
    for key, value in desired.items():
        if value is None:
            continue
        current_value = current.get(key)
        if current_value != value:
            return True
    return False


def build_payload(module):
    """Build the API request payload from module params."""
    payload = {}

    if module.params.get("deployment_branch_policy") is not None:
        payload["deployment_branch_policy"] = module.params["deployment_branch_policy"]

    if module.params.get("prevent_self_review") is not None:
        payload["prevent_self_review"] = module.params["prevent_self_review"]

    if module.params.get("reviewers") is not None:
        payload["reviewers"] = module.params["reviewers"]

    if module.params.get("wait_timer") is not None:
        payload["wait_timer"] = module.params["wait_timer"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            deployment_branch_policy=dict(
                type="dict",

            ),

            prevent_self_review=dict(
                type="bool",

            ),

            reviewers=dict(
                type="list",
                elements="str",

            ),

            wait_timer=dict(
                type="int",

            ),

        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,

    )

    state = module.params["state"]
    result = dict(changed=False, diff=dict(before={}, after={}))

    try:
        client = Client(module)
        current = get_current_state(client, module)

        if state == "present":
            desired = build_payload(module)

            if current is None:
                # Resource does not exist — create it
                result["changed"] = True
                result["diff"]["before"] = {}
                result["diff"]["after"] = desired

                if not module.check_mode:

                    pass

            elif needs_update(current, desired):
                # Resource exists but needs updating
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = dict(current, **{k: v for k, v in desired.items() if v is not None})

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "".replace(
                        "{id}", str(identifier)
                    )
                    response = client.put(
                        path,
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            else:
                # Resource exists and is up-to-date

                result["id"] = current.get("id")

                result["node_id"] = current.get("node_id")

                result["name"] = current.get("name")

                result["url"] = current.get("url")

                result["html_url"] = current.get("html_url")

                result["created_at"] = current.get("created_at")

                result["updated_at"] = current.get("updated_at")

                result["protection_rules"] = current.get("protection_rules")

                result["deployment_branch_policy"] = current.get("deployment_branch_policy")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/environments/{environment_name}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
