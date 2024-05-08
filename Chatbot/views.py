from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch,Pinecone,Weaviate,FAISS
import os
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from .forms import HotelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
import PyPDF2
from django.http import FileResponse
from .models import *



def home(request):
    if request.method=="POST":
        u_pdf=request.FILES['user']
        # print(u_name)
        # response = requests.get(u_name)
        # soup = BeautifulSoup(response.content, 'html.parser')

        # # Find all the text content within the <body> tag and its descendants
        # text_content = []

        # for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        #     if not element.find('a'):
        #         text = element.get_text(strip=True)
        #         text_content.append(text)

        # # Print or process the extracted text content
        # text_content=set(text_content)
        # #print(text_content)

        # raw_text=''
        # count=0
        # for text in text_content:
        #     raw_text+=text

        # os.environ["OPENAI_API_KEY"]="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"
        # text_splitter=CharacterTextSplitter(
        #     separator=".",
        #     chunk_size=10000,
        #     chunk_overlap=200,
        #     length_function=len
        # )
        # texts=text_splitter.split_text(raw_text)
        # print(texts[0])
        # embeddings=OpenAIEmbeddings()
        # docsearch = FAISS.from_texts(texts,embeddings)
        # chain=load_qa_chain(OpenAI(),chain_type="stuff")
        # query="what was the topic discuused in the data?"
        # docs=docsearch.similarity_search(query)
        # print(chain.run(input_documents=docs,question=query))


    

    #return render(request,"index.html")

def chat(request):

    return render(request,"chat.html")

def urltrain(request):
    global raw_text
    raw_text=''
    if request.method == "POST":
        link_address = request.POST["website"]
        print(link_address)
        response = requests.get(link_address)
        soup = BeautifulSoup(response.content, 'html.parser')

# Find all the text content within the <body> tag and its descendants
        text_content = []

        for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if not element.find('a'):
                text = element.get_text(strip=True)
                text_content.append(text)

        text_content=set(text_content)
        for text in text_content:
            raw_text+=text
        return redirect('readweb')
    return render(request,"url.html")


def read_web(request):
    return render(request,"chat.html")

def hotel_image_view(request):
 
    if request.method == 'POST':
        pdf=request.FILES['fileAttachment']
        Hotel.objects.create(name="Rahul",hotel_Main_Img=pdf)
        return redirect('success')
 
    return render(request, 'index.html')
 
 
def success(request):
    global raw_text
    raw_text=''
    filepath = os.path.join('media')
    for filename in os.listdir(filepath):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(filepath, filename)
            raw_text += read_pdf(pdf_path)
    print(raw_text)
    #return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


    return render(request,"chat.html")

def read_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    

def chatresponse(request):

    print("chat called")
    question=request.POST['text']
    os.environ["OPENAI_API_KEY"]="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"
    text_splitter=CharacterTextSplitter(
    separator="\n",
    chunk_size=10000,
    chunk_overlap=200,
    length_function=len
    )

    texts=text_splitter.split_text(raw_text)
    embeddings=OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts,embeddings)
    chain=load_qa_chain(OpenAI(),chain_type="stuff")
    #query="does the author have any work experience?"
    docs=docsearch.similarity_search(question)
    return HttpResponse(chain.run(input_documents=docs,question=question))