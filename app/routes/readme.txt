Routes are how Flask translates a url into specific functionality. Routes use decorators
which point a url to a set of python code. for example:
@app.route('.login')
is a route that waits for someone to type https://website.com/login and then runs the 
code associated with that route. 