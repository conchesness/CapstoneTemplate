from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Sleep, User
from app.classes.forms import SleepForm, ConsentForm
from flask_login import login_required
import datetime as dt
import matplotlib.pyplot as plt
#import numpy as np

@app.route('/consent', methods=['GET', 'POST'])
def consent():
    form = ConsentForm()
    if form.validate_on_submit():
        if form.consent.data == "True":
            consent = True
        else:
            consent = False
        current_user.update(
            consent = consent,
            adult_fname = form.adult_fname.data,
            adult_lname = form.adult_lname.data,
            adult_email = form.adult_email.data
        )
        return redirect(url_for('myProfile'))

    form.consent.process_data(current_user.consent)
    form.adult_fname.data = current_user.adult_fname
    form.adult_lname.data = current_user.adult_lname
    form.adult_email.data = current_user.adult_email
    return render_template("consentform.html", form=form)


@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/sleep/new', methods=['GET', 'POST'])
@login_required
def sleepNew():
    form = SleepForm()
    if form.validate_on_submit():
        startDT = dt.datetime.combine(form.sleep_date.data, form.starttime.data)
        endDT = dt.datetime.combine(form.wake_date.data, form.endtime.data)
        diff = startDT - endDT
        hours = diff.seconds/60/60
        newSleep = Sleep(
            hours = hours,
            sleeper = current_user,
            rating = form.rating.data,
            start = startDT,
            end = endDT,
            feel = form.feel.data,
            minstosleep = form.minstosleep.data,
        )
        newSleep.save()
        return redirect(url_for("sleep",sleepId=newSleep.id))
    
    if form.submit.data:
        if form.rating.data == 'None':
            form.rating.errors = ['Required']
        if form.feel.data == 'None':
            form.feel.errors = ['Required']
        
    return render_template("sleepform.html",form=form)

@app.route('/sleep/edit/<sleepId>', methods=['GET', 'POST'])
@login_required

def sleepEdit(sleepId):
    form = SleepForm()
    editSleep = Sleep.objects.get(id=sleepId)

    if editSleep.sleeper != current_user:
        flash("You can't edit a sleep you don't own.")
        return redirect(url_for('sleeps'))
    
    if form.validate_on_submit():
        startDT = dt.datetime.combine(form.sleep_date.data, form.starttime.data)
        endDT = dt.datetime.combine(form.wake_date.data, form.endtime.data)
        diff = endDT - startDT
        hours = diff.seconds/60/60

        editSleep.update(
            hours = hours,
            rating = form.rating.data,
            start = startDT,
            end = endDT,
            feel = form.feel.data,
            minstosleep = form.minstosleep.data
        )
        return redirect(url_for("sleep",sleepId=editSleep.id))
    
    form.sleep_date.process_data(editSleep.start.date())
    form.starttime.process_data(editSleep.start.time())
    form.wake_date.process_data(editSleep.end.date())
    form.endtime.process_data(editSleep.end.time())
    form.rating.process_data(editSleep.rating)
    form.feel.process_data(editSleep.feel)
    form.minstosleep.data = editSleep.minstosleep
    return render_template("sleepform.html",form=form)

@app.route('/sleep/<sleepId>')
@login_required

def sleep(sleepId):
    thisSleep = Sleep.objects.get(id=sleepId)
    return render_template("sleep.html",sleep=thisSleep)

@app.route('/sleeps')
@login_required

def sleeps():
    sleeps = Sleep.objects()
    return render_template("sleeps.html",sleeps=sleeps)

@app.route('/sleep/delete/<sleepId>')
@login_required

def sleepDelete(sleepId):
    delSleep = Sleep.objects.get(id=sleepId)
    sleepDate = delSleep.sleep_date
    delSleep.delete()
    flash(f"sleep with date {sleepDate} has been deleted.")
    return redirect(url_for('sleeps'))

@app.route('/sleepgraph')
@login_required

def sleepgraph():
    sleeps = Sleep.objects()


    hours = []
    dates = []
    colors = []
    for sleep in sleeps:
        hours.append(sleep.hours)
        dates.append(sleep.start.date())   
        if sleep.rating >=4:
            colors.append('green')
        elif sleep.rating == 3:
            colors.append('yellow')
        else:
            colors.append('red')
    
    fig, ax = plt.subplots()

    ax.scatter(dates, hours, marker='o', c=colors)


    #ax.legend()
    plt.yticks(hours)
    plt.xticks(dates, rotation=45)
    #plt.gcf().set_size_inches(10, 5)
    fig.savefig("app/static/graphs/sleep.png", bbox_inches="tight")
    #fig.show()
    return render_template('sleepgraph.html',images=['sleep.png'])