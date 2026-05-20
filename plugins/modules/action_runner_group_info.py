#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: action_runner_group_info
short_description: Retrieve information about action_runner-group resources
version_added: "1.0.0"
description:
  - Retrieve a single action_runner-group by its identifier, or list all action_runner-group resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  id:
    description:
      - The unique identifier of the action_runner-group to retrieve.
      - When omitted, all action_runner-group resources are listed.
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
- name: Get a specific action_runner-group
  stevefulme1.github.action_runner_group_info:
    id: "example_id"
  register: result

- name: List all action_runner-group resources
  stevefulme1.github.action_runner_group_info:
  register: result


- name: List action_runner-group resources filtered by name
  stevefulme1.github.action_runner_group_info:
    name: "my_action_runner-group"
  register: result


- name: List action_runner-group resources with pagination
  stevefulme1.github.action_runner_group_info:
    page: 1
    page_size: 50
  register: result
"""

RETURN = r"""
action_runner_groups:
  description: List of action_runner-group resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    id:
      description: >-
        
      type: float


    name:
      description: >-
        
      type: str


    visibility:
      description: >-
        
      type: str


    default:
      description: >-
        
      type: bool


    selected_repositories_url:
      description: >-
        Link to the selected repositories resource for this runner group. Not present unless visibility...
      type: str


    runners_url:
      description: >-
        
      type: str


    hosted_runners_url:
      description: >-
        
      type: str


    network_configuration_id:
      description: >-
        The identifier of a hosted compute network configuration.
      type: str


    inherited:
      description: >-
        
      type: bool


    inherited_allows_public_repositories:
      description: >-
        
      type: bool


    allows_public_repositories:
      description: >-
        
      type: bool


    workflow_restrictions_read_only:
      description: >-
        If true, the restricted_to_workflows and selected_workflows fields cannot be modified.
      type: bool


    restricted_to_workflows:
      description: >-
        If true, the runner group will be restricted to running only the workflows specified in the...
      type: bool


    selected_workflows:
      description: >-
        List of workflows the runner group should be allowed to run. This setting will be ignored unless...
      type: list


"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single action_runner-group by identifier."""

    # No single-resource GET endpoint; filter from list
    items = client.get("/orgs/{org}/actions/runner-groups")
    if isinstance(items, dict):
        items = items.get("results", items.get("data", items.get("items", [])))
    for item in items:
        if str(item.get("id")) == str(identifier):
            return item
    return None



def fetch_list(client, module):
    """List action_runner-group resources with optional filtering and pagination."""

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
        response = client.get("/orgs/{org}/actions/runner-groups", params=params)
        if isinstance(response, dict):
            return response.get("results", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/orgs/{org}/actions/runner-groups", params=params)



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
        action_runner_groups=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["action_runner_groups"] = [item] if item else []
        else:
            result["action_runner_groups"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
