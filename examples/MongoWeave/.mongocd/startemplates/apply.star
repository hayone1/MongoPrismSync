toMatch = ctx.resource_list["functionConfig"]["params"]["toMatch"]
  toAdd = ctx.resource_list["functionConfig"]["params"]["toAdd"]
  for resource in ctx.resource_list["items"]:
    match = True
    for key in toMatch:
      if key not in resource["metadata"]["annotations"] or resource["metadata"]["annotations"][key] != toMatch[key]:
        match = False
        break
    if match:
      for key in toAdd:
        resource["metadata"]["annotations"][key] = toAdd[key]