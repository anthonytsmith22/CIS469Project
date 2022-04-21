from asyncio.windows_events import NULL
import email
from logging import warning
from multiprocessing.sharedctypes import Value
import profile
from pydoc import cli
from telnetlib import LOGOUT
from venv import create
from wsgiref.util import request_uri
from django.shortcuts import render
import os
from django.conf import settings
from django.core.files import File
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from myapp.models import SpendingProfile, Entry
from datetime import datetime
import uuid

client_user = NULL
selected_profile = NULL

def index(request):

    # Check the method type for GET or POST
    
    # If method type is of type GET
    if request.method == 'GET':
        # direct user to account creation page if they send create account GET
        if 'create_account' in request.GET:               
            return render(request, 'create_account.html')
        # if they request return to login, redirect them back to login
        elif 'return_to_login' in request.GET:
            return render(request, 'index.html')
        # If they request to create a new spending profile
        elif 'create_new_profile' in request.GET:
            return render(request, "profile_creation.html")
            #direct_to_profile_creation_page(request)
        # If they cancel spending profile creation, return to main page
        elif 'cancel_create_profile' in request.GET:
            user_associated_profiles = load_profiles(request.user.username)
            profile_names = []
            for profile in user_associated_profiles:
                profile_names.append(profile["ProfileName"])
            print(profile_names)
            return render(request, "main_page.html", context={
                "profiles" : profile_names
            })
        # direct to login by default
        else:
            return render(request, 'index.html')

    # If method type is of type POST
    elif request.method == 'POST':
        # If request is a LOGIN POST request, get entered credentials
        if 'login' in request.POST:
            email = request.POST.get('email')
            raw_password = request.POST.get('password')

            # validate user credentials
            
            # DB User credential check here
            
            # # Query Account table for account with entered credentials
            # query_account = User.objects.filter(username=email)
            
            # # Check if User exits, if so, get the User model
            # if query_account.exists(): 
            #     query_account = query_account.get()
            #     # Check if password matches
            #     if query_account.check_password(raw_password):
            #         if query_account.
            #         return render(request, 'main_page.html')
            #     else:
            #         # Password did not match, return generic error message
            #         account_not_found_warning = "Credentials did not match any existing user!"
            #         return render(request, 'index.html', context={
            #             "account_not_found" : account_not_found_warning
            #         })  
            # # Model did not exist, return generic error message
            # else:
            #     account_not_found_warning = "Credentials did not match any existing user!"
            #     return render(request, 'index.html', context={
            #         "account_not_found" : account_not_found_warning
            #     })    

            client_user = authenticate(request, username=email, password=raw_password)# or authenticate(email=email, password=raw_password)
            if client_user is not None:
                request.session.set_expiry(86400)
                login(request, client_user)
                user_associated_profiles = load_profiles(request.user.username)
                profile_names = []
                for profile in user_associated_profiles:
                    profile_names.append(profile["ProfileName"])
                print(profile_names)
                return render(request, "main_page.html", context={
                    "profiles" : profile_names
                })
            else:
                return render(request, "index.html")
        
        elif 'create_new_account' in request.POST:
            # Get new credentials
            new_first_name = request.POST.get('first_name')
            new_last_name = request.POST.get('last_name')
            new_username = request.POST.get('username')
            new_email = request.POST.get('email')
            unhashed_password = request.POST.get('password')
            confirm_unhashed = request.POST.get('password_match')
            # print(f'First Name: {new_first_name}\nLast Name: {new_last_name}\nEmail: {new_email}\nPassword: {unhashed_password}')

            # Check if passwords match
            if unhashed_password != confirm_unhashed:
                print("no match")
                # Don't match, send error
                warning_string = "Passwords Don't Match!"
                return render(request, 'create_account.html', context={
                    "account_creation_warning" : warning_string,
                    "populate_first_name" : new_first_name,
                    "populate_last_name" : new_last_name,
                    "populate_username" : new_username,
                    "populate_email" : new_email
                })

            # Check if username is over 30 characters
            # Needs to be 30 or less for models
            if new_username.__len__() > 30:
                warning_string = "Username must be under 30 characters!"
                return render(request, "create_account.html", context={
                    "account_creation_warning" : warning_string,
                    "populate_first_name" : new_first_name,
                    "populate_last_name" : new_last_name,
                    "populate_username" : "",
                    "populate_email" : new_email
                })
            
            # Check is username is taken
            if User.objects.filter(username=new_username).exists():
                warning_string = "Username already exists!"
                return render(request, "create_account.html", context={
                    "account_creation_warning" : warning_string,
                    "populate_first_name" : new_first_name,
                    "populate_last_name" : new_last_name,
                    "populate_username" : "",
                    "populate_email" : new_email
                })

            # Check if password is a common password
            
            # Read txt file with 10,000 common passwords, src: https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10k-most-common.txt
            common_passwords_file = open(os.path.join(settings.BASE_DIR, 'common_passwords.txt'), 'r')
            my_file = File(common_passwords_file)
            
            content = my_file.readlines()

            # Close file
            common_passwords_file.close()
            my_file.close()

            # Iterate through common passwords until there is a match
            # If there is a match, redirect to create_account.html with a common password warning
            # Else, user did not enter a common password, proceed to creating user account
            for raw_password in content:
                raw_password = raw_password[:len(raw_password)-2]
                if unhashed_password == raw_password:
                    warning_string = "<p >Too Common A Password!"
                    return render(request, "create_account.html", context={
                        "account_creation_warning" : warning_string,
                        "populate_first_name" : new_first_name,
                        "populate_last_name" : new_last_name,
                        "populate_username" : new_username,
                        "populate_email" : new_email
                    })
            
            # If we passed the loop, the password is not common and can be used
            
            # Hash the password
            # hashed_password = make_password(password=unhashed_password, salt=None, hasher='unsalted_md5')
            
            # # Create user Account and save it to DB
            # new_account = Account(first_name=new_first_name, last_name=new_last_name, email=new_email, password=hashed_password)
            # new_account.save()

            new_user = User.objects.create_user(new_username, new_email, unhashed_password)
            # new_user.set_password(unhashed_password)
            new_user.first_name = new_first_name
            new_user.last_name = new_last_name
            new_user.save()

            # Return to login
            return render(request, 'index.html')
        # If user requests to logout, return to login
        elif 'logout' in request.POST:
            logout(request)
            return render(request, 'index.html')
        # If user adds a username to profile creation
        elif 'add_contributor' in request.POST:
            get_username = request.POST["contributor"].strip()
            # Check if user entered a value
            if get_username.__len__() == 0:
                warning_string = "Contributor username must not be left blank!"
                return render(request, "profile_creation.html", context={
                    "profile_creation_warning" : warning_string
                })
            # Do check to find user
            get_user = User.objects.filter(username=get_username)
            if not get_user.exists():
                warning_string = f'No user found by name {get_username}!'
                return render(request, "profile_creation.html", context={
                    "profile_creation_warning" : warning_string
                })
            # Found valid user
            # contributors_string = ""
            # for contributor in SPENDING_PROFILE_USERNAMES:
            #     contributors_string += str(contributor)
            #     contributors_string += "\n"
            # print(contributors_string)
            return render(request, "profile_creation.html", context={
                "populate_contributors" : get_username
            })
        # If user requests to create a new profile
        elif 'create_profile' in request.POST:

            profile_name = request.POST.get("profile_name")
            contributors = request.POST.get("contributors")
            description = request.POST.get("description")

            # process textarea results into list of names
            contributors_processed = contributors.replace("\n", " ").replace("\r", " ").strip().split(" ")
            for i in contributors_processed:  
                # also check if they added themselves as a contributor
                if i == request.user.username:
                    contributors_processed.remove(i)
            
            for i in contributors_processed:
                if i.__len__() < 5:
                    contributors_processed.remove(i)

            print(contributors_processed)
            # Check if contributors exists
            for i in contributors_processed:
                if not User.objects.filter(username=i).exists():
                    warning_string = f'{i} does not match any registered users!'
                    return render(request, "profile_creation.html", context={
                        "profile_creation_warning" : warning_string,
                        "populate_profile_name" : profile_name,
                    })

            # Check if profile name is within 30 character constraint
            if profile_name.__len__() > 30:
                warning_string = "Profile name must be 30 characters or less!"
                return render(request, "profile_creation.html", context={
                    "profile_creation_warning" : warning_string,
                    "populate_profile_name" : profile_name,
                })

            # Check if description is within limit
            if description.__len__() > 100:
                warning_string = "Description must be 100 characters or less!"
                return render(request, "profile_creation.html", context={
                    "profile_creation_warning" : warning_string,
                    "populate_profile_name" : profile_name,
                })
            
            # If all checks pass, create profile
            profile_data = {"ProfileName" : profile_name, "ProfileOwner" : request.user.username, 
            "Description" : description, "Contributors" : {"contributor0" : request.user.username}, "Entries" : {} }
            contributor_index = 1
            for i in contributors_processed:
                profile_data["Contributors"]["contributor" + str(contributor_index)] = i
                contributor_index += 1
            
            print(profile_data)

            new_spending_profile = SpendingProfile(profile_name=profile_name, profile_owner=request.user.username, data=profile_data)
            new_spending_profile.save()

            if SpendingProfile.objects.filter(profile_name=profile_name).exists():
                print(True)
            else:
                print(False)

            return render(request, "main_page.html")
        # If user selecs spending profile
        elif "select_profile" in request.POST:
            selected_profile_name = request.POST["select_profile_option"]
            print(f'{selected_profile_name} test get')
            if selected_profile_name == "default":
                return render(request, "main_page.html", context={
                    "main_page_warning" : "No Profile Selected!"
                })
            selected_profile = SpendingProfile.objects.filter(profile_name=selected_profile_name).get()
            profile_data = selected_profile.data
            user_associated_profiles = load_profiles(request.user.username)
            profile_names = []
            for profile in user_associated_profiles:
                profile_names.append(profile["ProfileName"])
            data, spending_total, contributor_data = get_profile_data(selected_profile)
            return render(request, "main_page.html", context={
                "profile_data" : data,
                "total_amount" : spending_total,
                "selected_profile_name": selected_profile_name,
                "profiles" : profile_names,
                "contributor_data" : contributor_data
            })
        # If user is creating a spending entry
        elif "create_entry" in request.POST:
            entry_name = request.POST["entry_name"]
            entry_amount = request.POST["entry_amount"]
            profile_name = request.POST["profile_name"]

            spending_profile = SpendingProfile.objects.filter(profile_name=profile_name)

            if spending_profile.exists():
                spending_profile = spending_profile.get()
            else:
                return render(request, "main_page.html", context={
                    "main_page_warning" : f'Spending Profile Not Found!'
                })

            try:
                entry_amount = int(entry_amount)
            except ValueError:
                user_associated_profiles = load_profiles(request.user.username)
                profile_names = []
                for profile in user_associated_profiles:
                    profile_names.append(profile["ProfileName"])
                data, spending_total, contributor_data = get_profile_data(spending_profile)
                return render(request, "main_page.html", context={
                    "main_page_warning" : "Amount must be a number!",
                    "profile_data" : data,
                    "total_amount" : spending_total,
                    "selected_profile_name": profile_name,
                    "profiles" : profile_names,
                    "contributor_data" : contributor_data
                })
            
            if entry_amount <= 0:
                user_associated_profiles = load_profiles(request.user.username)
                profile_names = []
                for profile in user_associated_profiles:
                    profile_names.append(profile["ProfileName"])
                data, spending_total = get_profile_data(spending_profile)
                return render(request, "main_page.html", context={
                    "main_page_warning" : "Amount must be a positive number!",
                    "profile_data" : data,
                    "total_amount" : spending_total,
                    "selected_profile_name": profile_name,
                    "profiles" : profile_names
                })

            if request.POST["contributor_name"] == "default":
                entry_owner = request.user.username
            else:
                entry_owner = request.POST["contributor_name"]
            entry_date = datetime.today().strftime('%Y-%m-%d')

            new_id = str(uuid.uuid4())

            entry_data = {"Name" : entry_name, "Amount" : entry_amount, "Contributor" : entry_owner, "Date" : entry_date}
            
            # spending_profile_data = spending_profile.data
            # spending_profile_data["Entries"][new_id] = entry_data

            spending_profile.data["Entries"][new_id] = entry_data
            print(spending_profile.data)
            spending_profile.save()
            # spending_profile.save()
            
            user_associated_profiles = load_profiles(request.user.username)
            profile_names = []
            for profile in user_associated_profiles:
                profile_names.append(profile["ProfileName"])
            print(profile_names)
            return render(request, "main_page.html", context={
                "profiles" : profile_names
            })

        # Redirect to login by default
        else:
            return render(request, 'index.html')
    # Redirect to login by default
    else:
        return render(request, 'index.html')


