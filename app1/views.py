from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import mysql.connector
from django.contrib import messages
from decouple import config
from google.genai import Client
from django.http import JsonResponse
from django.contrib.auth import logout,authenticate,login
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
from django.conf import settings
from shutil import copyfile
import os,json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_mistralai import MistralAIEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
def home(request):
    user_email = request.COOKIES.get('user_email', None)  # Retrieve cookie
    is_logged_in = user_email is not None

    return render(request, 'home.html', {
        'is_logged_in': is_logged_in,
        'user_email': user_email,
    })
    return render(request, 'home.html')

# @login_required(login_url='signin')
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
        return JsonResponse({"response": response.text})
    return render(request, "chattoai.html")

@csrf_exempt
def aboutinfo(request):
    if request.method == 'POST':
        try:
            raw_body=request.body.decode('utf-8')
            print("Raw request body:", raw_body) # Debugging
            data = json.loads(raw_body)
            responses = data.get('responses', '')
            print("Received responses:", responses)
            
            response_dict = {}
            for line in responses.splitlines():
                key, value = line.split(':', 1)  # Split into key and value
                response_dict[key.strip()] = value.strip()

                    # Access individual values
            name = response_dict.get('name')
            age = response_dict.get('age')
            gender = response_dict.get('gender')
            like = response_dict.get('likes')
            nature = response_dict.get('nature')
            # global system_prompt_for_own
            system_prompt_for_own = f"""
                You are an AI Assistant of {name}.
                Your age is {age}. You always talk like your age number.
                Your gender is {gender} version, So talk based on your gender.
                and your hobbies are {like}.
                and your mood is always a {nature} . Always talk in your moode. 
                Use a some time emojis for chatting in a one chat 1 or 2 emojis only.
                And the give the proper answer based on the provided contain.
            """
            request.session['system_prompt_for_own'] = system_prompt_for_own
            # global system_prompt_for_own = system_prompt1
            print("System Prompt:", system_prompt_for_own)
        except json.JSONDecodeError as e:
                print("JSON Decode Error:", e)
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return render(request, 'aboutinfo.html')

# @login_required(login_url='signin')
@csrf_exempt
def builtownai(request):
    system_prompt_for_own=request.session.get('system_prompt_for_own', None)
    # print("this is ",system_prompt_for_own)
    system_prompt=system_prompt_for_own
    if request.method == 'POST':
        api_key=config('BUILT_OWN_AI')
        # print(api_key)
        client = Client(api_key=api_key)
        user_input =request.POST.get("message", "")
        print(user_input)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
               contents=[
                    system_prompt,
                    user_input
                ],
            )
        # print("AI Response:", response.text)
        return JsonResponse({"response": response.text})
    return render(request, "builtownai.html")

# @login_required(login_url='signin')
@csrf_exempt 
def chattopdf(request):
    vector_store = None  # Define vector_store outside the conditions to reuse it later
    if request.method == 'POST':
        if request.session.get('pdf_uploaded', False):
            return JsonResponse({
                'response': 'A PDF has already been uploaded. Please ask questions about the current PDF.(if the another pdf uploaded please refresh) '
            }, status=200)
        # Handle File Upload
        file = request.FILES.get('file')  # Check for uploaded file
        if file:
            uploaded_file = request.FILES['file']  # 'file' is the name attribute of the input in your form
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            file_name = uploaded_file.name
            print(file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            request.session['pdf_uploaded'] = True

            media_path = Path(settings.MEDIA_ROOT)
            pdf_path= media_path / file_name;
            print(pdf_path)

            # Load and process PDF
            loader=PyPDFLoader(file_path=pdf_path)
            docs=loader.load()
            # print(docs[0])

            text_spiltter=RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
            split_docs=text_spiltter.split_documents(documents=docs)
            
            api_key =config("MISTRAL_API_KEY") 
            model = "mistral-embed"
            embedder = MistralAIEmbeddings(
                model=model,
                api_key=api_key
            )
            
            vector_Store=QdrantVectorStore.from_documents(
                collection_name="talk_to_pdf",
                url="http://localhost:6333",
                embedding=embedder,
                documents=[]
            )

            vector_Store.add_documents(split_docs)
            print("Injection done")

            return JsonResponse({'response':f"Successfully proceed file : {file_name}"})
            # return render(request, 'upload.html', {'success': "Upload a PDF and ask questions!"})

        message=request.POST.get('message')
        if message:
            # print(message)
            
            # if not vector_Store:
            #     return render(request, 'upload.html', {'error': "Please upload a PDF first."})
                
            # search_result=vector_Store.similarity_search(query=message)
            
            # print(f"User query: {message}")
            
            # api_key=config('CHAT_TO_AI')
            # client = Client(api_key=api_key)
            # system_prompt = f"""
            #         Your an AI assistant whose work on the find the answer based on the relevant chunk.
            #         You give the user friendly message.
            #         And the also the answer give to the {search_result}
            #     """
            # response = client.models.generate_content(
            #     model="gemini-1.5-flash",
            #         contents=[
            #             system_prompt,
            #             message
            #         ],
            #     )
            # print(f"AI response: {response.text}")
            # return JsonResponse({"response": response.text})
            response_text = f"AI response to your query: {message}"
            return JsonResponse({'response': response_text}, status=200)

        return JsonResponse({'error': 'No file or message provided.'}, status=400)
           
    return render(request, 'upload.html', {'success': "Upload a PDF and ask questions!"})

@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        useremail = request.POST.get('signin-email')
        passw = request.POST.get('signin-password')

        print("Email:", useremail, "Password:", passw)
        try:
            # Connect to MySQL database
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="wtl_project",
            )
            mycur=mydb.cursor()
            mycur.execute("select * from usermast where uemail='"+useremail+"' and upass='"+passw+"' ;")
            print(mycur)
            mydata=mycur.fetchone()
            print(mydata)
            
            if mydata is not None:
                print("email and password is correct")
                response= redirect('/home/')
                response.set_cookie('user_email',useremail)
                return response
                # return render(request, 'home.html',{"email":useremail})
                # return render(request, 'home.html')
            else:
                return render(request, 'signin.html', {'error': 'Invalid credentials'})
        except mysql.connector.Error as err:
            return render(request, 'signin.html', {'error': f"Database error: {err}"})
        finally:
            if mydb.is_connected():
                mycur.close()
                mydb.close()
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

# @login_required(login_url='signin')
def aboutus(request):
    return render(request, 'aboutus.html')

# @login_required(login_url='signin')
def custom_logout(request):
    response = redirect('/signin/')
    response.delete_cookie('user_email')  # Clear cookie
    return response
    # logout(request)
    # return redirect('signin')
