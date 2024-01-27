This module/folder holds all the classes that support the app. 
Currently this is where all the database and webforms are defiined. When you instantiate
these classes you get an object that .that you can then manipulate with your code.

Forms:
Forms are created by creating an object like this.:

    form = ProfileForm()

This is done in a route and it creates a form object. That form object contains the fields
of that form as well as the lables and the data if there is any. It also contains any choices
that may have been defined for that form in a dropdown or other field type. The forms also have 
several methods like form.validate_on_submit() which is true/false and can be used to see 
if the form was submitted and contains data. The form object also contains any errors that 
may have occurred in the submitting of the form. Checkout 'profileform.html' to see how forms
are renderred in html.  In that form there are two different ways to show errors. Check out 
forum.py to see how forms are created and handled for all the CRUD (Create, Read, Update, Delete)
operations.

Check out WTForms for more information on field types: https://wtforms.readthedocs.io
For Flask specific information: https://flask-wtf.readthedocs.io

Data:
We are using MongoDB to store and manipulate data. We are using the MongoEngine library to connect
Flask to MongoDB. In data.py you can define a data collection which is a set of related fields. 
An example of a collection is a User collection where the fields are things like firstName, lastName,
email, etc.  There are four things you will need to do with data: Create, Read, Update, Delete. 
Take a look at the forum.py file to see all of these.  

Additionally, you will want to relate data collections.  For example, a Blog has an author who
is a User and a Blog has Comments.  One of the filed types is ReferenceField() which is used for
this putpose. Here is the author example from the Blog Collection in the data.py file:
    author = ReferenceField('User') 
This means that when you you get a blog in an object you ALSO have the Author and all of that
Author's User fields. For example:
    blogs = Blog.objects() <-- this gets ALL of the Blogs, you can also query for a smaller group
    blogs = Blog.objects(author = current_user) <-- this will get alll blogs authored by the User
                                                    who called the route
Both of these methods will get multiple blogs.  Even if only one blog matches a query, the 
object will contain a list of one object. If you want to get exactly one response you can use 
something like this:
    user = User.objects.get(email = 'stephen.wright@ousd.org')

Learn More: http://mongoengine.org/