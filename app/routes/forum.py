# These routes are an example of how to use data, forms and routes to create
# a forum where a blogs and comments on those blogs can be
# Created, Read, Updated or Deleted (CRUD)

from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Blog, Comment
from app.classes.forms import BlogForm, CommentForm
from flask_login import login_required
import datetime as dt

# This is the route to list all blogs
@app.route('/blog/list')
@app.route('/blogs')
# This means the user must be logged in to see this page
@login_required
def blogList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    blogs = Blog.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('blogs.html',blogs=blogs)

# This route will get one specific blog and any comments associated with that blog.  
# The blogID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that blog from the database. This route 
# is called when the user clicks a link on bloglist.html template.
# The angle brackets (<>) indicate a variable. 
@app.route('/blog/<blogID>')
# This route will only run if the user is logged in.
@login_required
def blog(blogID):
    # retrieve the blog using the blogID
    thisBlog = Blog.objects.get(id=blogID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    theseComments = Comment.objects(blog=thisBlog)
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('blog.html',blog=thisBlog,comments=theseComments)

# This route will delete a specific blog.  You can only delete the blog if you are the author.
# <blogID> is a variable sent to this route by the user who clicked on the trash can in the 
# template 'blog.html'. 
# TODO add the ability for an administrator to delete blogs. 
@app.route('/blog/delete/<blogID>')
# Only run this route if the user is logged in.
@login_required
def blogDelete(blogID):
    # retrieve the blog to be deleted using the blogID
    deleteBlog = Blog.objects.get(id=blogID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteBlog.author:
        # delete the blog using the delete() method from Mongoengine
        deleteBlog.delete()
        # send a message to the user that the blog was deleted.
        flash('The Blog was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a blog you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    blogs = Blog.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('blogs.html',blogs=blogs)

# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new blog based on what the user put in the form.
# Because this route includes a form that both gets and blogs data it needs the 'methods'
# in the route decorator.
@app.route('/blog/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def blogNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = BlogForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newBlog = Blog(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            subject = form.subject.data,
            content = form.content.data,
            tag = form.tag.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newBlog.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('blog',blogID=newBlog.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('blogform.html',form=form)


# This route enables a user to edit a blog.  This functions very similar to creating a new 
# blog except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original blog. Read and understand the new blog route 
# before this one. 
@app.route('/blog/edit/<blogID>', methods=['GET', 'POST'])
@login_required
def blogEdit(blogID):
    editBlog = Blog.objects.get(id=blogID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editBlog.author:
        flash("You can't edit a blog you don't own.")
        return redirect(url_for('blog',blogID=blogID))
    # get the form object
    form = BlogForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editBlog.update(
            subject = form.subject.data,
            content = form.content.data,
            tag = form.tag.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('blog',blogID=blogID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.subject.data = editBlog.subject
    form.content.data = editBlog.content
    form.tag.data = editBlog.tag


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('blogform.html',form=form)

#####
# the routes below are the CRUD for the comments that are related to the blogs. This
# process is exactly the same as for blogs with one addition. Each comment is related to
# a specific blog via a field on the comment called 'blog'. The 'blog' field contains a 
# reference to the Blog document. See the @app.route('/blog/<blogID>') above for more details
# about how comments are related to blogs.  Additionally, take a look at data.py to see how the
# relationship is defined in the Blog and the Comment collections.

@app.route('/comment/new/<blogID>', methods=['GET', 'POST'])
@login_required
def commentNew(blogID):
    blog = Blog.objects.get(id=blogID)
    form = CommentForm()
    if form.validate_on_submit():
        newComment = Comment(
            author = current_user.id,
            blog = blogID,
            content = form.content.data
        )
        newComment.save()
        return redirect(url_for('blog',blogID=blogID))
    return render_template('commentform.html',form=form,blog=blog)

@app.route('/comment/edit/<commentID>', methods=['GET', 'POST'])
@login_required
def commentEdit(commentID):
    editComment = Comment.objects.get(id=commentID)
    if current_user != editComment.author:
        flash("You can't edit a comment you didn't write.")
        return redirect(url_for('blog',blogID=editComment.blog.id))
    blog = Blog.objects.get(id=editComment.blog.id)
    form = CommentForm()
    if form.validate_on_submit():
        editComment.update(
            content = form.content.data,
            modifydate = dt.datetime.utcnow
        )
        return redirect(url_for('blog',blogID=editComment.blog.id))

    form.content.data = editComment.content

    return render_template('commentform.html',form=form,blog=blog)   

@app.route('/comment/delete/<commentID>')
@login_required
def commentDelete(commentID): 
    deleteComment = Comment.objects.get(id=commentID)
    deleteComment.delete()
    flash('The comments was deleted.')
    return redirect(url_for('blog',blogID=deleteComment.blog.id)) 