def direct_to_main_page(request):
    if request.user.is_authenticated:
        return render(request, "main_page.html")   
    return render(request, "index.html") 


def direct_to_profile_creation_page(request):
    if request.user.is_authenticated:
        return render(request, "profile_creation.html")   
    return render(request, "index.html") 
    
def get_spending_profiles():
    profiles = SpendingProfile.objects.all()
    print(profiles)

def load_profiles(username):
    all_profiles = SpendingProfile.objects.all()
    user_associated_profiles = []
    for i in all_profiles:
        profile_data = i.data
        profile_contributors = profile_data["Contributors"]
        index = 0
        for x in range(profile_contributors.__len__()):
            key = f'contributor{index}'
            if username == profile_contributors[key]: 
                user_associated_profiles.append(profile_data)
                break
            index += 1
    return user_associated_profiles

def get_profile_data(profile):
    entries = profile.data["Entries"]
    spending_total = 0

    data = []
    
    profile_contributors = profile.data["Contributors"]
    names = []
    index = 0
    contributor_data = {}
    for x in range(profile_contributors.__len__()):
        key = f'contributor{index}'
        names.append(profile_contributors[key])
        contributor_data[names[index]] = 0
        index += 1
    
    
    for entry in entries:
        print(f'{entry} test entry data')
        name = entries[entry]["Name"]
        amount = entries[entry]["Amount"]
        date = entries[entry]["Date"]
        contributor = entries[entry]["Contributor"]
        
        spending_total += int(amount)

        entry_data = []

        entry_data.append(name)
        entry_data.append(amount)
        entry_data.append(date)
        entry_data.append(contributor)

        data.append(entry_data)
        contributor_data[name] += int(amount)
    print(f'{data} test data')
    
    return data, spending_total, contributor_data
