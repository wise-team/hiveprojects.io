{% for item in items %}

# {{ item.project.name }}

> {{ item.project.description }}

**Category**: [{{item.category_name}}]({{item.category_url}})

**Team**: {{ item.hive_team_members }}

![]({{ item.project_image_url }})
{% endfor %}
