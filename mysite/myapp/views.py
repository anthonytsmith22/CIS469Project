from asyncio.windows_events import NULL
import email
from django.shortcuts import render
import os
from django.conf import settings
from django.core.files import File
from myapp.models import Account
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

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
            return render(request, 'profile_creation.html')
        # If they cancel spending profile creation, return to main page
        elif 'cancel_create_profile' in request.GET:
            return render(request, 'main_page.html')
        # If user requests to logout, return to login
        elif 'logout' in request.GET:
            return render(request, 'index.html')
        # direct to login by default
        else:
            return render(request, 'index.html')

    # If method type is of type POST
    elif request.method == 'POST':
        # If request is a LOGIN POST request, get entered credentials
        if 'login' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')

            # validate credentials
            # placeholder check until DB setup
            # if username == 'admin' and password == 'admin':
            #     return render(request, 'main_page.html')
            # else:
            #     return render(request, 'index.html')
            
            # DB User credential check here
            
            # Query Account table for account with entered credentials
            temp_user = User(username=email)
            temp_user.set_password(password)
            query_account = User.objects.all().filter(email=email, password=temp_user.password)
            print(query_account.exists())
            # Check if it found a match
            if query_account.exists():
                # hash entered password to compare with DB
                # hashed_password = make_password(password=password, salt=None, hasher='PBKDF2SHA1PasswordHasher')
                
                return render(request, 'main_page.html')
            else:
                account_not_found_warning = "Credentials did not match any existing user!"
                return render(request, 'index.html', context={
                    "account_not_found" : account_not_found_warning
                })    
            

        
        elif 'create_new_account' in request.POST:
            # Get new credentials
            new_first_name = request.POST.get('first_name')
            new_last_name = request.POST.get('last_name')
            new_email = request.POST.get('email')
            unhashed_password = request.POST.get('password')
            # print(f'First Name: {new_first_name}\nLast Name: {new_last_name}\nEmail: {new_email}\nPassword: {unhashed_password}')
            
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
            for password in content:
                password = password[:len(password)-2]
                if unhashed_password == password:
                    warning_string = "Too Common A Password!"
                    return render(request, "create_account.html", context={"common_password_warning" : warning_string})
            
            # If we passed the loop, the password is not common and can be used
            
            # Hash the password
            # hashed_password = make_password(password=unhashed_password, salt=None, hasher='unsalted_md5')
            
            # # Create user Account and save it to DB
            # new_account = Account(first_name=new_first_name, last_name=new_last_name, email=new_email, password=hashed_password)
            # new_account.save()

            new_user = User(username=new_email)
            new_user.set_password(unhashed_password)
            new_user.first_name = new_first_name
            new_user.last_name = new_last_name
            new_user.save()

            # Return to login
            return render(request, 'index.html')
        # Redirect to login by default
        else:
            return render(request, 'index.html')
    # Redirect to login by default
    else:
        return render(request, 'index.html')

    
    
