Templates are the html files that render the pages the user sees.  Templates are 
called by routes. Templates use a templating language called Jinja. You can send variables to 
templates.  Those variables can be accessed with {{ variable }}.  You can also use conditionals
and for loops. for example

{% if currUser.role == 'student' %}
 <some html>
{% endif %}

or 

{% for user in users %}
 {{user.fname}} {{user.lname}}
{% endfor %}