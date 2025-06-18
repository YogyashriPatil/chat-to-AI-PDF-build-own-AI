from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import mysql.connector
from django.contrib import messages
from decouple import config
from google.genai import Client
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required(login_url='signin')
def chattoai(request):
    api_key=config('CHAT_TO_AI')
    # print(api_key)
    client = Client(api_key=api_key)
    system_prompt = """
        Your an AI assistant whose work on the simple message of user.
        and you give the user friendly message.
        And the also 
    """
    if request.method == "POST":
        user_input = request.POST.get("message", "")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                system_prompt,
                user_input
            ],
        )
        # Return a dictionary with a key and the AI response text as value
        return JsonResponse({"response": response.text})
    return render(request, "chattoai.html")

    # return render(request, 'chattoai.html')

@login_required(login_url='signin')
def builtownai(request):

    api_key=config('BUILT_OWN_AI')
    client=Client(api_key=api_key)
    system_prompt="Your an AI assistant that work on the following detail. You always talk with the emojis and the behave like professional teacher"+str(request.POST.get('first_message'))

    if request.method == "POST":
        user_input = request.POST.get("message", "")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[
                system_prompt,
                user_input
            ],
        )
        response = {"response": f"{response.text}"}
        return JsonResponse(response)
    return render(request, "builtownai.html")

@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        useremail = request.POST['signin-email']
        passw = request.POST['signin-password']

        print("Email:", useremail, "Password:", passw)
    
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="wtl_project",
        )

        mycur=mydb.cursor()
        mycur.execute("select * from usermast where uemail='"+useremail+"' and upass='"+passw+"' ;")

        mydata=mycur.fetchone()
        print(mydata)
        if mydata is not None:
            return render(request, 'home.html',{"email":useremail})
            # return render(request, 'home.html')
        else:
            return render(request, 'signin.html', {'error': 'Invalid credentials'})
    
    return render(request, 'signin.html')

def signup(request):
    # try :
    #     s1=request.POST.get("signup-name")
    #     s2=request.POST.get("signup-email")
    #     s3=request.POST.get("signup-password")
    #     s4=request.POST.get("signup-repassword")


    #     name=str(s1)
    #     email=str(s2)
    #     password=str(s3)
    #     mydb=mysql.connector.connect(
    #         host="localhost",
    #         user="root",
    #         password="",
    #         database="wtl_project",
    #     )

    #     mycur=mydb.cursor()
    #     mycur.execute("INSERT INTO usermast(uname, uemail, upass) VALUES ('"+name+"','"+email+"','"+password+"');")
    #     mydb.commit()
    #     return render(request, 'home.html')
    
    # except mysql.connector.Error as err:
    #    return HttpResponse("hellllll"+err)
    if request.method == "POST":
        name = request.POST.get("signup-name")
        email = request.POST.get("signup-email")
        password = request.POST.get("signup-password")
        repassword = request.POST.get("signup-repassword")

        if password != repassword:
            return HttpResponse("<h1>Passwords do not match.</h1>")

        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="wtl_project",
            )
            mycur = mydb.cursor()

            # ✅ Secure way to insert data (prevents SQL injection)
            mycur.execute(
                "INSERT INTO usermast(uname, uemail, upass) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            mydb.commit()
            mycur.close()
            mydb.close()
            messages.success(request, "Sign-up successsful. Please sign in.")
            return redirect('signin')  # Redirect to signin after success
        except mysql.connector.Error as err:
            return HttpResponse(f"<h1>Database Error: {err}</h1>")

    return render(request, 'signup.html')

@login_required(login_url='signin')
def aboutus(request):
    return render(request, 'aboutus.html')

@login_required(login_url='signin')
def custom_logout(request):
    logout(request)
    return redirect('signin')
