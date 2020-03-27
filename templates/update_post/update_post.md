{% for item in items %}

# {{ item.project.name }}
**Category**: [{{item.category_name}}]({{item.category_url}})
**Team**: {{ item.hive_team_members }}
**Description**:
> {{ item.project.description }}

![]({{ item.project_image_url }})
{% endfor %}
