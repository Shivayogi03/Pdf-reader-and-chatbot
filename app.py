import streamlit as st
from PyPDF2 import PdfReader
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "PDF Reader and Chatbot"])

if page == "Home":
    st.title("Home Page")
    st.write("Welcome to the PDF Reader and Chatbot application. Use the sidebar to navigate to the PDF Reader and Chatbot page.")
else:
    # Streamlit app
    st.title("PDF Reader and Chatbot")

    # Check if the API key is set
    if not google_api_key:
        st.error("Google API key is missing. Please set it in the .env file.")
        st.stop()

    # File uploader
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        pdf_texts = []
        for uploaded_file in uploaded_files:
            # Read the PDF file
            pdf_reader = PdfReader(uploaded_file)
            pdf_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
            pdf_texts.append(pdf_text)

        combined_pdf_text = "\n".join(pdf_texts)

        if not combined_pdf_text.strip():
            st.error("Could not extract text from the PDFs. Please try other files.")
            st.stop()

        # Display the combined PDF content
        st.text_area("Combined PDF Content", combined_pdf_text, height=300)

        try:
            # Initialize Gemini Pro chatbot
            llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

            # Define prompt template
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="You are an AI assistant. Answer the following question based on the provided context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
            )

            # Create LLMChain
            qa_chain = LLMChain(llm=llm, prompt=prompt)

            # User input for questions
            question = st.text_input("Ask a question about the PDF content:")

            if question:
                # Get the answer from the chatbot
                answer = qa_chain.run({"context": combined_pdf_text, "question": question})
                st.write("Answer:", answer)
        except Exception as e:
            st.error(f"An error occurred: {e}")