{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:

   {% block attributes %}
   {% set own_attributes = documented_attributes(attributes, fullname, inherited_members) %}
   {% if own_attributes %}
   .. rubric:: Attributes

   {% for item in own_attributes %}
   .. attribute:: {{ item }}
      :no-index:

      {{ attribute_summary(item, fullname) }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block methods %}
   {% set own_methods = methods | reject("in", inherited_members) | reject("equalto", "__init__") | list %}
   {% if own_methods %}
   .. rubric:: Methods

   .. autosummary::
   {% for item in own_methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}

   {% for item in own_methods %}
   .. automethod:: {{ item }}

   {% endfor %}
   {% endif %}
   {% endblock %}
