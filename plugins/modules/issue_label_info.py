#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: issue_label_info
short_description: Retrieve information about issue_label resources
version_added: "1.0.0"
description:
  - Retrieve a single issue_label by its identifier, or list all issue_label resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  id:
    description:
      - The unique identifier of the issue_label to retrieve.
      - When omitted, all issue_label resources are listed.
    type: str
    required: false

  name:
    description:
      - Filter results by name.
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
- name: Get a specific issue_label
  stevefulme1.github.issue_label_info:
    id: "example_id"
  register: result

- name: List all issue_label resources
  stevefulme1.github.issue_label_info:
  register: result

- name: List issue_label resources filtered by name
  stevefulme1.github.issue_label_info:
    name: "my_issue_label"
  register: result

- name: List issue_label resources with pagination
  stevefulme1.github.issue_label_info:
    page: 1
    page_size: 50
  register: result
"""

RETURN = r"""
issue_labels:
  description: List of issue_label resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    id:
      description: >-
        Unique identifier for the label.
      type: int

    node_id:
      description: >-

      type: str

    url:
      description: >-
        URL for the label
      type: str

    name:
      description: >-
        The name of the label.
      type: str

    description:
      description: >-
        Optional description of the label, such as its purpose.
      type: str

    color:
      description: >-
        6-character hex code, without the leading , identifying the color
      type: str

    default:
      description: >-
        Whether this label comes by default in a new repository.
      type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single issue_label by identifier."""

    # No single-resource GET endpoint; filter from list
    items = client.get("/repos/{owner}/{repo}/issues/{issue_number}/labels")
    if isinstance(items, dict):
        items = items.get("results", items.get("data", items.get("items", [])))
    for item in items:
        if str(item.get("id")) == str(identifier):
            return item
    return None


def fetch_list(client, module):
    """List issue_label resources with optional filtering and pagination."""

    params = {}

    name_filter = module.params.get("name")
    if name_filter is not None:
        params["name"] = name_filter

    page = module.params.get("page")
    page_size = module.params.get("page_size")

    if page is not None or page_size is not None:
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        response = client.get("/repos/{owner}/{repo}/issues/{issue_number}/labels", params=params)
        if isinstance(response, dict):
            return response.get("results", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/repos/{owner}/{repo}/issues/{issue_number}/labels", params=params)


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            id=dict(type="str", required=False),

            name=dict(type="str", required=False),

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
        issue_labels=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["issue_labels"] = [item] if item else []
        else:
            result["issue_labels"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
