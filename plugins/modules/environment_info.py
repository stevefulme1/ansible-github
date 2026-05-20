#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: environment_info
short_description: Retrieve information about environment resources
version_added: "1.0.0"
description:
  - Retrieve a single environment by its identifier, or list all environment resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  id:
    description:
      - The unique identifier of the environment to retrieve.
      - When omitted, all environment resources are listed.
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
- name: Get a specific environment
  stevefulme1.github.environment_info:
    id: "example_id"
  register: result

- name: List all environment resources
  stevefulme1.github.environment_info:
  register: result


- name: List environment resources filtered by name
  stevefulme1.github.environment_info:
    name: "my_environment"
  register: result


- name: List environment resources with pagination
  stevefulme1.github.environment_info:
    page: 1
    page_size: 50
  register: result
"""

RETURN = r"""
environments:
  description: List of environment resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    id:
      description: >-
        The id of the environment.
      type: int


    node_id:
      description: >-
        
      type: str


    name:
      description: >-
        The name of the environment.
      type: str


    url:
      description: >-
        
      type: str


    html_url:
      description: >-
        
      type: str


    created_at:
      description: >-
        The time that the environment was created, in ISO 8601 format.
      type: str


    updated_at:
      description: >-
        The time that the environment was last updated, in ISO 8601 format.
      type: str


    protection_rules:
      description: >-
        Built-in deployment protection rules for the environment.
      type: list


    deployment_branch_policy:
      description: >-
        The type of deployment branch policy for this environment. To allow all branches to deploy, set to null.
      type: dict


"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single environment by identifier."""

    # No single-resource GET endpoint; filter from list
    items = client.get("/repos/{owner}/{repo}/environments")
    if isinstance(items, dict):
        items = items.get("results", items.get("data", items.get("items", [])))
    for item in items:
        if str(item.get("id")) == str(identifier):
            return item
    return None



def fetch_list(client, module):
    """List environment resources with optional filtering and pagination."""

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
        response = client.get("/repos/{owner}/{repo}/environments", params=params)
        if isinstance(response, dict):
            return response.get("results", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/repos/{owner}/{repo}/environments", params=params)



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
        environments=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["environments"] = [item] if item else []
        else:
            result["environments"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
