#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: deployment
short_description: Manage repos
version_added: "1.0.0"
description:
  - Create, update, and delete deployment resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the deployment resource.
    type: str
    choices: ['present', 'absent']
    default: present

  ref:
    description:
      - >-
        The ref to deploy. This can be a branch, tag, or SHA.
    type: str

    required: true

  auto_merge:
    description:
      - >-
        Attempts to automatically merge the default branch into the requested ref, if it's behind the...
    type: bool

    default: true

  description:
    description:
      - >-
        Short description of the deployment.
    type: str

    default: ""

  environment:
    description:
      - >-
        Name for the target deployment environment (e.g., production, staging, qa).
    type: str

    default: "production"

  payload:
    description:
      - >-

    type: dict

  production_environment:
    description:
      - >-
        Specifies if the given environment is one that end-users directly interact with. Default: true...
    type: bool

  required_contexts:
    description:
      - >-
        The status contexts to verify against commit status checks. If you omit this parameter, GitHub...
    type: list

  task:
    description:
      - >-
        Specifies a task to execute (e.g., deploy or deploy:migrations).
    type: str

    default: "deploy"

  transient_environment:
    description:
      - >-
        Specifies if the given environment is specific to the deployment and will no longer exist at...
    type: bool

    default: false

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Create a deployment
  stevefulme1.github.deployment:

    ref: "example_ref"

    state: present
  # API: POST /repos/{owner}/{repo}/deployments

- name: Update a deployment
  stevefulme1.github.deployment:
    id: "existing_id"

    auto_merge: "updated_auto_merge"

    description: "updated_description"

    environment: "updated_environment"

    payload: "updated_payload"

    production_environment: "updated_production_environment"

    required_contexts: "updated_required_contexts"

    task: "updated_task"

    transient_environment: "updated_transient_environment"

    state: present
  # API:

- name: Delete a deployment
  stevefulme1.github.deployment:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/deployments/{deployment_id}
"""

RETURN = r"""
url:
  description: >-

  returned: success
  type: str

id:
  description: >-
    Unique identifier of the deployment
  returned: success
  type: int

node_id:
  description: >-

  returned: success
  type: str

sha:
  description: >-

  returned: success
  type: str

ref:
  description: >-
    The ref to deploy. This can be a branch, tag, or sha.
  returned: success
  type: str

task:
  description: >-
    Parameter to specify a task to execute
  returned: success
  type: str

payload:
  description: >-

  returned: success
  type: dict

original_environment:
  description: >-

  returned: success
  type: str

environment:
  description: >-
    Name for the target deployment environment.
  returned: success
  type: str

description:
  description: >-

  returned: success
  type: str

creator:
  description: >-
    A GitHub user.
  returned: success
  type: dict

created_at:
  description: >-

  returned: success
  type: str

updated_at:
  description: >-

  returned: success
  type: str

statuses_url:
  description: >-

  returned: success
  type: str

repository_url:
  description: >-

  returned: success
  type: str

transient_environment:
  description: >-
    Specifies if the given environment is will no longer exist at some point in the future. Default: false.
  returned: success
  type: bool

production_environment:
  description: >-
    Specifies if the given environment is one that end-users directly interact with. Default: false.
  returned: success
  type: bool

performed_via_github_app:
  description: >-
    GitHub apps are a new way to extend GitHub. They can be installed directly on organizations and...
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
    """Retrieve the current state of the deployment via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    search_key = "id"
    search_value = identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/deployments")
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

    if module.params.get("ref") is not None:
        payload["ref"] = module.params["ref"]

    if module.params.get("auto_merge") is not None:
        payload["auto_merge"] = module.params["auto_merge"]

    if module.params.get("description") is not None:
        payload["description"] = module.params["description"]

    if module.params.get("environment") is not None:
        payload["environment"] = module.params["environment"]

    if module.params.get("payload") is not None:
        payload["payload"] = module.params["payload"]

    if module.params.get("production_environment") is not None:
        payload["production_environment"] = module.params["production_environment"]

    if module.params.get("required_contexts") is not None:
        payload["required_contexts"] = module.params["required_contexts"]

    if module.params.get("task") is not None:
        payload["task"] = module.params["task"]

    if module.params.get("transient_environment") is not None:
        payload["transient_environment"] = module.params["transient_environment"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            ref=dict(
                type="str",

                required=True,

            ),

            auto_merge=dict(
                type="bool",

                default=True,

            ),

            description=dict(
                type="str",

                default="",

            ),

            environment=dict(
                type="str",

                default="production",

            ),

            payload=dict(
                type="dict",

            ),

            production_environment=dict(
                type="bool",

            ),

            required_contexts=dict(
                type="list",

            ),

            task=dict(
                type="str",

                default="deploy",

            ),

            transient_environment=dict(
                type="bool",

                default=False,

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

                    response = client.POST(
                        "/repos/{owner}/{repo}/deployments",
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

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

                result["url"] = current.get("url")

                result["id"] = current.get("id")

                result["node_id"] = current.get("node_id")

                result["sha"] = current.get("sha")

                result["ref"] = current.get("ref")

                result["task"] = current.get("task")

                result["payload"] = current.get("payload")

                result["original_environment"] = current.get("original_environment")

                result["environment"] = current.get("environment")

                result["description"] = current.get("description")

                result["creator"] = current.get("creator")

                result["created_at"] = current.get("created_at")

                result["updated_at"] = current.get("updated_at")

                result["statuses_url"] = current.get("statuses_url")

                result["repository_url"] = current.get("repository_url")

                result["transient_environment"] = current.get("transient_environment")

                result["production_environment"] = current.get("production_environment")

                result["performed_via_github_app"] = current.get("performed_via_github_app")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/deployments/{deployment_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
