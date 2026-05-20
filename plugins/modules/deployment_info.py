#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: deployment_info
short_description: Retrieve information about deployment resources
version_added: "1.0.0"
description:
  - Retrieve a single deployment by its identifier, or list all deployment resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  id:
    description:
      - The unique identifier of the deployment to retrieve.
      - When omitted, all deployment resources are listed.
    type: str
    required: false

  page:
    description:
      - Page number for paginated results.
      - Only applies when listing resources.
    type: int
    required: false
  page_size:
    description:
      - Number of results per page.
      - Only applies when listing resources.
    type: int
    required: false
extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Get a specific deployment
  stevefulme1.github.deployment_info:
    id: "example_id"
  register: result

- name: List all deployment resources
  stevefulme1.github.deployment_info:
  register: result

- name: List deployment resources with pagination
  stevefulme1.github.deployment_info:
    page: 1
    page_size: 50
  register: result
"""

RETURN = r"""
deployments:
  description: List of deployment resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    url:
      description: >-

      type: str

    id:
      description: >-
        Unique identifier of the deployment
      type: int

    node_id:
      description: >-

      type: str

    sha:
      description: >-

      type: str

    ref:
      description: >-
        The ref to deploy. This can be a branch, tag, or sha.
      type: str

    task:
      description: >-
        Parameter to specify a task to execute
      type: str

    payload:
      description: >-

      type: dict

    original_environment:
      description: >-

      type: str

    environment:
      description: >-
        Name for the target deployment environment.
      type: str

    description:
      description: >-

      type: str

    creator:
      description: >-
        A GitHub user.
      type: dict

    created_at:
      description: >-

      type: str

    updated_at:
      description: >-

      type: str

    statuses_url:
      description: >-

      type: str

    repository_url:
      description: >-

      type: str

    transient_environment:
      description: >-
        Specifies if the given environment is will no longer exist at some point in the future. Default: false.
      type: bool

    production_environment:
      description: >-
        Specifies if the given environment is one that end-users directly interact with. Default: false.
      type: bool

    performed_via_github_app:
      description: >-
        GitHub apps are a new way to extend GitHub. They can be installed directly on organizations and...
      type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single deployment by identifier."""

    # No single-resource GET endpoint; filter from list
    items = client.get("/repos/{owner}/{repo}/deployments")
    if isinstance(items, dict):
        items = items.get("results", items.get("data", items.get("items", [])))
    for item in items:
        if str(item.get("id")) == str(identifier):
            return item
    return None


def fetch_list(client, module):
    """List deployment resources with optional filtering and pagination."""

    params = {}

    page = module.params.get("page")
    page_size = module.params.get("page_size")

    if page is not None or page_size is not None:
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        response = client.get("/repos/{owner}/{repo}/deployments", params=params)
        if isinstance(response, dict):
            return response.get("results", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/repos/{owner}/{repo}/deployments", params=params)


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            id=dict(type="str", required=False),

            page=dict(type="int", required=False),
            page_size=dict(type="int", required=False),
        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("id", "page"),
            ("id", "page_size"),
        ],
    )

    result = dict(
        changed=False,
        deployments=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["deployments"] = [item] if item else []
        else:
            result["deployments"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
